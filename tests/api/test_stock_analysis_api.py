"""API tests for stock qualitative analysis endpoint."""
import pytest
from unittest.mock import patch

from app import db
from app.ai_report.models import AiReport
from app.stock_analysis.services import REPORT_TYPE, PROMPT_NAME

FAKE_CLAUDE_RESPONSE = {
    'result': {
        'signal': '買進',
        'summary': '近期營運正向。',
        'positives': ['毛利率提升'],
        'risks': ['匯率風險'],
        'data_freshness': '2026-05-15 法說會',
    },
    'raw': '{"signal":"買進","summary":"近期營運正向。","positives":["毛利率提升"],"risks":["匯率風險"],"data_freshness":"2026-05-15 法說會"}',
    'input_tokens': 800,
    'output_tokens': 150,
    'model': 'claude-haiku-4-5-20251001',
}


class TestStockQualitativeAnalysisApi:

    def test_returns_cached_result(self, client, sample_stock_analysis_report):
        stock_id = sample_stock_analysis_report.subject
        response = client.get(f'/api/v0/stock_analysis/{stock_id}')

        assert response.status_code == 200
        data = response.get_json()
        assert data['stock_id'] == stock_id
        assert data['signal'] == sample_stock_analysis_report.sentiment
        assert data['processing_status'] == 'completed'

    def test_returns_422_when_no_prompt(self, client, sample_basic_info):
        response = client.get(f'/api/v0/stock_analysis/{sample_basic_info.id}')

        assert response.status_code == 422
        data = response.get_json()
        assert 'error' in data
        assert PROMPT_NAME in data['error']

    def test_creates_and_returns_analysis(self, client, sample_basic_info, sample_ai_prompt):
        from app.stock_analysis.services import StockAnalysisService
        with (
            patch.object(StockAnalysisService, '_get_api_key_value', return_value='test-key'),
            patch.object(StockAnalysisService, 'call_ai', return_value=FAKE_CLAUDE_RESPONSE),
        ):
            response = client.get(f'/api/v0/stock_analysis/{sample_basic_info.id}')

        assert response.status_code == 200
        data = response.get_json()
        assert data['signal'] == '買進'
        assert data['summary'] == '近期營運正向。'
        assert isinstance(data['positives'], list)
        assert isinstance(data['risks'], list)

        # Cleanup
        AiReport.query.filter_by(
            report_type=REPORT_TYPE,
            subject=sample_basic_info.id,
        ).delete()
        db.session.commit()

    def test_response_structure(self, client, sample_stock_analysis_report):
        stock_id = sample_stock_analysis_report.subject
        response = client.get(f'/api/v0/stock_analysis/{stock_id}')

        data = response.get_json()
        expected_keys = {'stock_id', 'signal', 'summary', 'positives', 'risks',
                         'data_freshness', 'processing_status', 'model_name', 'analyzed_at'}
        assert expected_keys.issubset(data.keys())
