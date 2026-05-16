from datetime import datetime

from .. import db
from ..database_setup import BasicInformation


class StockIndexWeight(db.Model):
    __tablename__ = 'stock_index_weight'

    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(
        db.String(6), db.ForeignKey(BasicInformation.id),
        nullable=False)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    index_type = db.Column(db.String(10), nullable=False)  # 'twse' | 'tpex'
    rank = db.Column(db.Integer)
    weight = db.Column(db.Numeric(10, 4))
    create_time = db.Column(db.DateTime, default=datetime.now)

    __table_args__ = (
        db.UniqueConstraint(
            'stock_id', 'year', 'month', 'index_type',
            name='uix_stock_index_weight'
        ),
    )

    def __repr__(self):
        return f'StockIndexWeight({self.stock_id}, {self.year}/{self.month}, {self.index_type})'

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)
