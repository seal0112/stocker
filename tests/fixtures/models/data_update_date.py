"""DataUpdateDate model fixtures for testing.

Architecture:
- Depends on sample_basic_info (which depends on app_context)
- Each fixture cleans up ONLY the records it creates
"""
import pytest
from datetime import date
from app import db
from app.database_setup import DataUpdateDate


@pytest.fixture
def sample_data_update_date(sample_basic_info):
    """Create sample data update date for TSMC (2330).

    Depends on: sample_basic_info → app_context
    """
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

    # Explicit cleanup
    DataUpdateDate.query.filter_by(stock_id=sample_basic_info.id).delete()
    db.session.commit()
