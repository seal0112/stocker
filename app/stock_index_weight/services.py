from app.log_config import get_logger

from marshmallow import ValidationError

from .models import StockIndexWeight
from .serializer import StockIndexWeightSchema
from .. import db

logger = get_logger(__name__)


class StockIndexWeightService():

    def get(self, stock_id, year, month, index_type):
        return StockIndexWeight.query.filter_by(
            stock_id=stock_id, year=year, month=month, index_type=index_type
        ).one_or_none()

    def get_by_stock(self, stock_id, years):
        from datetime import datetime
        min_year = datetime.now().year - years
        return StockIndexWeight.query.filter_by(
            stock_id=stock_id
        ).filter(StockIndexWeight.year >= min_year).order_by(
            StockIndexWeight.year.desc(), StockIndexWeight.month.desc()
        ).all()

    def upsert(self, data: dict):
        try:
            validated = StockIndexWeightSchema().load(data)
        except ValidationError as err:
            logger.error(f"Validation error: {err.messages}")
            return None

        record = self.get(
            validated['stock_id'],
            validated['year'],
            validated['month'],
            validated['index_type']
        )

        if record:
            record['rank'] = validated.get('rank')
            record['weight'] = validated.get('weight')
        else:
            record = StockIndexWeight(**validated)
            db.session.add(record)

        try:
            db.session.commit()
            return record
        except Exception as ex:
            db.session.rollback()
            logger.error(
                f"Failed to upsert stock_index_weight: "
                f"{data.get('stock_id')}-{data.get('year')}/{data.get('month')}-{data.get('index_type')}, ex: {ex}"
            )
            return None
