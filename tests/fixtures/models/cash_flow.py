"""CashFlow model fixtures for testing.

Architecture:
- Depends on sample_basic_info (which depends on app_context)
- Each fixture cleans up ONLY the records it creates
- Teardown runs before sample_basic_info teardown (pytest handles this)
"""
import pytest
from datetime import date
from app import db
from app.database_setup import CashFlow


@pytest.fixture
def sample_cash_flow(sample_basic_info):
    """Create sample cash flow for TSMC (2330).

    Depends on: sample_basic_info → app_context
    """
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

    # Explicit cleanup
    CashFlow.query.filter_by(
        stock_id=sample_basic_info.id,
        year=2024,
        season='1'
    ).delete()
    db.session.commit()
