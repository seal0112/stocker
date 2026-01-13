"""StockCommodity model fixtures for testing."""
import pytest
from app import db
from app.database_setup import StockCommodity


@pytest.fixture
def sample_stock_commodity(test_app, sample_basic_info):
    """Create sample stock commodity for TSMC (2330)."""
    with test_app.app_context():
        commodity = StockCommodity(
            stock_id=sample_basic_info.id,
            stock_future=True,
            stock_option=True,
            small_stock_future=True
        )
        db.session.add(commodity)
        db.session.commit()

        yield commodity

        # Cleanup
        db.session.delete(commodity)
        db.session.commit()


@pytest.fixture
def sample_stock_commodity_no_derivatives(test_app, sample_basic_info_2):
    """Create sample stock commodity without derivatives for Hon Hai (2317)."""
    with test_app.app_context():
        commodity = StockCommodity(
            stock_id=sample_basic_info_2.id,
            stock_future=False,
            stock_option=False,
            small_stock_future=False
        )
        db.session.add(commodity)
        db.session.commit()

        yield commodity

        # Cleanup
        db.session.delete(commodity)
        db.session.commit()
