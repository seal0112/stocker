"""StockSearchCounts model fixtures for testing."""
import pytest
from app import db
from app.database_setup import StockSearchCounts


@pytest.fixture
def sample_stock_search_counts(test_app, sample_basic_info):
    """Create sample stock search counts for TSMC (2330)."""
    with test_app.app_context():
        search_counts = StockSearchCounts(
            stock_id=sample_basic_info.id,
            search_count=1000
        )
        db.session.add(search_counts)
        db.session.commit()

        yield search_counts

        # Cleanup
        db.session.delete(search_counts)
        db.session.commit()
