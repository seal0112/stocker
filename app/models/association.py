from app import db


feed_feed_tag_association = db.Table(
    'feed_feedTag',
    db.Column('feed_id', db.Integer, db.ForeignKey('feed.id'), primary_key=True),
    db.Column('feedTag', db.Integer, db.ForeignKey('feed_tag.id'), primary_key=True)
)