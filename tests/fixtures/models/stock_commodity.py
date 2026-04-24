"""StockCommodity model fixtures for testing.

Architecture:
- Depends on sample_basic_info (which depends on app_context)
- Each fixture cleans up ONLY the records it creates
"""
import pytest
from app import db
from app.database_setup import StockCommodity


@pytest.fixture
def sample_stock_commodity(sample_basic_info):
    """Create sample stock commodity for TSMC (2330).

    Depends on: sample_basic_info → app_context
    """
    commodity = StockCommodity(
        stock_id=sample_basic_info.id,
        stock_future=True,
        stock_option=True,
        small_stock_future=True
    )
    db.session.add(commodity)
    db.session.commit()

    yield commodity

    # Explicit cleanup
    StockCommodity.query.filter_by(stock_id=sample_basic_info.id).delete()
    db.session.commit()


@pytest.fixture
def sample_stock_commodity_no_derivatives(sample_basic_info_2):
    """Create sample stock commodity without derivatives for Hon Hai (2317).

    Depends on: sample_basic_info_2 → app_context
    """
    commodity = StockCommodity(
        stock_id=sample_basic_info_2.id,
        stock_future=False,
        stock_option=False,
        small_stock_future=False
    )
    db.session.add(commodity)
    db.session.commit()

    yield commodity

    # Explicit cleanup
    StockCommodity.query.filter_by(stock_id=sample_basic_info_2.id).delete()
    db.session.commit()
