"""Tests for GET /api/v0/ai_usage_report"""
import pytest
from datetime import datetime

from app import db
from app.earnings_call.models import EarningsCall, EarningsCallSummary
from app.database_setup import BasicInformation


@pytest.fixture(autouse=True)
def clean_data(test_app):
    with test_app.app_context():
        EarningsCallSummary.query.delete()
        EarningsCall.query.delete()
        db.session.commit()
    yield
    with test_app.app_context():
        EarningsCallSummary.query.delete()
        EarningsCall.query.delete()
        db.session.commit()


@pytest.fixture
def stock(test_app):
    with test_app.app_context():
        s = BasicInformation.query.filter_by(id='2330').first()
        if not s:
            s = BasicInformation(id='2330', 公司名稱='台積電')
            db.session.add(s)
            db.session.commit()
        yield '2330'


@pytest.fixture
def sample_summaries(test_app, stock):
    with test_app.app_context():
        ec1 = EarningsCall(stock_id='2330', meeting_date='2026-06-01')
        ec2 = EarningsCall(stock_id='2330', meeting_date='2026-06-10')
        db.session.add_all([ec1, ec2])
        db.session.flush()

        s1 = EarningsCallSummary(
            earnings_call_id=ec1.id,
            stock_id='2330',
            processing_status='completed',
            model_name='gemini-2.0-flash',
            input_tokens=1000,
            output_tokens=200,
            total_tokens=1200,
            cost_usd=0.001,
            cost_twd=0.032,
            created_at=datetime(2026, 6, 1, 10, 0, 0),
        )
        s2 = EarningsCallSummary(
            earnings_call_id=ec2.id,
            stock_id='2330',
            processing_status='completed',
            model_name='gemini-2.0-flash',
            input_tokens=2000,
            output_tokens=400,
            total_tokens=2400,
            cost_usd=0.002,
            cost_twd=0.065,
            created_at=datetime(2026, 6, 10, 10, 0, 0),
        )
        db.session.add_all([s1, s2])
        db.session.commit()


class TestUsageReport:

    def test_unauthenticated_401(self, client):
        assert client.get('/api/v0/ai_usage_report').status_code == 401

    def test_regular_user_403(self, authenticated_client):
        assert authenticated_client.get('/api/v0/ai_usage_report').status_code == 403

    def test_admin_empty_result(self, admin_authenticated_client):
        resp = admin_authenticated_client.get(
            '/api/v0/ai_usage_report?date_from=2020-01-01&date_to=2020-01-31'
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['by_model'] == []
        assert data['daily'] == []

    def test_returns_correct_structure(self, admin_authenticated_client, sample_summaries):
        resp = admin_authenticated_client.get(
            '/api/v0/ai_usage_report?date_from=2026-06-01&date_to=2026-06-30'
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'by_feature' in data
        assert 'by_model' in data
        assert 'daily' in data
        assert data['date_from'] == '2026-06-01'
        assert data['date_to'] == '2026-06-30'

    def test_by_feature_totals(self, admin_authenticated_client, sample_summaries):
        resp = admin_authenticated_client.get(
            '/api/v0/ai_usage_report?date_from=2026-06-01&date_to=2026-06-30'
        )
        by_feature = resp.get_json()['by_feature']
        assert len(by_feature) == 1
        assert by_feature[0]['feature'] == '法說會摘要'
        assert by_feature[0]['input_tokens'] == 3000
        assert by_feature[0]['count'] == 2

    def test_by_model_aggregation(self, admin_authenticated_client, sample_summaries):
        resp = admin_authenticated_client.get(
            '/api/v0/ai_usage_report?date_from=2026-06-01&date_to=2026-06-30'
        )
        by_model = resp.get_json()['by_model']
        assert len(by_model) == 1
        assert by_model[0]['model_name'] == 'gemini-2.0-flash'
        assert by_model[0]['total_tokens'] == 3600

    def test_daily_breakdown(self, admin_authenticated_client, sample_summaries):
        resp = admin_authenticated_client.get(
            '/api/v0/ai_usage_report?date_from=2026-06-01&date_to=2026-06-30'
        )
        daily = resp.get_json()['daily']
        assert len(daily) == 2
        dates = [d['date'] for d in daily]
        assert '2026-06-01' in dates
        assert '2026-06-10' in dates

    def test_date_range_filter(self, admin_authenticated_client, sample_summaries):
        resp = admin_authenticated_client.get(
            '/api/v0/ai_usage_report?date_from=2026-06-01&date_to=2026-06-05'
        )
        by_model = resp.get_json()['by_model']
        assert by_model[0]['count'] == 1
        assert by_model[0]['input_tokens'] == 1000

    def test_failed_records_excluded(self, admin_authenticated_client, test_app, stock):
        with test_app.app_context():
            ec = EarningsCall(stock_id='2330', meeting_date='2026-06-15')
            db.session.add(ec)
            db.session.flush()
            s = EarningsCallSummary(
                earnings_call_id=ec.id,
                stock_id='2330',
                processing_status='failed',
                model_name='gemini-2.0-flash',
                cost_twd=9.99,
                created_at=datetime(2026, 6, 15, 10, 0, 0),
            )
            db.session.add(s)
            db.session.commit()

        resp = admin_authenticated_client.get(
            '/api/v0/ai_usage_report?date_from=2026-06-01&date_to=2026-06-30'
        )
        by_model = resp.get_json()['by_model']
        assert by_model == []
