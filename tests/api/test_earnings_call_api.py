"""Tests for EarningsCall API endpoints."""
import json
import pytest
from datetime import date, datetime, timedelta

from app import db
from app.earnings_call.models import EarningsCall, EarningsCallSummary
from app.models import Feed


@pytest.fixture
def earnings_call_summary(test_app, sample_earnings_call):
    """Create an EarningsCallSummary for the sample earnings call."""
    summary = EarningsCallSummary(
        earnings_call_id=sample_earnings_call.id,
        stock_id=sample_earnings_call.stock_id,
        processing_status='completed',
        capex='100億',
        capex_industry='半導體',
        outlook='正面展望',
        concerns_and_risks='地緣政治風險',
        key_points=['營收成長', '產能擴張'],
        source_feed_ids=[1, 2, 3]
    )
    db.session.add(summary)
    db.session.commit()

    yield summary

    EarningsCallSummary.query.filter_by(id=summary.id).delete()
    db.session.commit()


@pytest.fixture
def feed_near_earnings_call(test_app, sample_basic_info, sample_earnings_call):
    """Create a Feed near the earnings call meeting_date."""
    meeting_dt = datetime.combine(sample_earnings_call.meeting_date, datetime.min.time())
    feed = Feed(
        stock_id=sample_basic_info.id,
        releaseTime=meeting_dt + timedelta(hours=12),
        title='台積電法說會後新聞',
        link=f'https://test.com/ec-feed-{sample_earnings_call.id}',
        source='mops',
        feedType='news'
    )
    db.session.add(feed)
    db.session.commit()

    yield feed

    Feed.query.filter_by(id=feed.id).delete()
    db.session.commit()


class TestEarningsCallListGet:
    """Tests for GET /api/v0/earnings_call"""

    def test_get_success_with_stock_filter(self, test_app, authenticated_client, sample_earnings_call):
        """Should return earnings calls for the specified stock."""
        response = authenticated_client.get('/api/v0/earnings_call?stock=2330')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]['stock_id'] == '2330'

    def test_get_empty_result(self, test_app, authenticated_client, sample_basic_info):
        """Should return empty list when no earnings calls match."""
        response = authenticated_client.get('/api/v0/earnings_call?stock=9999')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_unauthorized_401(self, test_app, client):
        """Should return 401 for unauthenticated request."""
        response = client.get('/api/v0/earnings_call')
        assert response.status_code == 401

    def test_get_serializer_fields(self, test_app, authenticated_client, sample_earnings_call):
        """Response should contain expected serializer fields."""
        response = authenticated_client.get('/api/v0/earnings_call?stock=2330')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) >= 1
        item = data[0]
        expected_fields = ['id', 'stock_id', 'meeting_date', 'meeting_end_date',
                           'location', 'description', 'file_name_chinese']
        for field in expected_fields:
            assert field in item


class TestEarningsCallPost:
    """Tests for POST /api/v0/earnings_call"""

    def test_create_201(self, test_app, client, sample_basic_info):
        """Should create a new earnings call and return 201."""
        payload = {
            'stock_id': '2330',
            'meeting_date': '2025-01-15',
            'meeting_end_date': '2025-01-15',
            'location': '台北市信義區',
            'description': '2025年第一季法說會',
            'file_name_chinese': '2330_2025Q1法說會'
        }
        response = client.post(
            '/api/v0/earnings_call',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data['stock_id'] == '2330'
        assert data['description'] == '2025年第一季法說會'

        # Cleanup
        EarningsCall.query.filter_by(
            stock_id='2330', meeting_date=date(2025, 1, 15)).delete()
        db.session.commit()

    def test_create_duplicate_409(self, test_app, client, sample_earnings_call):
        """Should return 409 when earnings call already exists for same stock/date."""
        payload = {
            'stock_id': '2330',
            'meeting_date': '2024-04-18',
            'meeting_end_date': '2024-04-18',
            'location': '台北市',
            'description': '重複',
            'file_name_chinese': '重複'
        }
        response = client.post(
            '/api/v0/earnings_call',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 409
        assert 'already exists' in response.get_json()['error'].lower()

    def test_create_missing_body_400(self, test_app, client):
        """POST with empty body should return 400."""
        response = client.post(
            '/api/v0/earnings_call',
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_create_invalid_json_400(self, test_app, client):
        """POST with invalid JSON should return 400."""
        response = client.post(
            '/api/v0/earnings_call',
            data='not json',
            content_type='application/json'
        )
        assert response.status_code == 400


class TestEarningsCallPending:
    """Tests for GET /api/v0/earnings_call/pending"""

    def test_valid_date(self, test_app, client, sample_earnings_call):
        """Should return pending earnings calls for a given date."""
        response = client.get('/api/v0/earnings_call/pending?meeting_date=2024-04-18')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        # The sample_earnings_call has no summary, so it should be pending
        assert len(data) >= 1

    def test_missing_date_400(self, test_app, client):
        """Should return 400 when meeting_date is missing."""
        response = client.get('/api/v0/earnings_call/pending')
        assert response.status_code == 400
        assert 'required' in response.get_json()['error'].lower()

    def test_invalid_format_400(self, test_app, client):
        """Should return 400 for invalid date format."""
        response = client.get('/api/v0/earnings_call/pending?meeting_date=20240418')
        assert response.status_code == 400
        assert 'format' in response.get_json()['error'].lower()

    def test_no_results_empty_list(self, test_app, client):
        """Should return empty list when no pending calls on date."""
        response = client.get('/api/v0/earnings_call/pending?meeting_date=2000-01-01')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 0


class TestEarningsCallSummaryApi:
    """Tests for GET/POST/PUT /api/v0/earnings_call/<id>/summary"""

    def test_get_success(self, test_app, client, sample_earnings_call, earnings_call_summary):
        """Should return the summary for an earnings call."""
        ec_id = sample_earnings_call.id
        response = client.get(f'/api/v0/earnings_call/{ec_id}/summary')
        assert response.status_code == 200
        data = response.get_json()
        assert data['earnings_call_id'] == ec_id
        assert data['processing_status'] == 'completed'
        assert data['capex'] == '100億'

    def test_get_404(self, test_app, client, sample_earnings_call):
        """Should return 404 when no summary exists."""
        ec_id = sample_earnings_call.id
        response = client.get(f'/api/v0/earnings_call/{ec_id}/summary')
        assert response.status_code == 404

    def test_get_404_ec_not_found(self, test_app, client):
        """Should return 404 for non-existent earnings call."""
        response = client.get('/api/v0/earnings_call/99999/summary')
        assert response.status_code == 404

    def test_post_creates_pending_201(self, test_app, client, sample_earnings_call):
        """POST should create a pending summary record."""
        ec_id = sample_earnings_call.id
        response = client.post(f'/api/v0/earnings_call/{ec_id}/summary')
        assert response.status_code == 201
        data = response.get_json()
        assert data['earnings_call_id'] == ec_id
        assert data['processing_status'] == 'pending'

        # Cleanup
        EarningsCallSummary.query.filter_by(earnings_call_id=ec_id).delete()
        db.session.commit()

    def test_post_returns_existing_idempotent(self, test_app, client, sample_earnings_call, earnings_call_summary):
        """POST should return existing summary if one already exists (idempotent)."""
        ec_id = sample_earnings_call.id
        response = client.post(f'/api/v0/earnings_call/{ec_id}/summary')
        assert response.status_code == 201
        data = response.get_json()
        assert data['id'] == earnings_call_summary.id

    def test_post_404_ec_not_found(self, test_app, client):
        """POST should return 404 when earnings call doesn't exist."""
        response = client.post('/api/v0/earnings_call/99999/summary')
        assert response.status_code == 404

    def test_put_success(self, test_app, client, sample_earnings_call, earnings_call_summary):
        """PUT should update summary with AI content."""
        ec_id = sample_earnings_call.id
        payload = {
            'capex': '200億',
            'outlook': '非常正面',
            'processing_status': 'completed'
        }
        response = client.put(
            f'/api/v0/earnings_call/{ec_id}/summary',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['capex'] == '200億'
        assert data['outlook'] == '非常正面'

    def test_put_404(self, test_app, client, sample_earnings_call):
        """PUT should return 404 when no summary exists."""
        ec_id = sample_earnings_call.id
        payload = {'capex': '100億'}
        response = client.put(
            f'/api/v0/earnings_call/{ec_id}/summary',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 404

    def test_put_missing_body_400(self, test_app, client, sample_earnings_call, earnings_call_summary):
        """PUT with no body should return 400."""
        ec_id = sample_earnings_call.id
        response = client.put(
            f'/api/v0/earnings_call/{ec_id}/summary',
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_put_invalid_json_400(self, test_app, client, sample_earnings_call, earnings_call_summary):
        """PUT with invalid JSON should return 400."""
        ec_id = sample_earnings_call.id
        response = client.put(
            f'/api/v0/earnings_call/{ec_id}/summary',
            data='not json',
            content_type='application/json'
        )
        assert response.status_code == 400


class TestEarningsCallFeeds:
    """Tests for GET /api/v0/earnings_call/<id>/feeds"""

    def test_success_with_feeds(self, test_app, client, sample_earnings_call, feed_near_earnings_call):
        """Should return feeds related to the earnings call."""
        ec_id = sample_earnings_call.id
        response = client.get(f'/api/v0/earnings_call/{ec_id}/feeds')
        assert response.status_code == 200
        data = response.get_json()
        assert data['earnings_call_id'] == ec_id
        assert data['stock_id'] == '2330'
        assert data['feeds_count'] >= 1
        assert isinstance(data['feeds'], list)

    def test_ec_not_found_404(self, test_app, client):
        """Should return 404 for non-existent earnings call."""
        response = client.get('/api/v0/earnings_call/99999/feeds')
        assert response.status_code == 404

    def test_empty_feeds(self, test_app, client, sample_earnings_call):
        """Should return empty feeds list when no feeds near meeting date."""
        ec_id = sample_earnings_call.id
        response = client.get(f'/api/v0/earnings_call/{ec_id}/feeds')
        assert response.status_code == 200
        data = response.get_json()
        assert data['feeds_count'] == 0
        assert data['feeds'] == []

    def test_custom_days_after_param(self, test_app, client, sample_earnings_call, feed_near_earnings_call):
        """Should respect custom days_after parameter."""
        ec_id = sample_earnings_call.id
        response = client.get(f'/api/v0/earnings_call/{ec_id}/feeds?days_after=7')
        assert response.status_code == 200
        data = response.get_json()
        assert data['feeds_count'] >= 1
