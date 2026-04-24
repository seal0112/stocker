from app import db


class FeedTag(db.Model):
    __tablename__ = 'feed_tag'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)

    @property
    def serialize(self):
        return {
            'name': self.name
        }
