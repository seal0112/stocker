from app import db
from app.utils.model_utilities import get_current_date


class RecommendedStock(db.Model):
    __tablename__ = 'recommended_stocks'

    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.String(6), db.ForeignKey('basic_information.id'), nullable=True)
    update_date = db.Column(
        db.Date, nullable=False, default=get_current_date, index=True
    )
    filter_model = db.Column(db.String(100), nullable=False, index=True)

    __table_args__ = (
        db.UniqueConstraint('stock_id', 'update_date', 'filter_model', name='uix_stock_update_filter'),
    )

    def __repr__(self):
        return f'RecommendedStock({self.stock_id}, {self.update_date}, {self.filter_model})'
