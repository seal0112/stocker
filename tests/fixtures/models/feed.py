"""Feed model fixtures for testing."""
import logging
import pytest
from datetime import datetime
from sqlalchemy import text
from app import db
from app.models.feed import Feed

logger = logging.getLogger(__name__)


@pytest.fixture
def sample_feed(app_context, sample_basic_info):
    """Create a sample Feed record for testing.

    Note: Explicitly depends on app_context for proper cleanup.
    """
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
    feed_id = feed.id
    logger.info(f"[sample_feed] Created feed id={feed_id}")

    yield feed

    # Explicit cleanup using raw SQL to avoid SQLAlchemy session issues
    logger.info(f"[sample_feed] Teardown starting for feed id={feed_id}")
    try:
        db.session.execute(text("DELETE FROM announcement_income_sheet_analysis WHERE feed_id = :fid"), {"fid": feed_id})
        db.session.execute(text("DELETE FROM feed_feedTag WHERE feed_id = :fid"), {"fid": feed_id})
        db.session.execute(text("DELETE FROM feed WHERE id = :fid"), {"fid": feed_id})
        db.session.commit()
        logger.info(f"[sample_feed] Cleanup done for feed id={feed_id}")
    except Exception as e:
        logger.error(f"[sample_feed] Teardown error: {e}")
        db.session.rollback()
