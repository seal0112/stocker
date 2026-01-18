"""IncomeSheet model fixtures for testing."""
import pytest
from datetime import date
from decimal import Decimal
from app import db
from app.database_setup import IncomeSheet


@pytest.fixture
def sample_income_sheet(sample_basic_info):
    """Create sample income sheet for TSMC (2330).

    Note: Uses app context from sample_basic_info.
    Explicit cleanup in teardown.
    """
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

    # Explicit cleanup - delete what this fixture created
    IncomeSheet.query.filter_by(
        stock_id=sample_basic_info.id,
        year=2024,
        season='1'
    ).delete()
    db.session.commit()


@pytest.fixture
def sample_income_sheet_list(sample_basic_info):
    """Create multiple income sheets for different seasons.

    Note: Uses app context from sample_basic_info.
    Explicit cleanup in teardown.
    """
    income_sheets = []
    # Season to month mapping: Q1->5月, Q2->8月, Q3->11月, Q4->次年2月(簡化為12月)
    season_month = {'1': 5, '2': 8, '3': 11, '4': 12}
    for season in ['1', '2', '3', '4']:
        inc = IncomeSheet(
            stock_id=sample_basic_info.id,
            year=2023,
            season=season,
            update_date=date(2023, season_month[season], 15),
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

    # Explicit cleanup - delete what this fixture created
    IncomeSheet.query.filter_by(
        stock_id=sample_basic_info.id,
        year=2023
    ).delete()
    db.session.commit()
