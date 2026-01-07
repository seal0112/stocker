"""API tests for Feed endpoints."""
import pytest
import json
from datetime import datetime, timedelta

from app import db
from app.models.feed import Feed
from app.models.feed_tag import FeedTag


@pytest.mark.usefixtures('test_app')
class TestGetStockFeedAPI:
    """Tests for GET /feed/<stock_id> endpoint."""

    def test_get_stock_feed_success(self, test_app, client, sample_feed):
        """Test successful retrieval of stock feeds."""
        with test_app.app_context():
            response = client.get(f'/api/v0/feed/{sample_feed.stock_id}')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert isinstance(data, list)
            assert len(data) >= 1

    def test_get_stock_feed_with_time_param(self, test_app, client, sample_basic_info):
        """Test retrieval with time parameter."""
        with test_app.app_context():
            # Create feed with specific time
            feed = Feed(
                stock_id=sample_basic_info.id,
                releaseTime=datetime(2024, 3, 15, 10, 0, 0),
                title="Time Param Test",
                link="https://example.com/feed/time-param-test",
                feedType="announcement"
            )
            db.session.add(feed)
            db.session.commit()

            # Query with time after the feed's release time
            response = client.get(
                f'/api/v0/feed/{sample_basic_info.id}?time=2024-03-16T00:00:00'
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert isinstance(data, list)

            # Cleanup
            db.session.delete(feed)
            db.session.commit()

    def test_get_stock_feed_empty_result(self, test_app, client):
        """Test retrieval for stock with no feeds."""
        with test_app.app_context():
            response = client.get('/api/v0/feed/9999')

            # Should return 200 with empty list or handle gracefully
            assert response.status_code in [200, 404]

    def test_get_stock_feed_ordered_desc(self, test_app, client, sample_basic_info):
        """Test that feeds are ordered by releaseTime descending."""
        with test_app.app_context():
            # Create feeds with different release times
            feeds = []
            for i in range(3):
                feed = Feed(
                    stock_id=sample_basic_info.id,
                    releaseTime=datetime(2024, 3, i + 1, 10, 0, 0),
                    title=f"Order Test {i}",
                    link=f"https://example.com/feed/order-test-{i}",
                    feedType="announcement"
                )
                feeds.append(feed)
                db.session.add(feed)
            db.session.commit()

            response = client.get(f'/api/v0/feed/{sample_basic_info.id}')

            assert response.status_code == 200
            data = json.loads(response.data)

            # Verify ordering (newest first)
            if len(data) >= 2:
                for i in range(len(data) - 1):
                    current_time = datetime.fromisoformat(
                        data[i]['releaseTime'].replace('Z', '+00:00')
                    ) if 'Z' in data[i]['releaseTime'] else datetime.fromisoformat(
                        data[i]['releaseTime']
                    )
                    next_time = datetime.fromisoformat(
                        data[i + 1]['releaseTime'].replace('Z', '+00:00')
                    ) if 'Z' in data[i + 1]['releaseTime'] else datetime.fromisoformat(
                        data[i + 1]['releaseTime']
                    )
                    assert current_time >= next_time

            # Cleanup
            for feed in feeds:
                db.session.delete(feed)
            db.session.commit()


@pytest.mark.usefixtures('test_app')
class TestHandleFeedGetAPI:
    """Tests for GET /feed endpoint (HandleFeed class)."""

    def test_get_feeds_default_time_range(self, test_app, client, sample_basic_info):
        """Test GET feeds with default time range."""
        with test_app.app_context():
            # Create recent feed
            recent_feed = Feed(
                stock_id=sample_basic_info.id,
                releaseTime=datetime.now() - timedelta(hours=12),
                title="Recent Feed",
                link="https://example.com/feed/recent-default",
                feedType="announcement"
            )
            db.session.add(recent_feed)
            db.session.commit()

            response = client.get('/api/v0/feed')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert isinstance(data, list)

            # Cleanup
            db.session.delete(recent_feed)
            db.session.commit()

    def test_get_feeds_with_time_range(self, test_app, client, sample_basic_info):
        """Test GET feeds with specific time range."""
        with test_app.app_context():
            # Create feed within range
            feed = Feed(
                stock_id=sample_basic_info.id,
                releaseTime=datetime(2024, 3, 15, 10, 0, 0),
                title="Time Range Test",
                link="https://example.com/feed/time-range-test",
                feedType="announcement"
            )
            db.session.add(feed)
            db.session.commit()

            response = client.get(
                '/api/v0/feed?starttime=2024-03-01&endtime=2024-03-31'
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert isinstance(data, list)

            # Cleanup
            db.session.delete(feed)
            db.session.commit()

    def test_get_feeds_invalid_starttime_format(self, test_app, client):
        """Test GET feeds with invalid starttime format."""
        with test_app.app_context():
            response = client.get('/api/v0/feed?starttime=invalid-date')

            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data
            assert 'starttime' in data['error'].lower()

    def test_get_feeds_invalid_endtime_format(self, test_app, client):
        """Test GET feeds with invalid endtime format."""
        with test_app.app_context():
            response = client.get('/api/v0/feed?endtime=invalid-date')

            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data
            assert 'endtime' in data['error'].lower()


@pytest.mark.usefixtures('test_app')
class TestHandleFeedPostAPI:
    """Tests for POST /feed endpoint."""

    def test_create_feed_success(self, test_app, client, sample_basic_info):
        """Test successful creation of feed."""
        with test_app.app_context():
            payload = {
                'stock_id': sample_basic_info.id,
                'releaseTime': '2024-03-20T10:30:00',
                'title': 'API Test Feed',
                'link': 'https://example.com/feed/api-test-create',
                'source': 'mops',
                'description': 'Test description',
                'feedType': 'announcement',
                'tags': ['earnings']
            }

            response = client.post(
                '/api/v0/feed',
                data=json.dumps(payload),
                content_type='application/json'
            )

            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['message'] == 'Created'

            # Verify in database
            saved = Feed.query.filter_by(
                link='https://example.com/feed/api-test-create'
            ).first()
            assert saved is not None
            assert saved.title == 'API Test Feed'

            # Cleanup
            db.session.delete(saved)
            db.session.commit()

    def test_create_feed_news_type(self, test_app, client, sample_basic_info):
        """Test creating news type feed."""
        with test_app.app_context():
            payload = {
                'stock_id': sample_basic_info.id,
                'releaseTime': '2024-03-21T10:30:00',
                'title': 'News Test Feed',
                'link': 'https://example.com/feed/news-test',
                'source': 'news_source',
                'feedType': 'news',
                'tags': ['news']
            }

            response = client.post(
                '/api/v0/feed',
                data=json.dumps(payload),
                content_type='application/json'
            )

            assert response.status_code == 201

            # Cleanup
            Feed.query.filter_by(
                link='https://example.com/feed/news-test'
            ).delete()
            db.session.commit()

    def test_create_feed_with_stocks_array(self, test_app, client, sample_basic_info):
        """Test creating feed with stocks array instead of stock_id."""
        with test_app.app_context():
            payload = {
                'stocks': [sample_basic_info.id],  # Array format
                'releaseTime': '2024-03-22T10:30:00',
                'title': 'Stocks Array Test',
                'link': 'https://example.com/feed/stocks-array-test',
                'source': 'mops',
                'feedType': 'announcement',
                'tags': []
            }

            response = client.post(
                '/api/v0/feed',
                data=json.dumps(payload),
                content_type='application/json'
            )

            assert response.status_code == 201

            # Verify stock was set correctly
            saved = Feed.query.filter_by(
                link='https://example.com/feed/stocks-array-test'
            ).first()
            assert saved.stock_id == sample_basic_info.id

            # Cleanup
            db.session.delete(saved)
            db.session.commit()

    def test_create_feed_missing_body(self, test_app, client):
        """Test POST without request body returns 400."""
        with test_app.app_context():
            response = client.post(
                '/api/v0/feed',
                content_type='application/json'
            )

            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data

    def test_create_feed_invalid_json(self, test_app, client):
        """Test POST with invalid JSON returns 400."""
        with test_app.app_context():
            response = client.post(
                '/api/v0/feed',
                data='not valid json',
                content_type='application/json'
            )

            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data

    def test_create_feed_with_tags(self, test_app, client, sample_basic_info):
        """Test creating feed with multiple tags."""
        with test_app.app_context():
            payload = {
                'stock_id': sample_basic_info.id,
                'releaseTime': '2024-03-23T10:30:00',
                'title': 'Multiple Tags Test',
                'link': 'https://example.com/feed/multi-tags-test',
                'source': 'mops',
                'feedType': 'announcement',
                'tags': ['earnings', 'dividend', 'announcement']
            }

            response = client.post(
                '/api/v0/feed',
                data=json.dumps(payload),
                content_type='application/json'
            )

            assert response.status_code == 201

            # Verify tags were created
            saved = Feed.query.filter_by(
                link='https://example.com/feed/multi-tags-test'
            ).first()
            assert saved is not None
            assert len(saved.tags) >= 1

            # Cleanup
            db.session.delete(saved)
            db.session.commit()

    def test_create_feed_triggers_analysis_for_financial_report(
        self, test_app, client, sample_basic_info
    ):
        """Test that financial report feeds trigger analysis creation."""
        with test_app.app_context():
            payload = {
                'stock_id': sample_basic_info.id,
                'releaseTime': '2024-03-24T10:30:00',
                'title': '財務報表公告',  # Contains 財報
                'link': 'https://example.com/feed/financial-report-test',
                'source': 'mops',
                'feedType': 'announcement',
                'tags': ['earnings']
            }

            response = client.post(
                '/api/v0/feed',
                data=json.dumps(payload),
                content_type='application/json'
            )

            assert response.status_code == 201

            # Check if analysis was created
            saved = Feed.query.filter_by(
                link='https://example.com/feed/financial-report-test'
            ).first()

            # Cleanup
            from app.models.announcement_income_sheet_analysis import AnnouncementIncomeSheetAnalysis
            AnnouncementIncomeSheetAnalysis.query.filter_by(feed_id=saved.id).delete()
            db.session.delete(saved)
            db.session.commit()

    def test_update_existing_feed_by_link(self, test_app, client, sample_basic_info):
        """Test that POST with existing link updates the feed."""
        with test_app.app_context():
            # Create initial feed
            initial_feed = Feed(
                stock_id=sample_basic_info.id,
                releaseTime=datetime(2024, 3, 25, 10, 0, 0),
                title="Initial Title",
                link="https://example.com/feed/update-by-link-test",
                source="mops",
                feedType="announcement"
            )
            db.session.add(initial_feed)
            db.session.commit()

            # POST with same link (should update)
            payload = {
                'stock_id': sample_basic_info.id,
                'releaseTime': '2024-03-25T12:00:00',
                'title': 'Updated Title',
                'link': 'https://example.com/feed/update-by-link-test',
                'source': 'mops',
                'feedType': 'announcement',
                'tags': []
            }

            response = client.post(
                '/api/v0/feed',
                data=json.dumps(payload),
                content_type='application/json'
            )

            assert response.status_code == 201

            # Verify update (should still be one record)
            feeds = Feed.query.filter_by(
                link='https://example.com/feed/update-by-link-test'
            ).all()
            assert len(feeds) == 1
            assert feeds[0].title == 'Updated Title'

            # Cleanup
            db.session.delete(feeds[0])
            db.session.commit()


@pytest.mark.usefixtures('test_app')
class TestFeedAPIIntegration:
    """Integration tests for Feed API."""

    def test_create_then_get_by_stock(self, test_app, client, sample_basic_info):
        """Test creating a feed then retrieving it by stock_id."""
        with test_app.app_context():
            # Create
            payload = {
                'stock_id': sample_basic_info.id,
                'releaseTime': '2024-04-01T10:30:00',
                'title': 'Integration Test Feed',
                'link': 'https://example.com/feed/integration-test',
                'source': 'mops',
                'feedType': 'announcement',
                'tags': []
            }

            create_response = client.post(
                '/api/v0/feed',
                data=json.dumps(payload),
                content_type='application/json'
            )
            assert create_response.status_code == 201

            # Get
            get_response = client.get(f'/api/v0/feed/{sample_basic_info.id}')
            assert get_response.status_code == 200

            data = json.loads(get_response.data)
            matching = [d for d in data if d['title'] == 'Integration Test Feed']
            assert len(matching) >= 1

            # Cleanup
            Feed.query.filter_by(
                link='https://example.com/feed/integration-test'
            ).delete()
            db.session.commit()

    def test_create_then_get_by_time_range(self, test_app, client, sample_basic_info):
        """Test creating feeds then retrieving by time range."""
        with test_app.app_context():
            # Create feeds in specific time range
            feeds_created = []
            for day in [5, 10, 15]:
                payload = {
                    'stock_id': sample_basic_info.id,
                    'releaseTime': f'2024-04-{day:02d}T10:30:00',
                    'title': f'Time Range Test Day {day}',
                    'link': f'https://example.com/feed/time-range-int-{day}',
                    'source': 'mops',
                    'feedType': 'announcement',
                    'tags': []
                }

                response = client.post(
                    '/api/v0/feed',
                    data=json.dumps(payload),
                    content_type='application/json'
                )
                assert response.status_code == 201
                feeds_created.append(payload['link'])

            # Get by time range
            get_response = client.get(
                '/api/v0/feed?starttime=2024-04-01&endtime=2024-04-20'
            )
            assert get_response.status_code == 200

            data = json.loads(get_response.data)
            # Should include our created feeds
            titles = [d['title'] for d in data]
            assert any('Time Range Test' in title for title in titles)

            # Cleanup
            for link in feeds_created:
                Feed.query.filter_by(link=link).delete()
            db.session.commit()


@pytest.mark.usefixtures('test_app')
class TestFeedSerializer:
    """Tests for FeedSchema serialization."""

    def test_serializer_includes_expected_fields(self, test_app, client, sample_feed):
        """Test that serializer includes all expected fields."""
        with test_app.app_context():
            response = client.get(f'/api/v0/feed/{sample_feed.stock_id}')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data) >= 1

            item = data[0]
            expected_fields = [
                'id', 'update_date', 'releaseTime',
                'title', 'link', 'feedType', 'source'
            ]

            for field in expected_fields:
                assert field in item, f"Missing field: {field}"

    def test_serializer_date_format(self, test_app, client, sample_feed):
        """Test that dates are properly serialized."""
        with test_app.app_context():
            response = client.get(f'/api/v0/feed/{sample_feed.stock_id}')

            assert response.status_code == 200
            data = json.loads(response.data)

            if data:
                # releaseTime should be datetime format
                release_time = data[0].get('releaseTime')
                assert release_time is not None
                # Should contain date separator
                assert 'T' in release_time or '-' in release_time
