import json
import re
from datetime import date, datetime, timedelta

import boto3
from flask import current_app

from app import db
from app.log_config import get_logger

logger = get_logger(__name__)

PROMPT_NAME = 'stock_qualitative_analysis'
REPORT_TYPE = 'stock_analysis'
NEWS_DAYS = 30
EARNINGS_CALL_LIMIT = 3


class StockAnalysisService:

    def get_cached_analysis(self, stock_id: str):
        from app.ai_report.models import AiReport
        today = date.today()
        return AiReport.query.filter_by(
            report_type=REPORT_TYPE,
            subject=stock_id,
            period_start=today,
            period_end=today,
        ).one_or_none()

    def get_recent_earnings_call_reports(self, stock_id: str) -> list:
        from app.ai_report.models import AiReport
        return (
            AiReport.query
            .filter_by(
                report_type='earnings_call',
                subject=stock_id,
                processing_status='completed',
            )
            .order_by(AiReport.period_start.desc())
            .limit(EARNINGS_CALL_LIMIT)
            .all()
        )

    def get_recent_news(self, stock_id: str) -> list:
        from app.models.feed import Feed
        date_from = datetime.utcnow() - timedelta(days=NEWS_DAYS)
        return (
            Feed.query
            .filter(
                Feed.stock_id == stock_id,
                Feed.releaseTime >= date_from,
            )
            .order_by(Feed.releaseTime.desc())
            .limit(50)
            .all()
        )

    def get_prompt(self):
        from app.ai_prompt.models import AiPrompt
        return AiPrompt.query.filter_by(name=PROMPT_NAME, is_active=True).first()

    def _get_api_key_value(self, prompt) -> str:
        if not prompt.api_key:
            raise ValueError("Prompt has no API key configured")
        region = current_app.config.get('AWS_REGION', 'ap-northeast-1')
        ssm = boto3.client('ssm', region_name=region)
        response = ssm.get_parameter(Name=prompt.api_key.ssm_path, WithDecryption=True)
        return response['Parameter']['Value']

    def build_prompt_content(
        self,
        stock_id: str,
        company_name: str,
        earnings_reports: list,
        news_feeds: list,
        template: str,
    ) -> str:
        if earnings_reports:
            ec_lines = [
                f"【{r.period_start}】{r.summary or '（無摘要）'}"
                for r in earnings_reports
            ]
            ec_text = '\n'.join(ec_lines)
        else:
            ec_text = '（近期無法說會記錄）'

        if news_feeds:
            news_lines = [
                f"- {f.releaseTime.strftime('%Y-%m-%d')} {f.title}"
                for f in news_feeds
            ]
            news_text = '\n'.join(news_lines)
        else:
            news_text = '（近期無相關新聞）'

        return (
            template
            .replace('{{stock_id}}', stock_id)
            .replace('{{company_name}}', company_name)
            .replace('{{earnings_call_summaries}}', ec_text)
            .replace('{{news_titles}}', news_text)
        )

    def call_ai(self, prompt_content: str, api_key: str, provider: str, model: str) -> dict:
        """Dispatch to the appropriate AI provider."""
        if provider == 'gemini':
            return self._call_gemini(prompt_content, api_key, model)
        return self._call_claude(prompt_content, api_key, model)

    def _call_claude(self, prompt_content: str, api_key: str, model: str) -> dict:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model=model or 'claude-haiku-4-5-20251001',
            max_tokens=1024,
            messages=[{'role': 'user', 'content': prompt_content}],
        )
        raw_text = message.content[0].text
        json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        result = json.loads(json_match.group()) if json_match else {}
        return {
            'result': result,
            'raw': raw_text,
            'input_tokens': message.usage.input_tokens,
            'output_tokens': message.usage.output_tokens,
            'model': message.model,
        }

    def _call_gemini(self, prompt_content: str, api_key: str, model: str) -> dict:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        gemini_model = genai.GenerativeModel(model or 'gemini-1.5-flash')
        response = gemini_model.generate_content(prompt_content)
        raw_text = response.text
        json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        result = json.loads(json_match.group()) if json_match else {}
        usage = response.usage_metadata
        return {
            'result': result,
            'raw': raw_text,
            'input_tokens': usage.prompt_token_count if usage else 0,
            'output_tokens': usage.candidates_token_count if usage else 0,
            'model': model or 'gemini-1.5-flash',
        }

    def analyze(self, stock_id: str):
        from app.ai_report.models import AiReport
        from app.database_setup import BasicInformation

        cached = self.get_cached_analysis(stock_id)
        if cached and cached.processing_status == 'completed':
            return cached

        prompt = self.get_prompt()
        if not prompt:
            raise ValueError(f"No active prompt named '{PROMPT_NAME}'")

        earnings_reports = self.get_recent_earnings_call_reports(stock_id)
        news_feeds = self.get_recent_news(stock_id)

        basic_info = db.session.get(BasicInformation, stock_id)
        company_name = getattr(basic_info, '公司簡稱', None) or stock_id

        prompt_content = self.build_prompt_content(
            stock_id, company_name, earnings_reports, news_feeds, prompt.content
        )

        today = date.today()
        if cached:
            report = cached
            report.processing_status = 'processing'
        else:
            report = AiReport(
                report_type=REPORT_TYPE,
                subject=stock_id,
                period_start=today,
                period_end=today,
                prompt_name=PROMPT_NAME,
                processing_status='processing',
            )
            db.session.add(report)
        db.session.commit()

        try:
            api_key_value = self._get_api_key_value(prompt)
            provider = prompt.api_key.provider if prompt.api_key else 'claude'
            model_name = prompt.api_key.model if prompt.api_key else None
            response = self.call_ai(prompt_content, api_key_value, provider, model_name)

            result = response['result']
            report.processing_status = 'completed'
            report.raw_ai_response = response['raw']
            report.summary = result.get('summary', '')
            report.sentiment = result.get('signal', '觀望')
            report.key_points = {
                'positives': result.get('positives', []),
                'risks': result.get('risks', []),
                'data_freshness': result.get('data_freshness', ''),
            }
            report.input_tokens = response['input_tokens']
            report.output_tokens = response['output_tokens']
            report.total_tokens = response['input_tokens'] + response['output_tokens']
            report.model_name = response['model']
        except Exception as e:
            report.processing_status = 'failed'
            report.error_message = str(e)
            db.session.commit()
            raise

        db.session.commit()
        return report

    def to_dict(self, report) -> dict:
        kp = report.key_points or {}
        return {
            'stock_id': report.subject,
            'signal': report.sentiment,
            'summary': report.summary,
            'positives': kp.get('positives', []),
            'risks': kp.get('risks', []),
            'data_freshness': kp.get('data_freshness', ''),
            'processing_status': report.processing_status,
            'model_name': report.model_name,
            'analyzed_at': report.created_at.isoformat() if report.created_at else None,
        }
