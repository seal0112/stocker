"""MonthRevenue model fixtures for testing.

Architecture:
- Depends on sample_basic_info (which depends on app_context)
- Each fixture cleans up ONLY the records it creates
- Teardown runs before sample_basic_info teardown (pytest handles this)
"""
import pytest
from datetime import date
from app import db
from app.database_setup import MonthRevenue


@pytest.fixture
def sample_month_revenue(sample_basic_info):
    """Create sample month revenue for TSMC (2330).

    Depends on: sample_basic_info → app_context
    """
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

    # Explicit cleanup - only delete what this fixture created
    MonthRevenue.query.filter_by(
        stock_id=sample_basic_info.id,
        year=2024,
        month='3'
    ).delete()
    db.session.commit()


@pytest.fixture
def sample_month_revenue_list(sample_basic_info):
    """Create 12 months of revenue data for testing trends.

    Depends on: sample_basic_info → app_context
    """
    revenues = []
    base_revenue = 180000000000
    for month in range(1, 13):
        # For months 1-11, update_date is month+1 in the same year
        # For month 12, update_date is January next year
        if month <= 11:
            update = date(2024, month + 1, 10)
        else:
            update = date(2025, 1, 10)

        revenue = MonthRevenue(
            stock_id=sample_basic_info.id,
            year=2024,
            month=str(month),
            update_date=update,
            當月營收=base_revenue + month * 5000000000,
            去年當月營收=base_revenue - 10000000000,
            去年同月增減=((base_revenue + month * 5000000000) / (base_revenue - 10000000000) - 1) * 100
        )
        revenues.append(revenue)
        db.session.add(revenue)
    db.session.commit()

    yield revenues

    # Explicit cleanup - delete all 12 months created by this fixture
    MonthRevenue.query.filter_by(
        stock_id=sample_basic_info.id,
        year=2024
    ).delete()
    db.session.commit()
