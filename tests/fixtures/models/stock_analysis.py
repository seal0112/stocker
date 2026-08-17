"""Fixtures for stock_analysis tests: AiApiKey, AiPrompt, AiReport, recent Feed."""
import pytest
from datetime import date, datetime, timedelta

from app import db
from app.ai_api_key.models import AiApiKey
from app.ai_prompt.models import AiPrompt
from app.ai_report.models import AiReport
from app.models.feed import Feed
from app.stock_analysis.services import PROMPT_NAME, REPORT_TYPE


@pytest.fixture
def sample_recent_feed(sample_basic_info):
    """Feed with today's timestamp so it falls within the 30-day news window."""
    feed = Feed(
        stock_id=sample_basic_info.id,
        releaseTime=datetime.utcnow() - timedelta(days=3),
        title='近期法說會利多，營運展望正向',
        link='https://example.com/feed/recent-test',
        source='mops',
        feedType='announcement',
    )
    db.session.add(feed)
    db.session.commit()

    yield feed

    db.session.delete(feed)
    db.session.commit()


@pytest.fixture
def sample_ai_api_key():
    key = AiApiKey(
        name='test-claude-key',
        provider='claude',
        model='claude-haiku-4-5-20251001',
        owner='test',
        ssm_path='/test/claude/api_key',
        is_active=True,
    )
    db.session.add(key)
    db.session.commit()

    yield key

    db.session.delete(key)
    db.session.commit()


@pytest.fixture
def sample_ai_prompt(sample_ai_api_key):
    prompt = AiPrompt(
        name=PROMPT_NAME,
        provider='claude',
        content=(
            '請分析 {{company_name}}（{{stock_id}}）\n'
            '法說會：{{earnings_call_summaries}}\n'
            '新聞：{{news_titles}}\n'
            '輸出JSON: {"signal":"觀望","summary":"測試","positives":[],"risks":[],"data_freshness":""}'
        ),
        is_active=True,
        description='test prompt',
        api_key_id=sample_ai_api_key.id,
        schedule_enabled=False,
        created_by='test',
    )
    db.session.add(prompt)
    db.session.commit()

    yield prompt

    db.session.delete(prompt)
    db.session.commit()


@pytest.fixture
def sample_earnings_call_ai_report(sample_basic_info):
    report = AiReport(
        report_type='earnings_call',
        subject=sample_basic_info.id,
        period_start=date.today() - timedelta(days=60),
        period_end=date.today() - timedelta(days=60),
        prompt_name='earnings_call_summary',
        processing_status='completed',
        summary='本季營收成長，毛利率維持高檔，下季展望樂觀。',
        sentiment='Buy',
        score=3,
        key_points={'outlook': '正向'},
        model_name='claude-haiku-4-5-20251001',
        input_tokens=500,
        output_tokens=200,
        total_tokens=700,
    )
    db.session.add(report)
    db.session.commit()

    yield report

    db.session.delete(report)
    db.session.commit()


@pytest.fixture
def sample_stock_analysis_report(sample_basic_info):
    report = AiReport(
        report_type=REPORT_TYPE,
        subject=sample_basic_info.id,
        period_start=date.today(),
        period_end=date.today(),
        prompt_name=PROMPT_NAME,
        processing_status='completed',
        summary='近期營運正向，法說會展望樂觀。',
        sentiment='買進',
        key_points={
            'positives': ['毛利率提升'],
            'risks': ['匯率風險'],
            'data_freshness': f'{date.today() - timedelta(days=60)} 法說會',
        },
        model_name='claude-haiku-4-5-20251001',
        input_tokens=800,
        output_tokens=300,
        total_tokens=1100,
    )
    db.session.add(report)
    db.session.commit()

    yield report

    db.session.delete(report)
    db.session.commit()
