from datetime import datetime

from .. import db
from ..database_setup import BasicInformation
from ..auth.models import User
from ..utils.model_utilities import get_UUID


class Follow_Stock(db.Model):
    __tablename__ = 'follow_stock'

    id = db.Column(db.String(32), default=get_UUID, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey(User.id), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    last_update_time = db.Column(db.DateTime, default=datetime.utcnow)
    remove_time = db.Column(db.DateTime)
    comment = db.Column(db.Text)
    long_or_short = db.Column(db.String(10), nullable=False)
    is_delete = db.Column(db.Boolean, default=False)
    stock_id = db.Column(
        db.String(6), db.ForeignKey(BasicInformation.id),
        nullable=False)
    stock = db.relationship("BasicInformation", lazy="immediate")

    @property
    def serialize(self):
        return {
            "id": self.id,
            "stock_id": self.stock_id,
            "create_time": self.create_time,
            "last_update_time": self.last_update_time,
            "remove_time": self.remove_time,
            "comment": self.comment,
            "long_or_short": self.long_or_short,
            "is_delete": self.is_delete,
        }

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)
