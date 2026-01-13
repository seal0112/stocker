"""DailyInformation model fixtures for testing."""
import pytest
from datetime import date
from decimal import Decimal
from app import db
from app.database_setup import DailyInformation


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
