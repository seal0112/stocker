from datetime import datetime

from .. import db
from ..database_setup import BasicInformation


class MonthlyValuation(db.Model):
    __tablename__ = 'monthly_valuation'

    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(
        db.String(6), db.ForeignKey(BasicInformation.id),
        nullable=False)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(
        db.Enum('1', '2', '3', '4', '5', '6',
                '7', '8', '9', '10', '11', '12'), nullable=False)
    本益比 = db.Column(db.DECIMAL(10, 2))
    淨值比 = db.Column(db.DECIMAL(10, 2))
    殖利率 = db.Column(db.DECIMAL(10, 2))
    均價 = db.Column(db.DECIMAL(10, 2))
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'MonthlyValuation({self.stock_id}, {self.year}, {self.month})'

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)


db.Index(
    'stock_id_year_month',
    MonthlyValuation.stock_id,
    MonthlyValuation.year,
    MonthlyValuation.month,
    unique=True
)
