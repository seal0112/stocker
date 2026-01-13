"""BalanceSheet model fixtures for testing."""
import pytest
from datetime import date
from app import db
from app.database_setup import BalanceSheet


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
