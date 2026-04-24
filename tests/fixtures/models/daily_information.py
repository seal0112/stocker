"""DailyInformation model fixtures for testing.

Architecture:
- Depends on sample_basic_info (which depends on app_context)
- Each fixture cleans up ONLY the records it creates
- Teardown runs before sample_basic_info teardown (pytest handles this)
"""
import pytest
from datetime import date
from decimal import Decimal
from app import db
from app.database_setup import DailyInformation


@pytest.fixture
def sample_daily_info(sample_basic_info):
    """Create sample daily information for TSMC (2330).

    Depends on: sample_basic_info → app_context
    """
    # Check if record already exists (from previous test or seed data)
    daily_info = DailyInformation.query.filter_by(stock_id=sample_basic_info.id).first()
    created = False

    if not daily_info:
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
        created = True

    yield daily_info

    # Explicit cleanup - only delete what this fixture created
    if created:
        DailyInformation.query.filter_by(stock_id=sample_basic_info.id).delete()
        db.session.commit()


@pytest.fixture
def sample_daily_info_2(sample_basic_info_2):
    """Create sample daily information for Hon Hai (2317).

    Depends on: sample_basic_info_2 → app_context
    """
    # Check if record already exists (from previous test or seed data)
    daily_info = DailyInformation.query.filter_by(stock_id=sample_basic_info_2.id).first()
    created = False

    if not daily_info:
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
        created = True

    yield daily_info

    # Explicit cleanup - only delete what this fixture created
    if created:
        DailyInformation.query.filter_by(stock_id=sample_basic_info_2.id).delete()
        db.session.commit()
