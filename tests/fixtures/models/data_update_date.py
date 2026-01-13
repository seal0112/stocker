"""DataUpdateDate model fixtures for testing."""
import pytest
from datetime import date
from app import db
from app.database_setup import DataUpdateDate


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
