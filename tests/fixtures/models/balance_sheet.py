"""BalanceSheet model fixtures for testing.

Architecture:
- Depends on sample_basic_info (which depends on app_context)
- Each fixture cleans up ONLY the records it creates
- Teardown runs before sample_basic_info teardown (pytest handles this)
"""
import pytest
from datetime import date
from app import db
from app.database_setup import BalanceSheet


@pytest.fixture
def sample_balance_sheet(sample_basic_info):
    """Create sample balance sheet for TSMC (2330).

    Depends on: sample_basic_info → app_context
    """
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

    # Explicit cleanup
    BalanceSheet.query.filter_by(
        stock_id=sample_basic_info.id,
        year=2024,
        season='1'
    ).delete()
    db.session.commit()


@pytest.fixture
def sample_balance_sheet_list(sample_basic_info):
    """Create multiple balance sheets for different seasons.

    Depends on: sample_basic_info → app_context
    """
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

    # Explicit cleanup
    BalanceSheet.query.filter_by(
        stock_id=sample_basic_info.id,
        year=2023
    ).delete()
    db.session.commit()
