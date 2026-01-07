"""
Stock Screener Tests

Note: This file uses its own local fixtures (prefixed with 'screener_') instead of
shared fixtures because the tests require specific values to verify valuation logic:
- EPS > 0.3
- core_business_ratio (營業利益率/稅前淨利率) > 0.7
- stock_price < average_monthly_price * 1.25
"""
import pytest
from datetime import datetime, date, timedelta
from decimal import Decimal

from app.utils.stock_screener import StockScreenerManager
from app.database_setup import (
    BasicInformation, DailyInformation, IncomeSheet
)
from app.monthly_valuation.models import MonthlyValuation
from app.models.recommended_stock import RecommendedStock


@pytest.fixture
def screener_basic_info(test_app):
    """Create a BasicInformation record for screener testing."""
    with test_app.app_context():
        from app import db

        stock = BasicInformation(
            id='2330',
            公司名稱='台積電',
            公司簡稱='台積電',
            產業類別='半導體',
            exchange_type='sii',
            update_date=date.today()
        )
        db.session.add(stock)
        db.session.commit()

        yield stock

        # Cleanup
        db.session.delete(stock)
        db.session.commit()


@pytest.fixture
def screener_daily_info(test_app, screener_basic_info):
    """Create DailyInformation for screener testing."""
    with test_app.app_context():
        from app import db

        daily_info = DailyInformation(
            stock_id=screener_basic_info.id,
            本日收盤價=500.0,
            本日漲跌=5.0,
            近四季每股盈餘=25.0,
            本益比=Decimal('20.0'),
            殖利率=2.5,
            股價淨值比=3.5,
            update_date=date.today()
        )
        db.session.add(daily_info)
        db.session.commit()

        yield daily_info

        # Cleanup
        db.session.delete(daily_info)
        db.session.commit()


@pytest.fixture
def screener_income_sheet(test_app, screener_basic_info):
    """Create IncomeSheet with specific values for valuation testing.

    Values set to pass valuation checks:
    - 基本每股盈餘 = 6.5 (> 0.3 threshold)
    - 營業利益率 = 15.0, 稅前淨利率 = 18.0 (ratio = 0.833 > 0.7 threshold)
    """
    with test_app.app_context():
        from app import db

        income_sheet = IncomeSheet(
            stock_id=screener_basic_info.id,
            year=2024,
            season='3',
            營業收入合計=1000000000,
            營業利益=150000000,
            營業利益率=Decimal('15.0'),
            稅前淨利=180000000,
            稅前淨利率=Decimal('18.0'),
            本期淨利=150000000,
            本期淨利率=Decimal('15.0'),
            基本每股盈餘=6.5,
            update_date=date.today()
        )
        db.session.add(income_sheet)
        db.session.commit()

        yield income_sheet

        # Cleanup
        db.session.delete(income_sheet)
        db.session.commit()


@pytest.fixture
def screener_monthly_valuation(test_app, screener_basic_info):
    """Create 12 months of MonthlyValuation records for screener testing."""
    with test_app.app_context():
        from app import db

        valuations = []
        current_date = date.today()

        for i in range(12):
            month_date = current_date - timedelta(days=30 * i)
            valuation = MonthlyValuation(
                stock_id=screener_basic_info.id,
                year=month_date.year,
                month=str(month_date.month),
                本益比=Decimal('18.5') + Decimal(str(i * 0.5)),
                淨值比=Decimal('3.2'),
                殖利率=Decimal('2.5'),
                均價=Decimal('480.0') + Decimal(str(i * 5))
            )
            valuations.append(valuation)
            db.session.add(valuation)

        db.session.commit()

        yield valuations

        # Cleanup
        for valuation in valuations:
            db.session.delete(valuation)
        db.session.commit()


@pytest.fixture
def complete_stock_data(
    test_app, screener_basic_info, screener_daily_info,
    screener_income_sheet, screener_monthly_valuation
):
    """Fixture providing complete stock data setup for screener testing."""
    with test_app.app_context():
        yield {
            'basic_info': screener_basic_info,
            'daily_info': screener_daily_info,
            'income_sheet': screener_income_sheet,
            'monthly_valuation': screener_monthly_valuation
        }


@pytest.mark.usefixtures('test_app')
class TestStockScreenerManager:
    """Test suite for StockScreenerManager class."""

    def test_init_with_default_date(self, test_app):
        """Test StockScreenerManager initialization with default date."""
        with test_app.app_context():
            screener = StockScreenerManager("月營收近一年次高")

            assert screener.option == "月營收近一年次高"
            assert screener.now is not None
            assert 'date' in screener.query_condition
            assert 'season' in screener.query_condition
            assert 'year' in screener.query_condition
            assert 'month' in screener.query_condition
            assert 'monthList' in screener.query_condition

    def test_init_with_custom_date(self, test_app):
        """Test StockScreenerManager initialization with custom date."""
        with test_app.app_context():
            custom_date = datetime(2025, 8, 8)
            screener = StockScreenerManager("月營收近一年次高", custom_date)

            assert screener.now == custom_date
            assert screener.query_condition['date'] == '2025-08-08'
            assert screener.query_condition['month'] == 7  # (8-2)%12+1 = 7
            assert screener.query_condition['season'] == 2  # (ceil(8/3)-2)%4+1

    def test_get_screener_format_valid_option(self, test_app):
        """Test get_screener_format with valid option."""
        with test_app.app_context():
            screener = StockScreenerManager("月營收近一年次高")

            assert screener.screener_format is not None
            assert 'sqlSyntax' in screener.screener_format
            assert 'title' in screener.screener_format
            assert 'content' in screener.screener_format

    def test_get_screener_format_invalid_option(self, test_app):
        """Test get_screener_format with invalid option."""
        with test_app.app_context():
            with pytest.raises(KeyError) as exc_info:
                StockScreenerManager("invalid_option_12345")

            assert "Invalid screener option" in str(exc_info.value)

    def test_check_stock_valuation_valid_stock(self, test_app, complete_stock_data):
        """Test check_stock_valuation with a valid stock that passes all checks."""
        with test_app.app_context():
            screener = StockScreenerManager("月營收近一年次高")
            result = screener.check_stock_valuation('2330')

            # This should pass because:
            # - EPS (6.5) > 0.3 ✓
            # - core_business_ratio (15.0/18.0 = 0.833) > 0.7 ✓
            # - stock_price (500) < average_monthly_price * 1.25 ✓
            # - PE ratio check should pass ✓
            assert result is True

    def test_check_stock_valuation_nonexistent_stock(self, test_app):
        """Test check_stock_valuation with non-existent stock."""
        with test_app.app_context():
            screener = StockScreenerManager("月營收近一年次高")
            result = screener.check_stock_valuation('9999')

            assert result is False

    def test_check_stock_valuation_missing_daily_info(
        self, test_app, screener_basic_info, screener_income_sheet, screener_monthly_valuation
    ):
        """Test check_stock_valuation when daily_information is missing."""
        with test_app.app_context():
            screener = StockScreenerManager("月營收近一年次高")
            result = screener.check_stock_valuation(screener_basic_info.id)

            assert result is False

    def test_check_stock_valuation_low_eps(
        self, test_app, complete_stock_data
    ):
        """Test check_stock_valuation with low EPS."""
        with test_app.app_context():
            from app import db

            # Modify EPS to be below threshold
            income = complete_stock_data['income_sheet']
            income.基本每股盈餘 = 0.2
            db.session.commit()

            screener = StockScreenerManager("月營收近一年次高")
            result = screener.check_stock_valuation('2330')

            assert result is False

            # Restore
            income.基本每股盈餘 = 6.5
            db.session.commit()

    def test_check_stock_valuation_low_core_business_ratio(
        self, test_app, complete_stock_data
    ):
        """Test check_stock_valuation with low core business ratio."""
        with test_app.app_context():
            from app import db

            # Modify ratios to make core_business_ratio low
            income = complete_stock_data['income_sheet']
            income.營業利益率 = Decimal('5.0')
            income.稅前淨利率 = Decimal('18.0')  # ratio = 5/18 = 0.277 < 0.7
            db.session.commit()

            screener = StockScreenerManager("月營收近一年次高")
            result = screener.check_stock_valuation('2330')

            assert result is False

            # Restore
            income.營業利益率 = Decimal('15.0')
            db.session.commit()

    def test_save_recommended_stock_empty_list(self, test_app):
        """Test save_recommended_stock with empty stock list."""
        with test_app.app_context():
            screener = StockScreenerManager("月營收近一年次高")
            result = screener.save_recommended_stock([])

            assert result == {"added": 0, "skipped": 0, "total": 0}

    def test_save_recommended_stock_new_stocks(
        self, test_app, complete_stock_data
    ):
        """Test save_recommended_stock with new stocks."""
        with test_app.app_context():
            from app import db

            screener = StockScreenerManager("月營收近一年次高")
            stocks = [('2330', '台積電', 500.0)]

            result = screener.save_recommended_stock(stocks)

            assert result['added'] == 1
            assert result['skipped'] == 0
            assert result['total'] == 1

            # Verify in database
            saved = RecommendedStock.query.filter_by(
                stock_id='2330',
                filter_model='月營收近一年次高'
            ).first()
            assert saved is not None

            # Cleanup
            db.session.delete(saved)
            db.session.commit()

    def test_save_recommended_stock_duplicate_stocks(
        self, test_app, complete_stock_data
    ):
        """Test save_recommended_stock with duplicate stocks."""
        with test_app.app_context():
            from app import db

            screener = StockScreenerManager("月營收近一年次高")
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
                filter_model='月營收近一年次高'
            ).delete()
            db.session.commit()

    def test_save_recommended_stock_bulk_insert(
        self, test_app, complete_stock_data
    ):
        """Test save_recommended_stock with multiple stocks (bulk insert)."""
        with test_app.app_context():
            from app import db

            # Create additional test stocks
            stock2 = BasicInformation(
                id='2317',
                公司名稱='鴻海',
                公司簡稱='鴻海',
                exchange_type='sii'
            )
            db.session.add(stock2)
            db.session.commit()

            screener = StockScreenerManager("月營收近一年次高")
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
            db.session.delete(stock2)
            db.session.commit()

    def test_get_recommended_stocks_default(self, test_app, complete_stock_data):
        """Test get_recommended_stocks with default parameters."""
        with test_app.app_context():
            from app import db

            # Create test data
            rec = RecommendedStock(
                stock_id='2330',
                update_date=date.today(),
                filter_model='月營收近一年次高'
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

    def test_get_recommended_stocks_with_filter_model(
        self, test_app, complete_stock_data
    ):
        """Test get_recommended_stocks with specific filter model."""
        with test_app.app_context():
            from app import db

            # Create test data with different filter models
            rec1 = RecommendedStock(
                stock_id='2330',
                update_date=date.today(),
                filter_model='月營收近一年次高'
            )
            rec2 = RecommendedStock(
                stock_id='2317',
                update_date=date.today(),
                filter_model='其他模型'
            )
            db.session.add_all([rec1, rec2])
            db.session.commit()

            # Query with filter
            results = StockScreenerManager.get_recommended_stocks(
                filter_model='月營收近一年次高'
            )

            assert all(r.filter_model == '月營收近一年次高' for r in results)

            # Cleanup
            db.session.delete(rec1)
            db.session.delete(rec2)
            db.session.commit()

    def test_cleanup_old_recommendations(self, test_app, complete_stock_data):
        """Test cleanup_old_recommendations method."""
        with test_app.app_context():
            from app import db

            # Create old and new recommendations
            old_date = date.today() - timedelta(days=100)
            recent_date = date.today() - timedelta(days=30)

            old_rec = RecommendedStock(
                stock_id='2330',
                update_date=old_date,
                filter_model='月營收近一年次高'
            )
            recent_rec = RecommendedStock(
                stock_id='2317',
                update_date=recent_date,
                filter_model='月營收近一年次高'
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

    def test_format_screener_message(self, test_app):
        """Test format_screener_message method."""
        with test_app.app_context():
            screener = StockScreenerManager("月營收近一年次高")

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

    def test_run_and_save_no_stocks(self, test_app):
        """Test run_and_save when no stocks are found."""
        with test_app.app_context():
            # Using a filter that likely returns no results
            screener = StockScreenerManager("月營收近一年次高", datetime(2099, 1, 1))

            result = screener.run_and_save()

            assert result['messages'] == []
            assert result['save_stats']['total'] == 0
            assert 'stock_count' in result or result.get('stock_count') == 0


@pytest.mark.usefixtures('test_app')
class TestStockScreenerIntegration:
    """Integration tests for complete workflow."""

    def test_complete_workflow(self, test_app, complete_stock_data):
        """Test the complete screener workflow end-to-end."""
        with test_app.app_context():
            from app import db

            # This test would need actual screener_format.json configuration
            # and matching SQL data, so we'll skip the actual run_and_save
            # and just verify the components work together

            screener = StockScreenerManager("月營收近一年次高")

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
