"""Unit tests for StockAnalysisService."""
import pytest
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

from app import db
from app.ai_report.models import AiReport
from app.stock_analysis.services import StockAnalysisService, PROMPT_NAME, REPORT_TYPE

FAKE_CLAUDE_RESPONSE = {
    'result': {
        'signal': '買進',
        'summary': '近期營運正向，法說會展望樂觀。',
        'positives': ['毛利率提升', '訂單能見度高'],
        'risks': ['匯率風險'],
        'data_freshness': '2026-05-15 法說會',
    },
    'raw': '{"signal":"買進","summary":"近期營運正向，法說會展望樂觀。","positives":["毛利率提升","訂單能見度高"],"risks":["匯率風險"],"data_freshness":"2026-05-15 法說會"}',
    'input_tokens': 800,
    'output_tokens': 150,
    'model': 'claude-haiku-4-5-20251001',
}


@pytest.fixture
def service():
    return StockAnalysisService()


class TestGetCachedAnalysis:
    def test_returns_none_when_no_report(self, service, sample_basic_info, app_context):
        result = service.get_cached_analysis(sample_basic_info.id)
        assert result is None

    def test_returns_report_when_exists(self, service, sample_stock_analysis_report, app_context):
        result = service.get_cached_analysis(sample_stock_analysis_report.subject)
        assert result is not None
        assert result.id == sample_stock_analysis_report.id


class TestGetRecentEarningsCallReports:
    def test_returns_empty_when_no_reports(self, service, sample_basic_info, app_context):
        result = service.get_recent_earnings_call_reports(sample_basic_info.id)
        assert result == []

    def test_returns_completed_reports_only(
        self, service, sample_basic_info, sample_earnings_call_ai_report, app_context
    ):
        result = service.get_recent_earnings_call_reports(sample_basic_info.id)
        assert len(result) == 1
        assert result[0].processing_status == 'completed'

    def test_excludes_other_stocks(self, service, sample_earnings_call_ai_report, app_context):
        result = service.get_recent_earnings_call_reports('9999')
        assert result == []


class TestGetRecentNews:
    def test_returns_empty_when_no_news(self, service, sample_basic_info, app_context):
        result = service.get_recent_news(sample_basic_info.id)
        assert result == []

    def test_returns_news_for_stock(self, service, sample_recent_feed, app_context):
        result = service.get_recent_news(sample_recent_feed.stock_id)
        assert any(f.id == sample_recent_feed.id for f in result)


class TestBuildPromptContent:
    def test_replaces_all_placeholders(self, service):
        template = '{{stock_id}} {{company_name}} {{earnings_call_summaries}} {{news_titles}}'
        result = service.build_prompt_content('2330', '台積電', [], [], template)
        assert '{{' not in result
        assert '2330' in result
        assert '台積電' in result

    def test_shows_no_data_message_when_empty(self, service):
        template = '{{earnings_call_summaries}} {{news_titles}}'
        result = service.build_prompt_content('2330', '台積電', [], [], template)
        assert '近期無法說會記錄' in result
        assert '近期無相關新聞' in result

    def test_includes_earnings_call_summary(self, service, sample_earnings_call_ai_report):
        template = '{{earnings_call_summaries}}'
        result = service.build_prompt_content(
            '2330', '台積電', [sample_earnings_call_ai_report], [], template
        )
        assert sample_earnings_call_ai_report.summary in result

    def test_includes_news_titles(self, service, sample_recent_feed):
        template = '{{news_titles}}'
        result = service.build_prompt_content(
            '2330', '台積電', [], [sample_recent_feed], template
        )
        assert sample_recent_feed.title in result


class TestAnalyze:
    def test_returns_cached_when_already_completed(
        self, service, sample_stock_analysis_report, app_context
    ):
        result = service.analyze(sample_stock_analysis_report.subject)
        assert result.id == sample_stock_analysis_report.id
        assert result.processing_status == 'completed'

    def test_raises_when_no_prompt(self, service, sample_basic_info, app_context):
        with pytest.raises(ValueError, match=PROMPT_NAME):
            service.analyze(sample_basic_info.id)

    def test_creates_report_on_success(
        self, service, sample_basic_info, sample_ai_prompt, app_context
    ):
        with (
            patch.object(service, '_get_api_key_value', return_value='test-key'),
            patch.object(service, 'call_ai', return_value=FAKE_CLAUDE_RESPONSE),
        ):
            report = service.analyze(sample_basic_info.id)

        assert report.processing_status == 'completed'
        assert report.subject == sample_basic_info.id
        assert report.report_type == REPORT_TYPE
        assert report.sentiment == '買進'
        assert report.summary == '近期營運正向，法說會展望樂觀。'
        assert report.key_points['positives'] == ['毛利率提升', '訂單能見度高']

        # Cleanup
        db.session.delete(report)
        db.session.commit()

    def test_marks_failed_on_claude_error(
        self, service, sample_basic_info, sample_ai_prompt, app_context
    ):
        with (
            patch.object(service, '_get_api_key_value', return_value='test-key'),
            patch.object(service, 'call_ai', side_effect=Exception('API error')),
            pytest.raises(Exception, match='API error'),
        ):
            service.analyze(sample_basic_info.id)

        failed = AiReport.query.filter_by(
            report_type=REPORT_TYPE,
            subject=sample_basic_info.id,
            period_start=date.today(),
        ).one_or_none()
        assert failed is not None
        assert failed.processing_status == 'failed'

        # Cleanup
        db.session.delete(failed)
        db.session.commit()


class TestCallAi:
    def test_dispatches_to_claude(self, service):
        with (
            patch.object(service, '_call_claude', return_value=FAKE_CLAUDE_RESPONSE) as mock_claude,
            patch.object(service, '_call_gemini') as mock_gemini,
        ):
            result = service.call_ai('prompt', 'key', 'claude', 'claude-haiku-4-5-20251001')
        mock_claude.assert_called_once_with('prompt', 'key', 'claude-haiku-4-5-20251001')
        mock_gemini.assert_not_called()
        assert result == FAKE_CLAUDE_RESPONSE

    def test_dispatches_to_gemini(self, service):
        with (
            patch.object(service, '_call_gemini', return_value=FAKE_CLAUDE_RESPONSE) as mock_gemini,
            patch.object(service, '_call_claude') as mock_claude,
        ):
            result = service.call_ai('prompt', 'key', 'gemini', 'gemini-1.5-flash')
        mock_gemini.assert_called_once_with('prompt', 'key', 'gemini-1.5-flash')
        mock_claude.assert_not_called()
        assert result == FAKE_CLAUDE_RESPONSE

    def test_unknown_provider_falls_back_to_claude(self, service):
        with patch.object(service, '_call_claude', return_value=FAKE_CLAUDE_RESPONSE) as mock_claude:
            result = service.call_ai('prompt', 'key', 'openai', 'gpt-4')
        mock_claude.assert_called_once()
        assert result == FAKE_CLAUDE_RESPONSE


class TestToDict:
    def test_returns_expected_keys(self, service, sample_stock_analysis_report):
        result = service.to_dict(sample_stock_analysis_report)
        assert 'stock_id' in result
        assert 'signal' in result
        assert 'summary' in result
        assert 'positives' in result
        assert 'risks' in result
        assert 'processing_status' in result

    def test_maps_fields_correctly(self, service, sample_stock_analysis_report):
        result = service.to_dict(sample_stock_analysis_report)
        assert result['stock_id'] == sample_stock_analysis_report.subject
        assert result['signal'] == sample_stock_analysis_report.sentiment
        assert result['summary'] == sample_stock_analysis_report.summary
