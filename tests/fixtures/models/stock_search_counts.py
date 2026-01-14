"""StockSearchCounts model fixtures for testing.

Architecture:
- Depends on sample_basic_info (which depends on app_context)
- Each fixture cleans up ONLY the records it creates
"""
import pytest
from app import db
from app.database_setup import StockSearchCounts


@pytest.fixture
def sample_stock_search_counts(sample_basic_info):
    """Create sample stock search counts for TSMC (2330).

    Depends on: sample_basic_info → app_context
    """
    search_counts = StockSearchCounts(
        stock_id=sample_basic_info.id,
        search_count=1000
    )
    db.session.add(search_counts)
    db.session.commit()

    yield search_counts

    # Explicit cleanup
    StockSearchCounts.query.filter_by(stock_id=sample_basic_info.id).delete()
    db.session.commit()
