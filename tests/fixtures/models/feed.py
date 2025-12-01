"""Feed model fixtures for testing."""
import pytest
from datetime import datetime
from app.models.feed import Feed


@pytest.fixture
def sample_feed(test_app, sample_basic_info):
    """Create a sample Feed record for testing."""
    with test_app.app_context():
        from app import db

        feed = Feed(
            stock_id=sample_basic_info.id,
            releaseTime=datetime(2024, 3, 15, 10, 30, 0),
            title='測試公告',
            link='https://example.com/feed/test123',
            source='mops',
            description='測試描述',
            feedType='announcement'
        )
        db.session.add(feed)
        db.session.commit()

        yield feed

        # Cleanup
        db.session.delete(feed)
        db.session.commit()
