from datetime import datetime
from app.log_config import get_logger

from marshmallow import ValidationError

from .models import MonthlyValuation
from .serializer import MonthlyValuationSchema
from .. import db

logger = get_logger(__name__)


class MonthlyValuationService():

    def __init__(self):
        pass

    def get_stock_monthly_valuation(self, stock, year, month):
        return MonthlyValuation.query.filter_by(
            stock_id=stock, year=year, month=month).one_or_none()

    def get_stock_monthly_valuations(self, stock, years):
        data = MonthlyValuation.query.filter_by(
            stock_id=stock).filter(MonthlyValuation.year >= datetime.now().year-years).all()
        return data

    _UPSERT_FIELDS = ['本益比', '淨值比', '殖利率', '均價']

    def create_monthly_valuation(self, monthly_valuation_data):
        try:
            validated_data = MonthlyValuationSchema().load(monthly_valuation_data)
        except ValidationError as err:
            logger.error(err.messages)
            return None

        existing = self.get_stock_monthly_valuation(
            monthly_valuation_data['stock_id'],
            monthly_valuation_data['year'],
            monthly_valuation_data['month']
        )

        if existing:
            for key in self._UPSERT_FIELDS:
                if key in validated_data:
                    setattr(existing, key, validated_data[key])
            try:
                db.session.commit()
                return existing
            except Exception as ex:
                db.session.rollback()
                logger.error(
                    f'fail upsert monthly_valuation: {monthly_valuation_data.get("stock_id")}'
                    f'-{monthly_valuation_data.get("year")}/{monthly_valuation_data.get("month")}, ex: {ex}'
                )
                return None

        new_monthly_valuation = MonthlyValuation(**validated_data)
        try:
            db.session.add(new_monthly_valuation)
            db.session.commit()
            return new_monthly_valuation
        except Exception as ex:
            db.session.rollback()
            logger.error(
                f'fail create monthly_valuation: {monthly_valuation_data.get("stock_id")}'
                f'-{monthly_valuation_data.get("year")}/{monthly_valuation_data.get("month")}, ex: {ex}'
            )
            return None

    def update_monthly_valuation(self, monthly_valuation_data):
        data_key = ['本益比', '淨值比', '殖利率', '均價']

        monthly_valuation = self.get_stock_monthly_valuation(
            monthly_valuation_data['stock_id'],
            monthly_valuation_data['year'],
            monthly_valuation_data['month']
        )

        if not monthly_valuation:
            return monthly_valuation

        for key in monthly_valuation_data:
            if key in data_key:
                monthly_valuation[key] = monthly_valuation_data[key]

        try:
            db.session.commit()
            return monthly_valuation
        except Exception as ex:
            db.session.rollback()
            logging.exception((
                'fail update monthly_valuation, ' +
                f'payload: {monthly_valuation_data}, ex: {ex}'
            ))
            return None
