"""MonthlyValuation model fixtures for testing."""
import pytest
from datetime import date
from decimal import Decimal
from app import db
from app.monthly_valuation.models import MonthlyValuation


@pytest.fixture
def sample_monthly_valuation(test_app, sample_basic_info):
    """Create sample monthly valuation for TSMC (2330)."""
    with test_app.app_context():
        valuation = MonthlyValuation(
            stock_id=sample_basic_info.id,
            year=2024,
            month='3',
            本益比=Decimal('18.50'),
            淨值比=Decimal('4.80'),
            殖利率=Decimal('2.50'),
            均價=Decimal('575.00')
        )
        db.session.add(valuation)
        db.session.commit()

        yield valuation

        # Cleanup
        db.session.delete(valuation)
        db.session.commit()


@pytest.fixture
def sample_monthly_valuation_list(test_app, sample_basic_info):
    """Create multiple monthly valuations for testing historical data."""
    with test_app.app_context():
        valuations = []
        for month in range(1, 13):
            val = MonthlyValuation(
                stock_id=sample_basic_info.id,
                year=2023,
                month=str(month),
                本益比=Decimal('15.00') + Decimal(str(month * 0.5)),
                淨值比=Decimal('4.00') + Decimal(str(month * 0.1)),
                殖利率=Decimal('3.00') - Decimal(str(month * 0.05)),
                均價=Decimal('500.00') + Decimal(str(month * 10))
            )
            valuations.append(val)
            db.session.add(val)
        db.session.commit()

        yield valuations

        # Cleanup
        for val in valuations:
            db.session.delete(val)
        db.session.commit()
