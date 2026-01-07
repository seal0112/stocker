"""FeedTag model fixtures for testing."""
import pytest
from app import db
from app.models.feed_tag import FeedTag
from app.models.feed_feed_tag import FeedFeedTag


@pytest.fixture(scope='module')
def sample_feed_tag_earnings(test_app):
    """Create a sample earnings feed tag."""
    tag = FeedTag.query.filter_by(name='earnings').first()
    if not tag:
        tag = FeedTag(name='earnings')
        db.session.add(tag)
        db.session.commit()

    yield tag


@pytest.fixture(scope='module')
def sample_feed_tag_dividend(test_app):
    """Create a sample dividend feed tag."""
    tag = FeedTag.query.filter_by(name='dividend').first()
    if not tag:
        tag = FeedTag(name='dividend')
        db.session.add(tag)
        db.session.commit()

    yield tag


@pytest.fixture(scope='module')
def sample_feed_tag_announcement(test_app):
    """Create a sample announcement feed tag."""
    tag = FeedTag.query.filter_by(name='announcement').first()
    if not tag:
        tag = FeedTag(name='announcement')
        db.session.add(tag)
        db.session.commit()

    yield tag


@pytest.fixture(scope='module')
def sample_feed_tag_news(test_app):
    """Create a sample news feed tag."""
    tag = FeedTag.query.filter_by(name='news').first()
    if not tag:
        tag = FeedTag(name='news')
        db.session.add(tag)
        db.session.commit()

    yield tag


@pytest.fixture
def sample_feed_with_tags(test_app, sample_feed, sample_feed_tag_earnings, sample_feed_tag_dividend):
    """Create a feed with multiple tags."""
    # Create FeedFeedTag associations
    feed_tag_1 = FeedFeedTag(
        feed_id=sample_feed.id,
        feedTag=sample_feed_tag_earnings.id
    )
    feed_tag_2 = FeedFeedTag(
        feed_id=sample_feed.id,
        feedTag=sample_feed_tag_dividend.id
    )

    db.session.add(feed_tag_1)
    db.session.add(feed_tag_2)
    db.session.commit()

    yield sample_feed, [sample_feed_tag_earnings, sample_feed_tag_dividend]

    # Cleanup
    db.session.delete(feed_tag_1)
    db.session.delete(feed_tag_2)
    db.session.commit()
