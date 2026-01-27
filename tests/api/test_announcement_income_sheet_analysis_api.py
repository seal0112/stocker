"""API tests for AnnouncementIncomeSheetAnalysis endpoints."""
import pytest
import json
from datetime import date

from app import db
from app.models.announcement_income_sheet_analysis import AnnouncementIncomeSheetAnalysis
from app.models.feed import Feed


# ============================================================================
# Yield-based fixtures for automatic cleanup
# ============================================================================

@pytest.fixture
def temp_analysis_with_feed(sample_feed):
    """Create analysis with its feed, auto cleanup."""
    test_date = date(2024, 5, 20)

    analysis = AnnouncementIncomeSheetAnalysis(
        feed_id=sample_feed.id,
        stock_id=sample_feed.stock_id,
        update_date=test_date,
        year=2024,
        season='2',
        營業收入合計=1500000000,
        基本每股盈餘=6.0
    )
    db.session.add(analysis)
    db.session.commit()

    yield {'analysis': analysis, 'feed': sample_feed, 'date': test_date}

    db.session.delete(analysis)
    db.session.commit()


@pytest.fixture
def temp_feeds_with_analyses_date_range(sample_feed):
    """Create multiple feeds and analyses for date range testing."""
    date1 = date(2024, 3, 1)
    date2 = date(2024, 3, 15)
    date3 = date(2024, 3, 30)

    feeds = []
    analyses = []

    for i, (d, link_suffix) in enumerate([
        (date1, 'range1'), (date2, 'range2'), (date3, 'range3')
    ], 1):
        feed = Feed(
            stock_id=sample_feed.stock_id,
            releaseTime=d,
            title=f'測試{i}',
            link=f'https://example.com/{link_suffix}',
            feedType='announcement'
        )
        feeds.append(feed)
        db.session.add(feed)

    db.session.commit()

    for feed, d, revenue in zip(feeds, [date1, date2, date3],
                                 [1000000000, 1500000000, 2000000000]):
        analysis = AnnouncementIncomeSheetAnalysis(
            feed_id=feed.id,
            stock_id=sample_feed.stock_id,
            update_date=d,
            營業收入合計=revenue
        )
        analyses.append(analysis)
        db.session.add(analysis)

    db.session.commit()

    yield {
        'feeds': feeds,
        'analyses': analyses,
        'dates': [date1, date2, date3]
    }

    # Cleanup (analyses first due to FK)
    for analysis in analyses:
        db.session.delete(analysis)
    for feed in feeds:
        db.session.delete(feed)
    db.session.commit()


@pytest.fixture
def temp_feeds_with_analyses_start_date(sample_feed):
    """Create feeds and analyses for start_date testing."""
    date1 = date(2024, 6, 1)
    date2 = date(2024, 6, 15)

    feed1 = Feed(
        stock_id=sample_feed.stock_id,
        releaseTime=date1,
        title='測試1',
        link='https://example.com/start1',
        feedType='announcement'
    )
    feed2 = Feed(
        stock_id=sample_feed.stock_id,
        releaseTime=date2,
        title='測試2',
        link='https://example.com/start2',
        feedType='announcement'
    )
    db.session.add_all([feed1, feed2])
    db.session.commit()

    analysis1 = AnnouncementIncomeSheetAnalysis(
        feed_id=feed1.id,
        stock_id=sample_feed.stock_id,
        update_date=date1
    )
    analysis2 = AnnouncementIncomeSheetAnalysis(
        feed_id=feed2.id,
        stock_id=sample_feed.stock_id,
        update_date=date2
    )
    db.session.add_all([analysis1, analysis2])
    db.session.commit()

    yield {
        'feeds': [feed1, feed2],
        'analyses': [analysis1, analysis2],
        'dates': [date1, date2]
    }

    db.session.delete(analysis1)
    db.session.delete(analysis2)
    db.session.delete(feed1)
    db.session.delete(feed2)
    db.session.commit()


@pytest.fixture
def temp_feeds_with_analyses_end_date(sample_feed):
    """Create feeds and analyses for end_date testing."""
    date1 = date(2024, 7, 1)
    date2 = date(2024, 7, 15)

    feed1 = Feed(
        stock_id=sample_feed.stock_id,
        releaseTime=date1,
        title='測試1',
        link='https://example.com/end1',
        feedType='announcement'
    )
    feed2 = Feed(
        stock_id=sample_feed.stock_id,
        releaseTime=date2,
        title='測試2',
        link='https://example.com/end2',
        feedType='announcement'
    )
    db.session.add_all([feed1, feed2])
    db.session.commit()

    analysis1 = AnnouncementIncomeSheetAnalysis(
        feed_id=feed1.id,
        stock_id=sample_feed.stock_id,
        update_date=date1
    )
    analysis2 = AnnouncementIncomeSheetAnalysis(
        feed_id=feed2.id,
        stock_id=sample_feed.stock_id,
        update_date=date2
    )
    db.session.add_all([analysis1, analysis2])
    db.session.commit()

    yield {
        'feeds': [feed1, feed2],
        'analyses': [analysis1, analysis2],
        'dates': [date1, date2]
    }

    db.session.delete(analysis1)
    db.session.delete(analysis2)
    db.session.delete(feed1)
    db.session.delete(feed2)
    db.session.commit()


@pytest.fixture
def temp_feeds_with_analyses_ordering(sample_feed):
    """Create feeds and analyses for ordering tests."""
    feed1 = Feed(
        stock_id=sample_feed.stock_id,
        releaseTime=date(2024, 1, 1),
        title='舊資料',
        link='https://example.com/order1',
        feedType='announcement'
    )
    feed2 = Feed(
        stock_id=sample_feed.stock_id,
        releaseTime=date(2024, 12, 31),
        title='新資料',
        link='https://example.com/order2',
        feedType='announcement'
    )
    db.session.add_all([feed1, feed2])
    db.session.commit()

    analysis1 = AnnouncementIncomeSheetAnalysis(
        feed_id=feed1.id,
        stock_id=sample_feed.stock_id,
        update_date=date(2024, 1, 1),
        year=2024,
        season='1'
    )
    analysis2 = AnnouncementIncomeSheetAnalysis(
        feed_id=feed2.id,
        stock_id=sample_feed.stock_id,
        update_date=date(2024, 12, 31),
        year=2024,
        season='4'
    )
    db.session.add_all([analysis1, analysis2])
    db.session.commit()

    yield {
        'feeds': [feed1, feed2],
        'analyses': [analysis1, analysis2]
    }

    db.session.delete(analysis1)
    db.session.delete(analysis2)
    db.session.delete(feed1)
    db.session.delete(feed2)
    db.session.commit()


@pytest.fixture
def temp_feeds_with_analyses_multi_stock(sample_basic_info, sample_basic_info_2):
    """Create feeds and analyses for multiple stocks."""
    feed1 = Feed(
        stock_id=sample_basic_info.id,
        releaseTime=date.today(),
        title='2330測試',
        link='https://example.com/multi1',
        feedType='announcement'
    )
    feed2 = Feed(
        stock_id=sample_basic_info_2.id,
        releaseTime=date.today(),
        title='2317測試',
        link='https://example.com/multi2',
        feedType='announcement'
    )
    db.session.add_all([feed1, feed2])
    db.session.commit()

    analysis1 = AnnouncementIncomeSheetAnalysis(
        feed_id=feed1.id,
        stock_id=sample_basic_info.id,
        update_date=date.today(),
        營業收入合計=1000000000
    )
    analysis2 = AnnouncementIncomeSheetAnalysis(
        feed_id=feed2.id,
        stock_id=sample_basic_info_2.id,
        update_date=date.today(),
        營業收入合計=500000000
    )
    db.session.add_all([analysis1, analysis2])
    db.session.commit()

    yield {
        'feeds': [feed1, feed2],
        'analyses': [analysis1, analysis2]
    }

    db.session.delete(analysis1)
    db.session.delete(analysis2)
    db.session.delete(feed1)
    db.session.delete(feed2)
    db.session.commit()


# ============================================================================
# Test Classes
# ============================================================================

@pytest.mark.usefixtures('test_app')
class TestAnnouncementIncomeSheetAnalysisGetAPI:
    """Tests for GET /api/v0/announcement_income_sheet_analysis endpoints."""

    def test_get_list_empty(self, authenticated_client):
        """Test getting list when no data exists."""
        # Clean up any existing data
        AnnouncementIncomeSheetAnalysis.query.delete()
        db.session.commit()

        response = authenticated_client.get('/api/v0/announcement_income_sheet_analysis')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_list_with_data(self, authenticated_client, sample_announcement_income_sheet_analysis):
        """Test getting list with data."""
        response = authenticated_client.get('/api/v0/announcement_income_sheet_analysis')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) >= 1
        assert any(d['stock_id'] == '2330' for d in data)

        # Verify fields are present
        first_item = data[0]
        assert 'feed_id' in first_item
        assert 'stock_id' in first_item
        assert 'update_date' in first_item
        assert 'year' in first_item
        assert 'season' in first_item
        assert '營業收入合計' in first_item
        assert '基本每股盈餘' in first_item

    def test_get_list_filter_by_date(self, authenticated_client, temp_analysis_with_feed):
        """Test filtering by specific date."""
        response = authenticated_client.get(
            '/api/v0/announcement_income_sheet_analysis?date=2024-05-20'
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) >= 1
        assert all(d['update_date'] == '2024-05-20' for d in data)
        assert any(d['feed_id'] == temp_analysis_with_feed['feed'].id for d in data)

    def test_get_list_filter_by_date_range(self, authenticated_client, temp_feeds_with_analyses_date_range):
        """Test filtering by date range."""
        response = authenticated_client.get(
            '/api/v0/announcement_income_sheet_analysis?start_date=2024-03-10&end_date=2024-03-25'
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        # Should only include date2 (2024-03-15)
        dates_in_response = [d['update_date'] for d in data]
        assert '2024-03-15' in dates_in_response
        assert '2024-03-01' not in dates_in_response
        assert '2024-03-30' not in dates_in_response

    def test_get_list_filter_by_start_date_only(self, authenticated_client, temp_feeds_with_analyses_start_date):
        """Test filtering by start_date only."""
        feeds = temp_feeds_with_analyses_start_date['feeds']

        response = authenticated_client.get(
            '/api/v0/announcement_income_sheet_analysis?start_date=2024-06-10'
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        # Should only include date2 (2024-06-15)
        dates_in_response = [d['update_date'] for d in data if d['feed_id'] in [f.id for f in feeds]]
        assert '2024-06-15' in dates_in_response
        assert '2024-06-01' not in dates_in_response

    def test_get_list_filter_by_end_date_only(self, authenticated_client, temp_feeds_with_analyses_end_date):
        """Test filtering by end_date only."""
        feeds = temp_feeds_with_analyses_end_date['feeds']

        response = authenticated_client.get(
            '/api/v0/announcement_income_sheet_analysis?end_date=2024-07-10'
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        # Should only include date1 (2024-07-01)
        dates_in_response = [d['update_date'] for d in data if d['feed_id'] in [f.id for f in feeds]]
        assert '2024-07-01' in dates_in_response
        assert '2024-07-15' not in dates_in_response

    @pytest.mark.parametrize("param,value,error_keyword", [
        ("date", "2024/05/20", "Invalid date format"),
        ("start_date", "invalid-date", "start_date"),
        ("end_date", "20240520", "end_date"),
    ])
    def test_invalid_date_format(self, authenticated_client, param, value, error_keyword):
        """Test error handling for invalid date formats."""
        response = authenticated_client.get(
            f'/api/v0/announcement_income_sheet_analysis?{param}={value}'
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert error_keyword in data['error']

    def test_ordering_by_date_desc(self, authenticated_client, temp_feeds_with_analyses_ordering):
        """Test that results are ordered by update_date descending."""
        feeds = temp_feeds_with_analyses_ordering['feeds']

        response = authenticated_client.get('/api/v0/announcement_income_sheet_analysis')

        assert response.status_code == 200
        data = json.loads(response.data)

        # Find our test records in the response
        test_records = [d for d in data if d['feed_id'] in [f.id for f in feeds]]
        assert len(test_records) == 2

        # Verify ordering (newest first)
        assert test_records[0]['update_date'] == '2024-12-31'
        assert test_records[1]['update_date'] == '2024-01-01'

    def test_get_list_with_multiple_stocks(self, authenticated_client, temp_feeds_with_analyses_multi_stock):
        """Test getting list with multiple stocks."""
        response = authenticated_client.get('/api/v0/announcement_income_sheet_analysis')

        assert response.status_code == 200
        data = json.loads(response.data)

        # Should include both stocks
        stock_ids = [d['stock_id'] for d in data]
        assert '2330' in stock_ids
        assert '2317' in stock_ids


@pytest.mark.usefixtures('test_app')
class TestAnnouncementIncomeSheetAnalysisAuth:
    """Tests for authentication requirements."""

    def test_get_list_requires_jwt(self, test_app, sample_announcement_income_sheet_analysis):
        """Test that the endpoint requires JWT authentication."""
        # Create client without JWT token
        test_client = test_app.test_client()

        # Should return 401 Unauthorized
        response = test_client.get('/api/v0/announcement_income_sheet_analysis')

        assert response.status_code == 401


@pytest.mark.usefixtures('test_app')
class TestAnnouncementIncomeSheetAnalysisSerializer:
    """Tests for serialization."""

    def test_serializer_field_types(self, authenticated_client, sample_announcement_income_sheet_analysis):
        """Test that serializer returns correct field types."""
        response = authenticated_client.get('/api/v0/announcement_income_sheet_analysis')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) >= 1

        item = data[0]

        # Check integer fields
        assert isinstance(item['feed_id'], int)
        if item['營業收入合計'] is not None:
            assert isinstance(item['營業收入合計'], int)

        # Check string fields
        assert isinstance(item['stock_id'], str)
        if item['season'] is not None:
            assert isinstance(item['season'], str)

        # Check boolean fields
        assert isinstance(item['processing_failed'], bool)

        # Check numeric/float fields
        if item['營業毛利率'] is not None:
            assert isinstance(item['營業毛利率'], (int, float, str))
