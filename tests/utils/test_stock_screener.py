"""
Stock Screener Tests

Uses shared fixtures from tests/fixtures/models/ for test data.
The shared fixtures provide values that pass screener valuation checks:
- EPS (8.69) > 0.3 threshold
- core_business_ratio (41.67/43.33 = 0.96) > 0.7 threshold
"""
import pytest
from datetime import datetime, date, timedelta
from decimal import Decimal

from app.utils.stock_screener import StockScreenerManager
from app.models.recommended_stock import RecommendedStock


@pytest.fixture
def complete_stock_data(
    sample_basic_info, sample_daily_info,
    sample_income_sheet, sample_monthly_valuation_list
):
    """Combine shared fixtures for complete stock data setup."""
    yield {
        'basic_info': sample_basic_info,
        'daily_info': sample_daily_info,
        'income_sheet': sample_income_sheet,
        'monthly_valuation': sample_monthly_valuation_list
    }


@pytest.mark.skip(reason="requires screener_format.json which is not in repo")
@pytest.mark.usefixtures('app_context')
class TestStockScreenerManager:
    """Test suite for StockScreenerManager class."""

    def test_init_with_default_date(self, app_context):
        """Test StockScreenerManager initialization with default date."""
        screener = StockScreenerManager("test_screener_option")

        assert screener.option == "test_screener_option"
        assert screener.now is not None
        assert 'date' in screener.query_condition
        assert 'season' in screener.query_condition
        assert 'year' in screener.query_condition
        assert 'month' in screener.query_condition
        assert 'monthList' in screener.query_condition

    def test_init_with_custom_date(self, app_context):
        """Test StockScreenerManager initialization with custom date."""
        custom_date = datetime(2025, 8, 8)
        screener = StockScreenerManager("test_screener_option", custom_date)

        assert screener.now == custom_date
        assert screener.query_condition['date'] == '2025-08-08'
        assert screener.query_condition['month'] == 7  # (8-2)%12+1 = 7
        assert screener.query_condition['season'] == 2  # (ceil(8/3)-2)%4+1

    def test_get_screener_format_valid_option(self, app_context):
        """Test get_screener_format with valid option."""
        screener = StockScreenerManager("test_screener_option")

        assert screener.screener_format is not None
        assert 'sqlSyntax' in screener.screener_format
        assert 'title' in screener.screener_format
        assert 'content' in screener.screener_format

    def test_get_screener_format_invalid_option(self, app_context):
        """Test get_screener_format with invalid option."""
        with pytest.raises(KeyError) as exc_info:
            StockScreenerManager("invalid_option_12345")

        assert "Invalid screener option" in str(exc_info.value)

    def test_check_stock_valuation_valid_stock(self, complete_stock_data):
        """Test check_stock_valuation with a valid stock that passes all checks."""
        screener = StockScreenerManager("test_screener_option")
        result = screener.check_stock_valuation('2330')

        # This should pass because shared fixtures have:
        # - EPS (8.69) > 0.3 ✓
        # - core_business_ratio (41.67/43.33 = 0.96) > 0.7 ✓
        assert result is True

    def test_check_stock_valuation_nonexistent_stock(self, app_context):
        """Test check_stock_valuation with non-existent stock."""
        screener = StockScreenerManager("test_screener_option")
        result = screener.check_stock_valuation('9999')

        assert result is False

    def test_check_stock_valuation_missing_daily_info(
        self, sample_basic_info, sample_income_sheet, sample_monthly_valuation_list
    ):
        """Test check_stock_valuation when daily_information is missing."""
        screener = StockScreenerManager("test_screener_option")
        result = screener.check_stock_valuation(sample_basic_info.id)

        assert result is False

    def test_check_stock_valuation_low_eps(self, complete_stock_data):
        """Test check_stock_valuation with low EPS."""
        from app import db

        # Modify EPS to be below threshold
        income = complete_stock_data['income_sheet']
        original_eps = income.基本每股盈餘
        income.基本每股盈餘 = 0.2
        db.session.commit()

        screener = StockScreenerManager("test_screener_option")
        result = screener.check_stock_valuation('2330')

        assert result is False

        # Restore
        income.基本每股盈餘 = original_eps
        db.session.commit()

    def test_check_stock_valuation_low_core_business_ratio(self, complete_stock_data):
        """Test check_stock_valuation with low core business ratio."""
        from app import db

        # Modify ratios to make core_business_ratio low
        income = complete_stock_data['income_sheet']
        original_ratio = income.營業利益率
        income.營業利益率 = Decimal('5.0')  # ratio = 5/43.33 = 0.115 < 0.7
        db.session.commit()

        screener = StockScreenerManager("test_screener_option")
        result = screener.check_stock_valuation('2330')

        assert result is False

        # Restore
        income.營業利益率 = original_ratio
        db.session.commit()

    def test_save_recommended_stock_empty_list(self, app_context):
        """Test save_recommended_stock with empty stock list."""
        screener = StockScreenerManager("test_screener_option")
        result = screener.save_recommended_stock([])

        assert result == {"added": 0, "skipped": 0, "total": 0}

    def test_save_recommended_stock_new_stocks(self, complete_stock_data):
        """Test save_recommended_stock with new stocks."""
        from app import db

        screener = StockScreenerManager("test_screener_option")
        stocks = [('2330', '台積電', 500.0)]

        result = screener.save_recommended_stock(stocks)

        assert result['added'] == 1
        assert result['skipped'] == 0
        assert result['total'] == 1

        # Verify in database
        saved = RecommendedStock.query.filter_by(
            stock_id='2330',
            filter_model='test_screener_option'
        ).first()
        assert saved is not None

        # Cleanup
        db.session.delete(saved)
        db.session.commit()

    def test_save_recommended_stock_duplicate_stocks(self, complete_stock_data):
        """Test save_recommended_stock with duplicate stocks."""
        from app import db

        screener = StockScreenerManager("test_screener_option")
        stocks = [('2330', '台積電', 500.0)]

        # First save
        result1 = screener.save_recommended_stock(stocks)
        assert result1['added'] == 1

        # Second save (should skip)
        result2 = screener.save_recommended_stock(stocks)
        assert result2['added'] == 0
        assert result2['skipped'] == 1

        # Cleanup
        RecommendedStock.query.filter_by(
            stock_id='2330',
            filter_model='test_screener_option'
        ).delete()
        db.session.commit()

    def test_save_recommended_stock_bulk_insert(self, complete_stock_data, sample_basic_info_2):
        """Test save_recommended_stock with multiple stocks (bulk insert)."""
        from app import db

        screener = StockScreenerManager("test_screener_option")
        stocks = [
            ('2330', '台積電', 500.0),
            ('2317', '鴻海', 100.0)
        ]

        result = screener.save_recommended_stock(stocks)

        assert result['added'] == 2
        assert result['total'] == 2

        # Cleanup
        RecommendedStock.query.filter(
            RecommendedStock.stock_id.in_(['2330', '2317'])
        ).delete()
        db.session.commit()

    def test_get_recommended_stocks_default(self, complete_stock_data):
        """Test get_recommended_stocks with default parameters."""
        from app import db

        # Create test data
        rec = RecommendedStock(
            stock_id='2330',
            update_date=date.today(),
            filter_model='test_screener_option'
        )
        db.session.add(rec)
        db.session.commit()

        # Query
        results = StockScreenerManager.get_recommended_stocks()

        assert len(results) > 0
        assert any(r.stock_id == '2330' for r in results)

        # Cleanup
        db.session.delete(rec)
        db.session.commit()

    def test_get_recommended_stocks_with_filter_model(self, complete_stock_data):
        """Test get_recommended_stocks with specific filter model."""
        from app import db

        # Create test data with different filter models
        rec1 = RecommendedStock(
            stock_id='2330',
            update_date=date.today(),
            filter_model='test_screener_option'
        )
        rec2 = RecommendedStock(
            stock_id='2330',
            update_date=date.today(),
            filter_model='其他模型'
        )
        db.session.add_all([rec1, rec2])
        db.session.commit()

        # Query with filter
        results = StockScreenerManager.get_recommended_stocks(
            filter_model='test_screener_option'
        )

        assert all(r.filter_model == 'test_screener_option' for r in results)

        # Cleanup
        db.session.delete(rec1)
        db.session.delete(rec2)
        db.session.commit()

    def test_cleanup_old_recommendations(self, complete_stock_data):
        """Test cleanup_old_recommendations method."""
        from app import db

        # Create old and new recommendations
        old_date = date.today() - timedelta(days=100)
        recent_date = date.today() - timedelta(days=30)

        old_rec = RecommendedStock(
            stock_id='2330',
            update_date=old_date,
            filter_model='test_screener_option'
        )
        recent_rec = RecommendedStock(
            stock_id='2330',
            update_date=recent_date,
            filter_model='test_screener_option_recent'
        )
        db.session.add_all([old_rec, recent_rec])
        db.session.commit()

        # Cleanup records older than 90 days
        deleted = StockScreenerManager.cleanup_old_recommendations(days_to_keep=90)

        assert deleted >= 1

        # Verify old record is deleted
        assert RecommendedStock.query.filter_by(update_date=old_date).first() is None

        # Verify recent record still exists
        assert RecommendedStock.query.filter_by(update_date=recent_date).first() is not None

        # Cleanup
        RecommendedStock.query.filter_by(update_date=recent_date).delete()
        db.session.commit()

    def test_format_screener_message(self, app_context):
        """Test format_screener_message method."""
        screener = StockScreenerManager("test_screener_option")

        # Create sample stock data (tuples matching SQL result format)
        stocks = [
            ('2330', '台積電', 500.0, 1000000000),
            ('2317', '鴻海', 100.0, 500000000),
        ]

        messages = screener.format_screener_message(stocks)

        assert isinstance(messages, list)
        assert len(messages) > 0
        # First message should contain stock information
        assert '2330' in messages[0] or '台積電' in messages[0]

    def test_run_and_save_no_stocks(self, app_context):
        """Test run_and_save when no stocks are found."""
        # Using a filter that likely returns no results
        screener = StockScreenerManager("test_screener_option", datetime(2099, 1, 1))

        result = screener.run_and_save()

        assert result['messages'] == []
        assert result['save_stats']['total'] == 0
        # stock_count is not returned by run_and_save, total is in save_stats


@pytest.mark.skip(reason="requires screener_format.json which is not in repo")
@pytest.mark.usefixtures('app_context')
class TestStockScreenerIntegration:
    """Integration tests for complete workflow."""

    def test_complete_workflow(self, complete_stock_data):
        """Test the complete screener workflow end-to-end."""
        from app import db

        screener = StockScreenerManager("test_screener_option")

        # Test valuation check
        is_valid = screener.check_stock_valuation('2330')
        assert isinstance(is_valid, bool)

        # Test save (with mock data)
        if is_valid:
            stocks = [('2330', '台積電', 500.0)]
            result = screener.save_recommended_stock(stocks)
            assert result['total'] == 1

            # Cleanup
            RecommendedStock.query.filter_by(stock_id='2330').delete()
            db.session.commit()
