from datetime import datetime

from app import db


class FeedFeedTag(db.Model):
    """
    Association model for Feed-FeedTag many-to-many relationship.
    """
    __tablename__ = 'feed_feedTag'

    feed_id = db.Column(
        db.Integer,
        db.ForeignKey('feed.id', ondelete='CASCADE'),
        primary_key=True
    )
    feedTag = db.Column(
        db.Integer,
        db.ForeignKey('feed_tag.id', ondelete='CASCADE'),
        primary_key=True
    )

    # Relationships (viewonly to avoid conflicts with Feed.tags secondary relationship)
    feed = db.relationship(
        'Feed',
        backref=db.backref('feed_tags', lazy='dynamic', passive_deletes=True),
        viewonly=True
    )
    tag = db.relationship(
        'FeedTag',
        backref=db.backref('feed_tags', lazy='dynamic', passive_deletes=True),
        viewonly=True
    )

    def __repr__(self):
        return f'<FeedFeedTag feed_id={self.feed_id} tag_id={self.feedTag}>'
