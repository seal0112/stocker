"""Stock-related model fixtures for testing.

This module provides fixtures for all stock-related models:
- DailyInformation
- BalanceSheet
- IncomeSheet
- CashFlow
- MonthRevenue
- MonthlyValuation
- StockCommodity
- DataUpdateDate
- StockSearchCounts
- EarningsCall
- RecommendedStock
"""
import pytest
from datetime import date
from decimal import Decimal
from app import db
from app.database_setup import (
    DailyInformation,
    BalanceSheet,
    IncomeSheet,
    CashFlow,
    MonthRevenue,
    StockCommodity,
    DataUpdateDate,
    StockSearchCounts,
)
from app.monthly_valuation.models import MonthlyValuation
from app.earnings_call.models import EarningsCall
from app.models.recommended_stock import RecommendedStock


# =============================================================================
# DailyInformation Fixtures
# =============================================================================

@pytest.fixture
def sample_daily_info(test_app, sample_basic_info):
    """Create sample daily information for TSMC (2330)."""
    with test_app.app_context():
        daily_info = DailyInformation(
            stock_id=sample_basic_info.id,
            update_date=date(2024, 3, 15),
            本日收盤價=580.0,
            本日漲跌=5.0,
            近四季每股盈餘=32.5,
            本益比=Decimal('17.85'),
            殖利率=2.5,
            股價淨值比=4.8
        )
        db.session.add(daily_info)
        db.session.commit()

        yield daily_info

        # Cleanup
        db.session.delete(daily_info)
        db.session.commit()


@pytest.fixture
def sample_daily_info_2(test_app, sample_basic_info_2):
    """Create sample daily information for Hon Hai (2317)."""
    with test_app.app_context():
        daily_info = DailyInformation(
            stock_id=sample_basic_info_2.id,
            update_date=date(2024, 3, 15),
            本日收盤價=105.0,
            本日漲跌=-1.5,
            近四季每股盈餘=10.2,
            本益比=Decimal('10.29'),
            殖利率=5.3,
            股價淨值比=1.2
        )
        db.session.add(daily_info)
        db.session.commit()

        yield daily_info

        # Cleanup
        db.session.delete(daily_info)
        db.session.commit()


# =============================================================================
# BalanceSheet Fixtures
# =============================================================================

@pytest.fixture
def sample_balance_sheet(test_app, sample_basic_info):
    """Create sample balance sheet for TSMC (2330)."""
    with test_app.app_context():
        balance_sheet = BalanceSheet(
            stock_id=sample_basic_info.id,
            year=2024,
            season='1',
            update_date=date(2024, 5, 15),
            現金及約當現金=1500000000000,
            流動資產合計=2500000000000,
            非流動資產合計=4000000000000,
            資產總計=6500000000000,
            流動負債合計=800000000000,
            非流動負債合計=1200000000000,
            負債總計=2000000000000,
            股本合計=259000000000,
            保留盈餘合計=3500000000000,
            權益總計=4500000000000,
            負債及權益總計=6500000000000
        )
        db.session.add(balance_sheet)
        db.session.commit()

        yield balance_sheet

        # Cleanup
        db.session.delete(balance_sheet)
        db.session.commit()


@pytest.fixture
def sample_balance_sheet_list(test_app, sample_basic_info):
    """Create multiple balance sheets for different seasons."""
    with test_app.app_context():
        balance_sheets = []
        for season in ['1', '2', '3', '4']:
            bs = BalanceSheet(
                stock_id=sample_basic_info.id,
                year=2023,
                season=season,
                update_date=date(2023, int(season) * 3 + 2, 15),
                資產總計=6000000000000 + int(season) * 100000000000,
                負債總計=2000000000000,
                權益總計=4000000000000 + int(season) * 100000000000
            )
            balance_sheets.append(bs)
            db.session.add(bs)
        db.session.commit()

        yield balance_sheets

        # Cleanup
        for bs in balance_sheets:
            db.session.delete(bs)
        db.session.commit()


# =============================================================================
# IncomeSheet Fixtures
# =============================================================================

@pytest.fixture
def sample_income_sheet(test_app, sample_basic_info):
    """Create sample income sheet for TSMC (2330)."""
    with test_app.app_context():
        income_sheet = IncomeSheet(
            stock_id=sample_basic_info.id,
            year=2024,
            season='1',
            update_date=date(2024, 5, 15),
            營業收入合計=600000000000,
            營業成本合計=300000000000,
            營業毛利=300000000000,
            營業毛利率=Decimal('50.00'),
            營業費用=50000000000,
            營業費用率=Decimal('8.33'),
            營業利益=250000000000,
            營業利益率=Decimal('41.67'),
            稅前淨利=260000000000,
            稅前淨利率=Decimal('43.33'),
            本期淨利=230000000000,
            本期淨利率=Decimal('38.33'),
            母公司業主淨利=225000000000,
            基本每股盈餘=8.69,
            稀釋每股盈餘=8.65
        )
        db.session.add(income_sheet)
        db.session.commit()

        yield income_sheet

        # Cleanup
        db.session.delete(income_sheet)
        db.session.commit()


@pytest.fixture
def sample_income_sheet_list(test_app, sample_basic_info):
    """Create multiple income sheets for different seasons."""
    with test_app.app_context():
        income_sheets = []
        for season in ['1', '2', '3', '4']:
            inc = IncomeSheet(
                stock_id=sample_basic_info.id,
                year=2023,
                season=season,
                update_date=date(2023, int(season) * 3 + 2, 15),
                營業收入合計=550000000000 + int(season) * 10000000000,
                營業毛利=275000000000,
                營業毛利率=Decimal('50.00'),
                營業利益=220000000000,
                營業利益率=Decimal('40.00'),
                本期淨利=200000000000,
                基本每股盈餘=7.72 + float(season) * 0.2
            )
            income_sheets.append(inc)
            db.session.add(inc)
        db.session.commit()

        yield income_sheets

        # Cleanup
        for inc in income_sheets:
            db.session.delete(inc)
        db.session.commit()


# =============================================================================
# CashFlow Fixtures
# =============================================================================

@pytest.fixture
def sample_cash_flow(test_app, sample_basic_info):
    """Create sample cash flow for TSMC (2330)."""
    with test_app.app_context():
        cash_flow = CashFlow(
            stock_id=sample_basic_info.id,
            year=2024,
            season='1',
            update_date=date(2024, 5, 15),
            本期稅前淨利淨損=260000000000,
            折舊費用=150000000000,
            攤銷費用=5000000000,
            營業活動之淨現金流入流出=400000000000,
            投資活動之淨現金流入流出=-350000000000,
            籌資活動之淨現金流入流出=-50000000000,
            期初現金及約當現金餘額=1500000000000,
            期末現金及約當現金餘額=1500000000000,
            本期現金及約當現金增加減少數=0
        )
        db.session.add(cash_flow)
        db.session.commit()

        yield cash_flow

        # Cleanup
        db.session.delete(cash_flow)
        db.session.commit()


# =============================================================================
# MonthRevenue Fixtures
# =============================================================================

@pytest.fixture
def sample_month_revenue(test_app, sample_basic_info):
    """Create sample month revenue for TSMC (2330)."""
    with test_app.app_context():
        month_revenue = MonthRevenue(
            stock_id=sample_basic_info.id,
            year=2024,
            month='3',
            update_date=date(2024, 4, 10),
            當月營收=200000000000,
            上月營收=195000000000,
            去年當月營收=180000000000,
            上月比較增減=2.56,
            去年同月增減=11.11,
            當月累計營收=585000000000,
            去年累計營收=520000000000,
            前期比較增減=12.5
        )
        db.session.add(month_revenue)
        db.session.commit()

        yield month_revenue

        # Cleanup
        db.session.delete(month_revenue)
        db.session.commit()


@pytest.fixture
def sample_month_revenue_list(test_app, sample_basic_info):
    """Create multiple month revenues for testing trends."""
    with test_app.app_context():
        revenues = []
        base_revenue = 180000000000
        for month in range(1, 7):
            revenue = MonthRevenue(
                stock_id=sample_basic_info.id,
                year=2024,
                month=str(month),
                update_date=date(2024, month + 1, 10),
                當月營收=base_revenue + month * 5000000000,
                去年當月營收=base_revenue - 10000000000,
                去年同月增減=((base_revenue + month * 5000000000) / (base_revenue - 10000000000) - 1) * 100
            )
            revenues.append(revenue)
            db.session.add(revenue)
        db.session.commit()

        yield revenues

        # Cleanup
        for rev in revenues:
            db.session.delete(rev)
        db.session.commit()


# =============================================================================
# MonthlyValuation Fixtures
# =============================================================================

@pytest.fixture
def sample_monthly_valuation(test_app, sample_basic_info):
    """Create sample monthly valuation for TSMC (2330)."""
    with test_app.app_context():
        valuation = MonthlyValuation(
            stock_id=sample_basic_info.id,
            year=2024,
            month='3',
            本益比=Decimal('18.50'),
            淨值比=Decimal('4.80'),
            殖利率=Decimal('2.50'),
            均價=Decimal('575.00')
        )
        db.session.add(valuation)
        db.session.commit()

        yield valuation

        # Cleanup
        db.session.delete(valuation)
        db.session.commit()


@pytest.fixture
def sample_monthly_valuation_list(test_app, sample_basic_info):
    """Create multiple monthly valuations for testing historical data."""
    with test_app.app_context():
        valuations = []
        for month in range(1, 13):
            val = MonthlyValuation(
                stock_id=sample_basic_info.id,
                year=2023,
                month=str(month),
                本益比=Decimal('15.00') + Decimal(str(month * 0.5)),
                淨值比=Decimal('4.00') + Decimal(str(month * 0.1)),
                殖利率=Decimal('3.00') - Decimal(str(month * 0.05)),
                均價=Decimal('500.00') + Decimal(str(month * 10))
            )
            valuations.append(val)
            db.session.add(val)
        db.session.commit()

        yield valuations

        # Cleanup
        for val in valuations:
            db.session.delete(val)
        db.session.commit()


# =============================================================================
# StockCommodity Fixtures
# =============================================================================

@pytest.fixture
def sample_stock_commodity(test_app, sample_basic_info):
    """Create sample stock commodity for TSMC (2330)."""
    with test_app.app_context():
        commodity = StockCommodity(
            stock_id=sample_basic_info.id,
            stock_future=True,
            stock_option=True,
            small_stock_future=True
        )
        db.session.add(commodity)
        db.session.commit()

        yield commodity

        # Cleanup
        db.session.delete(commodity)
        db.session.commit()


@pytest.fixture
def sample_stock_commodity_no_derivatives(test_app, sample_basic_info_2):
    """Create sample stock commodity without derivatives for Hon Hai (2317)."""
    with test_app.app_context():
        commodity = StockCommodity(
            stock_id=sample_basic_info_2.id,
            stock_future=False,
            stock_option=False,
            small_stock_future=False
        )
        db.session.add(commodity)
        db.session.commit()

        yield commodity

        # Cleanup
        db.session.delete(commodity)
        db.session.commit()


# =============================================================================
# DataUpdateDate Fixtures
# =============================================================================

@pytest.fixture
def sample_data_update_date(test_app, sample_basic_info):
    """Create sample data update date for TSMC (2330)."""
    with test_app.app_context():
        update_date = DataUpdateDate(
            stock_id=sample_basic_info.id,
            month_revenue_last_update=date(2024, 4, 10),
            announcement_last_update=date(2024, 3, 15),
            news_last_update=date(2024, 3, 20),
            income_sheet_last_update=date(2024, 5, 15),
            earnings_call_last_update=date(2024, 3, 10)
        )
        db.session.add(update_date)
        db.session.commit()

        yield update_date

        # Cleanup
        db.session.delete(update_date)
        db.session.commit()


# =============================================================================
# StockSearchCounts Fixtures
# =============================================================================

@pytest.fixture
def sample_stock_search_counts(test_app, sample_basic_info):
    """Create sample stock search counts for TSMC (2330)."""
    with test_app.app_context():
        search_counts = StockSearchCounts(
            stock_id=sample_basic_info.id,
            search_count=1000
        )
        db.session.add(search_counts)
        db.session.commit()

        yield search_counts

        # Cleanup
        db.session.delete(search_counts)
        db.session.commit()


# =============================================================================
# EarningsCall Fixtures
# =============================================================================

@pytest.fixture
def sample_earnings_call(test_app, sample_basic_info):
    """Create sample earnings call for TSMC (2330)."""
    with test_app.app_context():
        earnings_call = EarningsCall(
            stock_id=sample_basic_info.id,
            meeting_date=date(2024, 4, 18),
            meeting_end_date=date(2024, 4, 18),
            location='台北市中山區松江路',
            description='2024年第一季法人說明會',
            file_name_chinese='2330_2024Q1法說會'
        )
        db.session.add(earnings_call)
        db.session.commit()

        yield earnings_call

        # Cleanup
        db.session.delete(earnings_call)
        db.session.commit()


@pytest.fixture
def sample_earnings_call_list(test_app, sample_basic_info):
    """Create multiple earnings calls for testing."""
    with test_app.app_context():
        calls = []
        for quarter in range(1, 5):
            call = EarningsCall(
                stock_id=sample_basic_info.id,
                meeting_date=date(2023, quarter * 3 + 1, 18),
                meeting_end_date=date(2023, quarter * 3 + 1, 18),
                location='台北市中山區松江路',
                description=f'2023年第{quarter}季法人說明會',
                file_name_chinese=f'2330_2023Q{quarter}法說會'
            )
            calls.append(call)
            db.session.add(call)
        db.session.commit()

        yield calls

        # Cleanup
        for call in calls:
            db.session.delete(call)
        db.session.commit()


# =============================================================================
# RecommendedStock Fixtures
# =============================================================================

@pytest.fixture
def sample_recommended_stock(test_app, sample_basic_info):
    """Create sample recommended stock for TSMC (2330)."""
    with test_app.app_context():
        recommended = RecommendedStock(
            stock_id=sample_basic_info.id,
            update_date=date(2024, 3, 15),
            filter_model='value_investing'
        )
        db.session.add(recommended)
        db.session.commit()

        yield recommended

        # Cleanup
        db.session.delete(recommended)
        db.session.commit()


@pytest.fixture
def sample_recommended_stock_list(test_app, sample_basic_info_list):
    """Create multiple recommended stocks for different filter models."""
    with test_app.app_context():
        recommended_list = []
        filter_models = ['value_investing', 'growth_investing', 'dividend_investing']

        for stock in sample_basic_info_list:
            for model in filter_models:
                recommended = RecommendedStock(
                    stock_id=stock.id,
                    update_date=date(2024, 3, 15),
                    filter_model=model
                )
                recommended_list.append(recommended)
                db.session.add(recommended)
        db.session.commit()

        yield recommended_list

        # Cleanup
        for rec in recommended_list:
            db.session.delete(rec)
        db.session.commit()
