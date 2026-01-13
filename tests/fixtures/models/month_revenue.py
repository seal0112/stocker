"""MonthRevenue model fixtures for testing."""
import pytest
from datetime import date
from app import db
from app.database_setup import MonthRevenue


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
