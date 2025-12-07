from datetime import datetime

from app import db


class FeedFeedTag(db.Model):
    """
    Association model for Feed-FeedTag many-to-many relationship.
    """
    __tablename__ = 'feed_feedTag'

    feed_id = db.Column(db.Integer, db.ForeignKey('feed.id'), primary_key=True)
    feedTag = db.Column(db.Integer, db.ForeignKey('feed_tag.id'), primary_key=True)

    # Relationships
    feed = db.relationship('Feed', backref=db.backref('feed_tags', lazy='dynamic'))
    tag = db.relationship('FeedTag', backref=db.backref('feed_tags', lazy='dynamic'))

    def __repr__(self):
        return f'<FeedFeedTag feed_id={self.feed_id} tag_id={self.feedTag}>'
