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
        score=3,
        sentiment='Buy',
        impact_duration='Long',
        source_reliability='Official',
        reasoning='官方確認長期資本支出計畫',
        news_contributions=[{'feed_id': 1, 'title': '法說', 'score_delta': 3, 'key_insight': '利多'}],
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

    def test_create_201(self, test_app, authenticated_client, sample_basic_info):
        """Should create a new earnings call and return 201."""
        payload = {
            'stock_id': '2330',
            'meeting_date': '2025-01-15',
            'meeting_end_date': '2025-01-15',
            'location': '台北市信義區',
            'description': '2025年第一季法說會',
            'file_name_chinese': '2330_2025Q1法說會'
        }
        response = authenticated_client.post(
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

    def test_create_duplicate_409(self, test_app, authenticated_client, sample_earnings_call):
        """Should return 409 when earnings call already exists for same stock/date."""
        meeting_date_str = sample_earnings_call.meeting_date.isoformat()
        payload = {
            'stock_id': '2330',
            'meeting_date': meeting_date_str,
            'meeting_end_date': meeting_date_str,
            'location': '台北市',
            'description': '重複',
            'file_name_chinese': '重複'
        }
        response = authenticated_client.post(
            '/api/v0/earnings_call',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 409
        assert 'already exists' in response.get_json()['error'].lower()

    def test_create_missing_body_400(self, test_app, authenticated_client):
        """POST with empty body should return 400."""
        response = authenticated_client.post(
            '/api/v0/earnings_call',
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_create_invalid_json_400(self, test_app, authenticated_client):
        """POST with invalid JSON should return 400."""
        response = authenticated_client.post(
            '/api/v0/earnings_call',
            data='not json',
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_create_unauthenticated_401(self, test_app, client):
        """POST without auth should return 401."""
        response = client.post(
            '/api/v0/earnings_call',
            data=json.dumps({'stock_id': '2330'}),
            content_type='application/json'
        )
        assert response.status_code == 401


class TestEarningsCallPending:
    """Tests for GET /api/v0/earnings_call/pending"""

    def test_unauthenticated_401(self, test_app, client):
        response = client.get('/api/v0/earnings_call/pending?meeting_date=2024-06-15')
        assert response.status_code == 401

    def test_valid_date(self, test_app, authenticated_client, sample_earnings_call):
        """Should return pending earnings calls for a given date."""
        meeting_date_str = sample_earnings_call.meeting_date.isoformat()
        response = authenticated_client.get(f'/api/v0/earnings_call/pending?meeting_date={meeting_date_str}')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_missing_date_400(self, test_app, authenticated_client):
        """Should return 400 when meeting_date is missing."""
        response = authenticated_client.get('/api/v0/earnings_call/pending')
        assert response.status_code == 400
        assert 'required' in response.get_json()['error'].lower()

    def test_invalid_format_400(self, test_app, authenticated_client):
        """Should return 400 for invalid date format."""
        response = authenticated_client.get('/api/v0/earnings_call/pending?meeting_date=20240418')
        assert response.status_code == 400
        assert 'format' in response.get_json()['error'].lower()

    def test_no_results_empty_list(self, test_app, authenticated_client):
        """Should return empty list when no pending calls on date."""
        response = authenticated_client.get('/api/v0/earnings_call/pending?meeting_date=2000-01-01')
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
        assert data['score'] == 3
        assert data['sentiment'] == 'Buy'
        assert data['impact_duration'] == 'Long'
        assert data['source_reliability'] == 'Official'
        assert data['reasoning'] == '官方確認長期資本支出計畫'
        assert isinstance(data['news_contributions'], list)

    def test_get_404(self, test_app, client, sample_earnings_call):
        """Should return 404 when no summary exists."""
        ec_id = sample_earnings_call.id
        response = client.get(f'/api/v0/earnings_call/{ec_id}/summary')
        assert response.status_code == 404

    def test_get_404_ec_not_found(self, test_app, client):
        """Should return 404 for non-existent earnings call."""
        response = client.get('/api/v0/earnings_call/99999/summary')
        assert response.status_code == 404

    def test_post_requires_admin_401(self, test_app, client, sample_earnings_call):
        """POST without auth should return 401."""
        ec_id = sample_earnings_call.id
        response = client.post(f'/api/v0/earnings_call/{ec_id}/summary')
        assert response.status_code == 401

    def test_post_requires_admin_403(self, test_app, authenticated_client, sample_earnings_call):
        """POST with regular user should return 403."""
        ec_id = sample_earnings_call.id
        response = authenticated_client.post(f'/api/v0/earnings_call/{ec_id}/summary')
        assert response.status_code == 403

    def test_post_creates_pending_201(self, test_app, admin_authenticated_client, sample_earnings_call):
        """POST by admin should create a pending summary record."""
        ec_id = sample_earnings_call.id
        response = admin_authenticated_client.post(f'/api/v0/earnings_call/{ec_id}/summary')
        assert response.status_code == 201
        data = response.get_json()
        assert data['earnings_call_id'] == ec_id
        assert data['processing_status'] == 'pending'

        # Cleanup
        EarningsCallSummary.query.filter_by(earnings_call_id=ec_id).delete()
        db.session.commit()

    def test_post_returns_existing_idempotent(self, test_app, admin_authenticated_client, sample_earnings_call, earnings_call_summary):
        """POST should return existing summary if one already exists (idempotent)."""
        ec_id = sample_earnings_call.id
        response = admin_authenticated_client.post(f'/api/v0/earnings_call/{ec_id}/summary')
        assert response.status_code == 201
        data = response.get_json()
        assert data['id'] == earnings_call_summary.id

    def test_post_404_ec_not_found(self, test_app, admin_authenticated_client):
        """POST should return 404 when earnings call doesn't exist."""
        response = admin_authenticated_client.post('/api/v0/earnings_call/99999/summary')
        assert response.status_code == 404

    def test_put_success(self, test_app, authenticated_client, sample_earnings_call, earnings_call_summary):
        """PUT should update summary with AI content."""
        ec_id = sample_earnings_call.id
        payload = {
            'capex': '200億',
            'outlook': '非常正面',
            'processing_status': 'completed',
            'score': 4,
            'sentiment': 'Strong Buy',
        }
        response = authenticated_client.put(
            f'/api/v0/earnings_call/{ec_id}/summary',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['capex'] == '200億'
        assert data['outlook'] == '非常正面'
        assert data['score'] == 4
        assert data['sentiment'] == 'Strong Buy'

    def test_put_404(self, test_app, authenticated_client, sample_earnings_call):
        """PUT should return 404 when no summary exists."""
        ec_id = sample_earnings_call.id
        payload = {'capex': '100億'}
        response = authenticated_client.put(
            f'/api/v0/earnings_call/{ec_id}/summary',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 404

    def test_put_missing_body_400(self, test_app, authenticated_client, sample_earnings_call, earnings_call_summary):
        """PUT with no body should return 400."""
        ec_id = sample_earnings_call.id
        response = authenticated_client.put(
            f'/api/v0/earnings_call/{ec_id}/summary',
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_put_invalid_json_400(self, test_app, authenticated_client, sample_earnings_call, earnings_call_summary):
        """PUT with invalid JSON should return 400."""
        ec_id = sample_earnings_call.id
        response = authenticated_client.put(
            f'/api/v0/earnings_call/{ec_id}/summary',
            data='not json',
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_put_unauthenticated_401(self, test_app, client, sample_earnings_call, earnings_call_summary):
        """PUT without auth should return 401."""
        ec_id = sample_earnings_call.id
        response = client.put(
            f'/api/v0/earnings_call/{ec_id}/summary',
            data=json.dumps({'capex': '100億'}),
            content_type='application/json'
        )
        assert response.status_code == 401


class TestEarningsCallFeeds:
    """Tests for GET /api/v0/earnings_call/<id>/feeds"""

    def test_unauthenticated_401(self, test_app, client, sample_earnings_call):
        response = client.get(f'/api/v0/earnings_call/{sample_earnings_call.id}/feeds')
        assert response.status_code == 401

    def test_success_with_feeds(self, test_app, authenticated_client, sample_earnings_call, feed_near_earnings_call):
        """Should return feeds related to the earnings call."""
        ec_id = sample_earnings_call.id
        response = authenticated_client.get(f'/api/v0/earnings_call/{ec_id}/feeds')
        assert response.status_code == 200
        data = response.get_json()
        assert data['earnings_call_id'] == ec_id
        assert data['stock_id'] == '2330'
        assert data['feeds_count'] >= 1
        assert isinstance(data['feeds'], list)

    def test_ec_not_found_404(self, test_app, authenticated_client):
        """Should return 404 for non-existent earnings call."""
        response = authenticated_client.get('/api/v0/earnings_call/99999/feeds')
        assert response.status_code == 404

    def test_empty_feeds(self, test_app, authenticated_client, sample_earnings_call):
        """Should return empty feeds list when no feeds near meeting date."""
        ec_id = sample_earnings_call.id
        response = authenticated_client.get(f'/api/v0/earnings_call/{ec_id}/feeds')
        assert response.status_code == 200
        data = response.get_json()
        assert data['feeds_count'] == 0
        assert data['feeds'] == []

    def test_custom_days_after_param(self, test_app, authenticated_client, sample_earnings_call, feed_near_earnings_call):
        """Should respect custom days_after parameter."""
        ec_id = sample_earnings_call.id
        response = authenticated_client.get(f'/api/v0/earnings_call/{ec_id}/feeds?days_after=7')
        assert response.status_code == 200
        data = response.get_json()
        assert data['feeds_count'] >= 1

    def test_keyword_filter_match(self, test_app, authenticated_client, sample_earnings_call, feed_near_earnings_call):
        """Should return feeds matching keyword in title."""
        ec_id = sample_earnings_call.id
        response = authenticated_client.get(f'/api/v0/earnings_call/{ec_id}/feeds?keywords=法說會')
        assert response.status_code == 200
        data = response.get_json()
        assert data['feeds_count'] >= 1

    def test_keyword_filter_no_match(self, test_app, authenticated_client, sample_earnings_call, feed_near_earnings_call):
        """Should return empty list when no feeds match keyword."""
        ec_id = sample_earnings_call.id
        response = authenticated_client.get(f'/api/v0/earnings_call/{ec_id}/feeds?keywords=不存在的關鍵字xyz')
        assert response.status_code == 200
        data = response.get_json()
        assert data['feeds_count'] == 0

    def test_multiple_keywords_or_logic(self, test_app, authenticated_client, sample_earnings_call, feed_near_earnings_call):
        """Multiple keywords should use OR logic."""
        ec_id = sample_earnings_call.id
        response = authenticated_client.get(f'/api/v0/earnings_call/{ec_id}/feeds?keywords=不存在xyz,法說會')
        assert response.status_code == 200
        data = response.get_json()
        assert data['feeds_count'] >= 1


class TestEarningsCallBoundFeeds:
    """Tests for GET /api/v0/earnings_call/<id>/bound_feeds"""

    @pytest.fixture
    def feed_with_contribution(self, test_app, sample_basic_info, sample_earnings_call):
        """Create two feeds and a summary whose news_contributions point to them."""
        meeting_dt = datetime.combine(sample_earnings_call.meeting_date, datetime.min.time())

        feed_a = Feed(
            stock_id=sample_basic_info.id,
            releaseTime=meeting_dt + timedelta(hours=2),
            title='AI晶片訂單能見度確立至2027年底',
            link='https://test.com/bound-feed-a',
            source='yahoo',
            feedType='news'
        )
        feed_b = Feed(
            stock_id=sample_basic_info.id,
            releaseTime=meeting_dt + timedelta(hours=4),
            title='美國關稅影響毛利率約2%',
            link='https://test.com/bound-feed-b',
            source='yahoo',
            feedType='news'
        )
        db.session.add_all([feed_a, feed_b])
        db.session.commit()

        summary = EarningsCallSummary(
            earnings_call_id=sample_earnings_call.id,
            stock_id=sample_earnings_call.stock_id,
            processing_status='completed',
            score=2,
            sentiment='Buy',
            news_contributions=[
                {'feed_id': feed_a.id, 'title': feed_a.title, 'score_delta': 3, 'key_insight': '長期利多'},
                {'feed_id': feed_b.id, 'title': feed_b.title, 'score_delta': -1, 'key_insight': '短期壓力'},
            ]
        )
        db.session.add(summary)
        db.session.commit()

        yield {'feed_a': feed_a, 'feed_b': feed_b, 'summary': summary}

        EarningsCallSummary.query.filter_by(id=summary.id).delete()
        Feed.query.filter(Feed.id.in_([feed_a.id, feed_b.id])).delete()
        db.session.commit()

    def test_returns_bound_feeds(self, test_app, authenticated_client, sample_earnings_call, feed_with_contribution):
        """Should return feeds linked via news_contributions."""
        ec_id = sample_earnings_call.id
        response = authenticated_client.get(f'/api/v0/earnings_call/{ec_id}/bound_feeds')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 2

    def test_feed_fields_present(self, test_app, authenticated_client, sample_earnings_call, feed_with_contribution):
        """Each item should have feed_id, title, link, releaseTime, score_delta, key_insight."""
        ec_id = sample_earnings_call.id
        response = authenticated_client.get(f'/api/v0/earnings_call/{ec_id}/bound_feeds')
        assert response.status_code == 200
        item = response.get_json()[0]
        for field in ('feed_id', 'title', 'link', 'releaseTime', 'score_delta', 'key_insight'):
            assert field in item, f"Missing field: {field}"

    def test_link_is_correct(self, test_app, authenticated_client, sample_earnings_call, feed_with_contribution):
        """link field should come from the real Feed record, not the JSON snapshot."""
        ec_id = sample_earnings_call.id
        response = authenticated_client.get(f'/api/v0/earnings_call/{ec_id}/bound_feeds')
        links = {item['link'] for item in response.get_json()}
        assert 'https://test.com/bound-feed-a' in links
        assert 'https://test.com/bound-feed-b' in links

    def test_sorted_by_score_delta_desc(self, test_app, authenticated_client, sample_earnings_call, feed_with_contribution):
        """Items should be sorted by score_delta descending (highest first)."""
        ec_id = sample_earnings_call.id
        response = authenticated_client.get(f'/api/v0/earnings_call/{ec_id}/bound_feeds')
        data = response.get_json()
        scores = [item['score_delta'] for item in data]
        assert scores == sorted(scores, reverse=True)

    def test_empty_when_no_summary(self, test_app, authenticated_client, sample_earnings_call):
        """Should return empty list when earnings call has no summary."""
        ec_id = sample_earnings_call.id
        response = authenticated_client.get(f'/api/v0/earnings_call/{ec_id}/bound_feeds')
        assert response.status_code == 200
        assert response.get_json() == []

    def test_empty_when_no_news_contributions(self, test_app, authenticated_client, sample_earnings_call):
        """Should return empty list when summary has no news_contributions."""
        summary = EarningsCallSummary(
            earnings_call_id=sample_earnings_call.id,
            stock_id=sample_earnings_call.stock_id,
            processing_status='pending',
            news_contributions=None
        )
        db.session.add(summary)
        db.session.commit()

        ec_id = sample_earnings_call.id
        response = authenticated_client.get(f'/api/v0/earnings_call/{ec_id}/bound_feeds')
        assert response.status_code == 200
        assert response.get_json() == []

        EarningsCallSummary.query.filter_by(id=summary.id).delete()
        db.session.commit()

    def test_ec_not_found_404(self, test_app, authenticated_client):
        """Should return 404 for non-existent earnings call."""
        response = authenticated_client.get('/api/v0/earnings_call/99999/bound_feeds')
        assert response.status_code == 404

    def test_unauthenticated_401(self, test_app, client, sample_earnings_call):
        """Endpoint should require JWT."""
        ec_id = sample_earnings_call.id
        response = client.get(f'/api/v0/earnings_call/{ec_id}/bound_feeds')
        assert response.status_code == 401


class TestEarningsCallListScoreFilter:
    """Tests for score_min/score_max filtering in GET /api/v0/earnings_call."""

    def test_score_filter_returns_matching(self, test_app, authenticated_client,
                                           sample_earnings_call, earnings_call_summary):
        """Should return earnings calls within score range."""
        response = authenticated_client.get('/api/v0/earnings_call?stock=2330&score_min=2&score_max=4')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        # summary has score=3, should match range 2-4
        assert len(data) >= 1

    def test_score_filter_excludes_non_matching(self, test_app, authenticated_client,
                                                 sample_earnings_call, earnings_call_summary):
        """Should exclude earnings calls outside score range."""
        response = authenticated_client.get('/api/v0/earnings_call?stock=2330&score_min=4&score_max=5')
        assert response.status_code == 200
        data = response.get_json()
        # summary has score=3, should not match range 4-5
        assert len(data) == 0

    def test_list_includes_summary_fields(self, test_app, authenticated_client,
                                          sample_earnings_call, earnings_call_summary):
        """List response should inline summary score/sentiment/status."""
        response = authenticated_client.get('/api/v0/earnings_call?stock=2330')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) >= 1
        item = data[0]
        assert 'summary' in item
        assert item['summary']['score'] == 3
        assert item['summary']['sentiment'] == 'Buy'
        assert item['summary']['processing_status'] == 'completed'
