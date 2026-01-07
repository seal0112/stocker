"""Unit tests for Feed and FeedTag models."""
import pytest
from datetime import datetime, date
from sqlalchemy.exc import IntegrityError

from app import db
from app.models.feed import Feed
from app.models.feed_tag import FeedTag
from app.models.feed_feed_tag import FeedFeedTag
from app.database_setup import BasicInformation


class TestFeedModel:
    """Tests for Feed model basic functionality."""

    def test_instance_creation(self, test_app):
        """Test Feed instance creation with all fields."""
        feed = Feed(
            stock_id="2330",
            update_date=date(2024, 3, 15),
            releaseTime=datetime(2024, 3, 15, 10, 30, 0),
            title="Test Announcement",
            link="https://example.com/feed/123",
            source="mops",
            description="Test description",
            feedType="announcement"
        )

        assert feed.stock_id == "2330"
        assert feed.title == "Test Announcement"
        assert feed.link == "https://example.com/feed/123"
        assert feed.source == "mops"
        assert feed.description == "Test description"
        assert feed.feedType == "announcement"

    def test_instance_creation_news_type(self, test_app):
        """Test Feed instance creation with news feedType."""
        feed = Feed(
            releaseTime=datetime(2024, 3, 15, 10, 30, 0),
            title="Test News",
            link="https://example.com/news/123",
            feedType="news"
        )

        assert feed.feedType == "news"

    def test_serialize_property(self, test_app):
        """Test serialize property returns all fields."""
        feed = Feed(
            stock_id="2330",
            releaseTime=datetime(2024, 3, 15, 10, 30, 0),
            title="Test Feed",
            link="https://example.com/feed/123",
            source="mops",
            feedType="announcement"
        )

        serialized = feed.serialize

        assert serialized["stock_id"] == "2330"
        assert serialized["title"] == "Test Feed"
        assert serialized["link"] == "https://example.com/feed/123"
        assert serialized["feedType"] == "announcement"
        assert "tags" in serialized
        assert "_sa_instance_state" not in serialized

    def test_serialize_includes_tags(self, test_app, sample_feed_with_tags):
        """Test serialize property includes tag names."""
        with test_app.app_context():
            feed, tags = sample_feed_with_tags
            serialized = feed.serialize

            assert "tags" in serialized
            assert isinstance(serialized["tags"], list)

    def test_getitem_method(self, test_app):
        """Test __getitem__ allows dictionary-style access."""
        feed = Feed(
            title="Test Feed",
            link="https://example.com/feed/123"
        )

        assert feed["title"] == "Test Feed"
        assert feed["link"] == "https://example.com/feed/123"

    def test_setitem_method(self, test_app):
        """Test __setitem__ allows dictionary-style assignment."""
        feed = Feed()

        feed["title"] = "New Title"
        feed["link"] = "https://example.com/new"

        assert feed.title == "New Title"
        assert feed.link == "https://example.com/new"


class TestFeedDatabaseOperations:
    """Tests for Feed database CRUD operations."""

    def test_create_feed(self, test_app, sample_basic_info):
        """Test creating a Feed record in database."""
        with test_app.app_context():
            feed = Feed(
                stock_id=sample_basic_info.id,
                releaseTime=datetime(2024, 3, 20, 14, 0, 0),
                title="Database Test Feed",
                link="https://example.com/feed/db-test",
                source="mops",
                feedType="announcement"
            )
            db.session.add(feed)
            db.session.commit()

            assert feed.id is not None

            # Verify in database
            saved = Feed.query.filter_by(id=feed.id).first()
            assert saved is not None
            assert saved.title == "Database Test Feed"

            # Cleanup
            db.session.delete(saved)
            db.session.commit()

    def test_read_feed(self, test_app, sample_feed):
        """Test reading Feed from database."""
        with test_app.app_context():
            feed = Feed.query.filter_by(id=sample_feed.id).first()

            assert feed is not None
            assert feed.title == sample_feed.title
            assert feed.link == sample_feed.link

    def test_update_feed(self, test_app, sample_basic_info):
        """Test updating Feed record."""
        with test_app.app_context():
            # Create
            feed = Feed(
                stock_id=sample_basic_info.id,
                releaseTime=datetime(2024, 3, 21, 10, 0, 0),
                title="Original Title",
                link="https://example.com/feed/update-test",
                feedType="announcement"
            )
            db.session.add(feed)
            db.session.commit()

            # Update
            feed.title = "Updated Title"
            feed.description = "Added description"
            db.session.commit()

            # Verify
            updated = Feed.query.filter_by(id=feed.id).first()
            assert updated.title == "Updated Title"
            assert updated.description == "Added description"

            # Cleanup
            db.session.delete(updated)
            db.session.commit()

    def test_delete_feed(self, test_app, sample_basic_info):
        """Test deleting Feed record."""
        with test_app.app_context():
            # Create
            feed = Feed(
                stock_id=sample_basic_info.id,
                releaseTime=datetime(2024, 3, 22, 10, 0, 0),
                title="Delete Test Feed",
                link="https://example.com/feed/delete-test",
                feedType="announcement"
            )
            db.session.add(feed)
            db.session.commit()
            feed_id = feed.id

            # Delete
            db.session.delete(feed)
            db.session.commit()

            # Verify
            deleted = Feed.query.filter_by(id=feed_id).first()
            assert deleted is None


class TestFeedConstraints:
    """Tests for Feed constraints and validation."""

    def test_unique_link_constraint(self, test_app, sample_basic_info):
        """Test unique constraint on link."""
        with test_app.app_context():
            # Create first feed
            feed1 = Feed(
                stock_id=sample_basic_info.id,
                releaseTime=datetime(2024, 3, 23, 10, 0, 0),
                title="Feed 1",
                link="https://example.com/feed/unique-test",
                feedType="announcement"
            )
            db.session.add(feed1)
            db.session.commit()

            # Try to create duplicate link
            feed2 = Feed(
                stock_id=sample_basic_info.id,
                releaseTime=datetime(2024, 3, 24, 10, 0, 0),
                title="Feed 2",
                link="https://example.com/feed/unique-test",  # Same link
                feedType="announcement"
            )
            db.session.add(feed2)

            with pytest.raises(IntegrityError):
                db.session.commit()

            db.session.rollback()

            # Cleanup
            Feed.query.filter_by(link="https://example.com/feed/unique-test").delete()
            db.session.commit()

    def test_valid_feed_type_enum(self, test_app, sample_basic_info):
        """Test that valid feedType values work."""
        with test_app.app_context():
            feeds = []
            for feed_type in ['announcement', 'news']:
                feed = Feed(
                    stock_id=sample_basic_info.id,
                    releaseTime=datetime(2024, 3, 25, 10, 0, 0),
                    title=f"Feed type {feed_type}",
                    link=f"https://example.com/feed/type-{feed_type}",
                    feedType=feed_type
                )
                feeds.append(feed)
                db.session.add(feed)

            db.session.commit()

            # Verify
            for feed_type in ['announcement', 'news']:
                saved = Feed.query.filter_by(
                    link=f"https://example.com/feed/type-{feed_type}"
                ).first()
                assert saved.feedType == feed_type

            # Cleanup
            for feed in feeds:
                db.session.delete(feed)
            db.session.commit()

    def test_nullable_stock_id(self, test_app):
        """Test that stock_id can be null."""
        with test_app.app_context():
            feed = Feed(
                stock_id=None,  # Nullable
                releaseTime=datetime(2024, 3, 26, 10, 0, 0),
                title="Feed without stock",
                link="https://example.com/feed/no-stock",
                feedType="news"
            )
            db.session.add(feed)
            db.session.commit()

            saved = Feed.query.filter_by(id=feed.id).first()
            assert saved.stock_id is None

            # Cleanup
            db.session.delete(saved)
            db.session.commit()

    def test_title_required(self, test_app):
        """Test that title is required."""
        with test_app.app_context():
            feed = Feed(
                releaseTime=datetime(2024, 3, 27, 10, 0, 0),
                title=None,  # Should fail
                link="https://example.com/feed/no-title",
                feedType="announcement"
            )
            db.session.add(feed)

            with pytest.raises(IntegrityError):
                db.session.commit()

            db.session.rollback()


class TestFeedRelationships:
    """Tests for Feed relationships."""

    def test_basic_information_relationship(self, test_app, sample_basic_info):
        """Test relationship with BasicInformation."""
        with test_app.app_context():
            feed = Feed(
                stock_id=sample_basic_info.id,
                releaseTime=datetime(2024, 3, 28, 10, 0, 0),
                title="Relationship Test Feed",
                link="https://example.com/feed/relationship-test",
                feedType="announcement"
            )
            db.session.add(feed)
            db.session.commit()

            # Access relationship
            saved = Feed.query.filter_by(id=feed.id).first()
            assert saved.stock is not None
            assert saved.stock.id == sample_basic_info.id

            # Cleanup
            db.session.delete(feed)
            db.session.commit()

    def test_tags_relationship(self, test_app, sample_feed_with_tags):
        """Test many-to-many relationship with FeedTag."""
        with test_app.app_context():
            feed, tags = sample_feed_with_tags

            # Verify tags relationship
            assert len(feed.tags) >= 2

    def test_announcement_income_sheet_analysis_relationship(
        self, test_app, sample_feed, sample_announcement_income_sheet_analysis
    ):
        """Test one-to-one relationship with AnnouncementIncomeSheetAnalysis."""
        with test_app.app_context():
            feed = Feed.query.filter_by(id=sample_feed.id).first()

            # Verify relationship
            assert feed.announcement_income_sheet_analysis is not None


class TestFeedQueries:
    """Tests for Feed query patterns."""

    def test_query_by_stock_id(self, test_app, sample_feed):
        """Test querying feeds by stock_id."""
        with test_app.app_context():
            feeds = Feed.query.filter_by(stock_id=sample_feed.stock_id).all()

            assert len(feeds) >= 1
            assert all(f.stock_id == sample_feed.stock_id for f in feeds)

    def test_query_by_feed_type(self, test_app, sample_basic_info):
        """Test querying feeds by feedType."""
        with test_app.app_context():
            # Create feeds of different types
            feeds = []
            for feed_type in ['announcement', 'news']:
                feed = Feed(
                    stock_id=sample_basic_info.id,
                    releaseTime=datetime(2024, 4, 1, 10, 0, 0),
                    title=f"Query test {feed_type}",
                    link=f"https://example.com/feed/query-{feed_type}",
                    feedType=feed_type
                )
                feeds.append(feed)
                db.session.add(feed)
            db.session.commit()

            # Query by type
            announcements = Feed.query.filter_by(feedType='announcement').all()
            news = Feed.query.filter_by(feedType='news').all()

            assert all(f.feedType == 'announcement' for f in announcements)
            assert all(f.feedType == 'news' for f in news)

            # Cleanup
            for feed in feeds:
                db.session.delete(feed)
            db.session.commit()

    def test_query_ordered_by_release_time_desc(self, test_app, sample_basic_info):
        """Test querying feeds ordered by releaseTime descending."""
        with test_app.app_context():
            # Create feeds with different release times
            feeds = []
            for i in range(3):
                feed = Feed(
                    stock_id=sample_basic_info.id,
                    releaseTime=datetime(2024, 4, i + 1, 10, 0, 0),
                    title=f"Order test {i}",
                    link=f"https://example.com/feed/order-{i}",
                    feedType="announcement"
                )
                feeds.append(feed)
                db.session.add(feed)
            db.session.commit()

            # Query ordered
            results = Feed.query.filter_by(
                stock_id=sample_basic_info.id
            ).order_by(Feed.releaseTime.desc()).all()

            # Verify order (newest first)
            if len(results) >= 2:
                for i in range(len(results) - 1):
                    assert results[i].releaseTime >= results[i + 1].releaseTime

            # Cleanup
            for feed in feeds:
                db.session.delete(feed)
            db.session.commit()

    def test_query_by_time_range(self, test_app, sample_basic_info):
        """Test querying feeds by time range."""
        with test_app.app_context():
            # Create feeds
            feeds = []
            for day in [1, 5, 10, 15]:
                feed = Feed(
                    stock_id=sample_basic_info.id,
                    releaseTime=datetime(2024, 4, day, 10, 0, 0),
                    title=f"Time range test {day}",
                    link=f"https://example.com/feed/time-{day}",
                    feedType="announcement"
                )
                feeds.append(feed)
                db.session.add(feed)
            db.session.commit()

            # Query time range
            start_time = datetime(2024, 4, 3)
            end_time = datetime(2024, 4, 12)
            results = Feed.query.filter(
                Feed.releaseTime.between(start_time, end_time)
            ).all()

            for feed in results:
                assert start_time <= feed.releaseTime <= end_time

            # Cleanup
            for feed in feeds:
                db.session.delete(feed)
            db.session.commit()


class TestFeedTagModel:
    """Tests for FeedTag model."""

    def test_instance_creation(self, test_app):
        """Test FeedTag instance creation."""
        tag = FeedTag(name="test_tag")

        assert tag.name == "test_tag"

    def test_serialize_property(self, test_app):
        """Test serialize property."""
        tag = FeedTag(name="serialize_test")

        serialized = tag.serialize

        assert serialized["name"] == "serialize_test"

    def test_unique_name_constraint(self, test_app):
        """Test unique constraint on name."""
        with test_app.app_context():
            # Create first tag
            tag1 = FeedTag(name="unique_tag_test")
            db.session.add(tag1)
            db.session.commit()

            # Try to create duplicate
            tag2 = FeedTag(name="unique_tag_test")
            db.session.add(tag2)

            with pytest.raises(IntegrityError):
                db.session.commit()

            db.session.rollback()

            # Cleanup
            FeedTag.query.filter_by(name="unique_tag_test").delete()
            db.session.commit()


class TestFeedFeedTagModel:
    """Tests for FeedFeedTag association model."""

    def test_create_association(self, test_app, sample_feed, sample_feed_tag_news):
        """Test creating Feed-FeedTag association."""
        with test_app.app_context():
            association = FeedFeedTag(
                feed_id=sample_feed.id,
                feedTag=sample_feed_tag_news.id
            )
            db.session.add(association)
            db.session.commit()

            # Verify
            saved = FeedFeedTag.query.filter_by(
                feed_id=sample_feed.id,
                feedTag=sample_feed_tag_news.id
            ).first()
            assert saved is not None

            # Cleanup
            db.session.delete(saved)
            db.session.commit()

    def test_repr_method(self, test_app, sample_feed, sample_feed_tag_earnings):
        """Test __repr__ method."""
        with test_app.app_context():
            association = FeedFeedTag(
                feed_id=sample_feed.id,
                feedTag=sample_feed_tag_earnings.id
            )

            repr_str = repr(association)

            assert str(sample_feed.id) in repr_str
            assert str(sample_feed_tag_earnings.id) in repr_str


class TestFeedMethods:
    """Tests for Feed model methods."""

    def test_create_default_announcement_income_sheet_analysis(
        self, test_app, sample_basic_info
    ):
        """Test create_default_announcement_income_sheet_analysis method."""
        with test_app.app_context():
            feed = Feed(
                stock_id=sample_basic_info.id,
                releaseTime=datetime(2024, 5, 1, 10, 0, 0),
                title="Analysis Test Feed",
                link="https://example.com/feed/analysis-test",
                feedType="announcement"
            )
            db.session.add(feed)
            db.session.commit()

            # Create analysis
            analysis = feed.create_default_announcement_income_sheet_analysis()

            assert analysis is not None
            assert analysis.feed_id == feed.id
            assert analysis.stock_id == feed.stock_id

            # Cleanup
            from app.models.announcement_income_sheet_analysis import AnnouncementIncomeSheetAnalysis
            AnnouncementIncomeSheetAnalysis.query.filter_by(feed_id=feed.id).delete()
            db.session.delete(feed)
            db.session.commit()

    def test_create_announcement_income_sheet_analysis_with_data(
        self, test_app, sample_basic_info
    ):
        """Test create_announcement_income_sheet_analysis method with data."""
        with test_app.app_context():
            feed = Feed(
                stock_id=sample_basic_info.id,
                releaseTime=datetime(2024, 5, 2, 10, 0, 0),
                title="Analysis Data Test Feed",
                link="https://example.com/feed/analysis-data-test",
                feedType="announcement"
            )
            db.session.add(feed)
            db.session.commit()

            # Create analysis with data
            analysis_data = {
                'year': 2024,
                'season': '1',
                '營業收入合計': 5000000000
            }
            analysis = feed.create_announcement_income_sheet_analysis(analysis_data)

            assert analysis is not None
            assert analysis.year == 2024
            assert analysis.season == '1'

            # Cleanup
            from app.models.announcement_income_sheet_analysis import AnnouncementIncomeSheetAnalysis
            AnnouncementIncomeSheetAnalysis.query.filter_by(feed_id=feed.id).delete()
            db.session.delete(feed)
            db.session.commit()


class TestFeedEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_long_link(self, test_app, sample_basic_info):
        """Test that link field can handle long URLs."""
        with test_app.app_context():
            long_link = "https://example.com/feed/" + "a" * 500

            feed = Feed(
                stock_id=sample_basic_info.id,
                releaseTime=datetime(2024, 5, 3, 10, 0, 0),
                title="Long Link Test",
                link=long_link,
                feedType="announcement"
            )
            db.session.add(feed)
            db.session.commit()

            saved = Feed.query.filter_by(id=feed.id).first()
            assert saved.link == long_link

            # Cleanup
            db.session.delete(saved)
            db.session.commit()

    def test_special_characters_in_title(self, test_app, sample_basic_info):
        """Test title with special characters."""
        with test_app.app_context():
            special_title = "公告：財務報表 & 營收 <重要> 'test' \"quote\""

            feed = Feed(
                stock_id=sample_basic_info.id,
                releaseTime=datetime(2024, 5, 4, 10, 0, 0),
                title=special_title,
                link="https://example.com/feed/special-chars",
                feedType="announcement"
            )
            db.session.add(feed)
            db.session.commit()

            saved = Feed.query.filter_by(id=feed.id).first()
            assert saved.title == special_title

            # Cleanup
            db.session.delete(saved)
            db.session.commit()

    def test_long_description(self, test_app, sample_basic_info):
        """Test that description field can handle long text."""
        with test_app.app_context():
            long_description = "描述內容 " * 1000  # Very long description

            feed = Feed(
                stock_id=sample_basic_info.id,
                releaseTime=datetime(2024, 5, 5, 10, 0, 0),
                title="Long Description Test",
                link="https://example.com/feed/long-desc",
                description=long_description,
                feedType="announcement"
            )
            db.session.add(feed)
            db.session.commit()

            saved = Feed.query.filter_by(id=feed.id).first()
            assert saved.description == long_description

            # Cleanup
            db.session.delete(saved)
            db.session.commit()

    def test_null_description(self, test_app, sample_basic_info):
        """Test that description can be null."""
        with test_app.app_context():
            feed = Feed(
                stock_id=sample_basic_info.id,
                releaseTime=datetime(2024, 5, 6, 10, 0, 0),
                title="No Description Test",
                link="https://example.com/feed/no-desc",
                description=None,
                feedType="announcement"
            )
            db.session.add(feed)
            db.session.commit()

            saved = Feed.query.filter_by(id=feed.id).first()
            assert saved.description is None

            # Cleanup
            db.session.delete(saved)
            db.session.commit()
