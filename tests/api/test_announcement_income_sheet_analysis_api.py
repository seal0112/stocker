import pytest
import json
from datetime import date, timedelta

from app.models.announcement_income_sheet_analysis import AnnouncementIncomeSheetAnalysis
from app.models.feed import Feed


@pytest.mark.usefixtures('test_app')
class TestAnnouncementIncomeSheetAnalysisAPI:
    """Test suite for AnnouncementIncomeSheetAnalysis API endpoints."""

    def test_get_list_empty(self, test_app, client):
        """Test getting list when no data exists."""
        with test_app.app_context():
            from app import db

            # Clean up any existing data
            AnnouncementIncomeSheetAnalysis.query.delete()
            db.session.commit()

            response = client.get('/api/v0/announcement_income_sheet_analysis')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert isinstance(data, list)
            assert len(data) == 0

    def test_get_list_with_data(
        self, test_app, client, sample_announcement_income_sheet_analysis
    ):
        """Test getting list with data."""
        with test_app.app_context():
            response = client.get('/api/v0/announcement_income_sheet_analysis')

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

    def test_get_list_filter_by_date(self, test_app, client, sample_feed):
        """Test filtering by specific date."""
        with test_app.app_context():
            from app import db

            test_date = date(2024, 5, 20)

            # Create test data with specific date
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

            # Test with date filter
            response = client.get(
                f'/api/v0/announcement_income_sheet_analysis?date=2024-05-20'
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data) >= 1
            assert all(d['update_date'] == '2024-05-20' for d in data)
            assert any(d['feed_id'] == sample_feed.id for d in data)

            # Cleanup
            db.session.delete(analysis)
            db.session.commit()

    def test_get_list_filter_by_date_range(self, test_app, client, sample_feed):
        """Test filtering by date range."""
        with test_app.app_context():
            from app import db

            # Create test data for different dates
            date1 = date(2024, 3, 1)
            date2 = date(2024, 3, 15)
            date3 = date(2024, 3, 30)

            # Create feeds for each date
            feed1 = Feed(
                stock_id=sample_feed.stock_id,
                releaseTime=date1,
                title='測試1',
                link='https://example.com/1',
                feedType='announcement'
            )
            feed2 = Feed(
                stock_id=sample_feed.stock_id,
                releaseTime=date2,
                title='測試2',
                link='https://example.com/2',
                feedType='announcement'
            )
            feed3 = Feed(
                stock_id=sample_feed.stock_id,
                releaseTime=date3,
                title='測試3',
                link='https://example.com/3',
                feedType='announcement'
            )
            db.session.add_all([feed1, feed2, feed3])
            db.session.commit()

            analysis1 = AnnouncementIncomeSheetAnalysis(
                feed_id=feed1.id,
                stock_id=sample_feed.stock_id,
                update_date=date1,
                營業收入合計=1000000000
            )
            analysis2 = AnnouncementIncomeSheetAnalysis(
                feed_id=feed2.id,
                stock_id=sample_feed.stock_id,
                update_date=date2,
                營業收入合計=1500000000
            )
            analysis3 = AnnouncementIncomeSheetAnalysis(
                feed_id=feed3.id,
                stock_id=sample_feed.stock_id,
                update_date=date3,
                營業收入合計=2000000000
            )
            db.session.add_all([analysis1, analysis2, analysis3])
            db.session.commit()

            # Test with date range
            response = client.get(
                '/api/v0/announcement_income_sheet_analysis?start_date=2024-03-10&end_date=2024-03-25'
            )

            assert response.status_code == 200
            data = json.loads(response.data)

            # Should only include date2 (2024-03-15)
            dates_in_response = [d['update_date'] for d in data]
            assert '2024-03-15' in dates_in_response
            assert '2024-03-01' not in dates_in_response
            assert '2024-03-30' not in dates_in_response

            # Cleanup
            db.session.delete(analysis1)
            db.session.delete(analysis2)
            db.session.delete(analysis3)
            db.session.delete(feed1)
            db.session.delete(feed2)
            db.session.delete(feed3)
            db.session.commit()

    def test_get_list_filter_by_start_date_only(self, test_app, client, sample_feed):
        """Test filtering by start_date only."""
        with test_app.app_context():
            from app import db

            date1 = date(2024, 6, 1)
            date2 = date(2024, 6, 15)

            # Create feeds
            feed1 = Feed(
                stock_id=sample_feed.stock_id,
                releaseTime=date1,
                title='測試1',
                link='https://example.com/test1',
                feedType='announcement'
            )
            feed2 = Feed(
                stock_id=sample_feed.stock_id,
                releaseTime=date2,
                title='測試2',
                link='https://example.com/test2',
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

            # Test with start_date only
            response = client.get(
                '/api/v0/announcement_income_sheet_analysis?start_date=2024-06-10'
            )

            assert response.status_code == 200
            data = json.loads(response.data)

            # Should only include date2 (2024-06-15)
            dates_in_response = [d['update_date'] for d in data if d['feed_id'] in [feed1.id, feed2.id]]
            assert '2024-06-15' in dates_in_response
            assert '2024-06-01' not in dates_in_response

            # Cleanup
            db.session.delete(analysis1)
            db.session.delete(analysis2)
            db.session.delete(feed1)
            db.session.delete(feed2)
            db.session.commit()

    def test_get_list_filter_by_end_date_only(self, test_app, client, sample_feed):
        """Test filtering by end_date only."""
        with test_app.app_context():
            from app import db

            date1 = date(2024, 7, 1)
            date2 = date(2024, 7, 15)

            # Create feeds
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

            # Test with end_date only
            response = client.get(
                '/api/v0/announcement_income_sheet_analysis?end_date=2024-07-10'
            )

            assert response.status_code == 200
            data = json.loads(response.data)

            # Should only include date1 (2024-07-01)
            dates_in_response = [d['update_date'] for d in data if d['feed_id'] in [feed1.id, feed2.id]]
            assert '2024-07-01' in dates_in_response
            assert '2024-07-15' not in dates_in_response

            # Cleanup
            db.session.delete(analysis1)
            db.session.delete(analysis2)
            db.session.delete(feed1)
            db.session.delete(feed2)
            db.session.commit()

    def test_invalid_date_format(self, test_app, client):
        """Test error handling for invalid date format."""
        with test_app.app_context():
            # Test invalid date format
            response = client.get(
                '/api/v0/announcement_income_sheet_analysis?date=2024/05/20'
            )

            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data
            assert 'Invalid date format' in data['error']

    def test_invalid_start_date_format(self, test_app, client):
        """Test error handling for invalid start_date format."""
        with test_app.app_context():
            response = client.get(
                '/api/v0/announcement_income_sheet_analysis?start_date=invalid-date'
            )

            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data
            assert 'start_date' in data['error']

    def test_invalid_end_date_format(self, test_app, client):
        """Test error handling for invalid end_date format."""
        with test_app.app_context():
            response = client.get(
                '/api/v0/announcement_income_sheet_analysis?end_date=20240520'
            )

            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data
            assert 'end_date' in data['error']

    def test_ordering_by_date_desc(self, test_app, client, sample_feed):
        """Test that results are ordered by update_date descending."""
        with test_app.app_context():
            from app import db

            # Create feeds
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

            # Create analysis records
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

            # Get list
            response = client.get('/api/v0/announcement_income_sheet_analysis')

            assert response.status_code == 200
            data = json.loads(response.data)

            # Find our test records in the response
            test_records = [d for d in data if d['feed_id'] in [feed1.id, feed2.id]]
            assert len(test_records) == 2

            # Verify ordering (newest first)
            assert test_records[0]['update_date'] == '2024-12-31'
            assert test_records[1]['update_date'] == '2024-01-01'

            # Cleanup
            db.session.delete(analysis1)
            db.session.delete(analysis2)
            db.session.delete(feed1)
            db.session.delete(feed2)
            db.session.commit()

    def test_get_list_with_multiple_stocks(
        self, test_app, client, sample_basic_info, sample_basic_info_2
    ):
        """Test getting list with multiple stocks."""
        with test_app.app_context():
            from app import db

            # Create feeds for different stocks
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

            # Create analysis records
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

            # Get list
            response = client.get('/api/v0/announcement_income_sheet_analysis')

            assert response.status_code == 200
            data = json.loads(response.data)

            # Should include both stocks
            stock_ids = [d['stock_id'] for d in data]
            assert '2330' in stock_ids
            assert '2317' in stock_ids

            # Cleanup
            db.session.delete(analysis1)
            db.session.delete(analysis2)
            db.session.delete(feed1)
            db.session.delete(feed2)
            db.session.commit()

    def test_get_list_requires_jwt(self, test_app, sample_announcement_income_sheet_analysis):
        """Test that the endpoint requires JWT authentication."""
        with test_app.app_context():
            # Create client without JWT token
            from flask import Flask
            test_client = test_app.test_client()

            # Should return 401 Unauthorized
            response = test_client.get('/api/v0/announcement_income_sheet_analysis')

            assert response.status_code == 401

    def test_serializer_field_types(
        self, test_app, client, sample_announcement_income_sheet_analysis
    ):
        """Test that serializer returns correct field types."""
        with test_app.app_context():
            response = client.get('/api/v0/announcement_income_sheet_analysis')

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
