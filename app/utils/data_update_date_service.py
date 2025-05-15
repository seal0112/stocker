from ..database_setup import DataUpdateDate
import logging
from datetime import date
from .. import db


logger = logging.getLogger(__name__)


class DataUpdateDateService:
    def __init__(self):
        pass

    def get_data_update_date(self, stock_id):
        data_update_date = db.session.query(DataUpdateDate).filter_by(
            stock_id=stock_id).one_or_none()
        if not data_update_date:
            data_update_date = self.create_stock_data_update_date(stock_id)
        return data_update_date

    def create_stock_data_update_date(self, stock_id):
        data_update_date = DataUpdateDate()
        data_update_date.stock_id = stock_id
        db.session.add(data_update_date)
        db.session.commit()
        return data_update_date

    def update_announcement_update_date(self, stock_id):
        data_update_date = self.get_data_update_date(stock_id)

        try:
            data_update_date.announcement_last_update = date.today()
            db.session.commit()
            return True
        except Exception as ex:
            db.session.rollback()
            logger.exception(f'Failed to update news update date: {ex}')
            return False

    def update_news_update_date(self, stock_id):
        data_update_date = self.get_data_update_date(stock_id)

        try:
            data_update_date.news_last_update = date.today()
            db.session.commit()
            return True
        except Exception as ex:
            db.session.rollback()
            logger.exception(f'Failed to update news update date: {ex}')
            return False

    def update_month_revenue_update_date(self, stock_id):
        data_update_date = self.get_data_update_date(stock_id)

        try:
            data_update_date.month_revenue_last_update = date.today()
            db.session.commit()
            return True
        except Exception as ex:
            db.session.rollback()
            logger.exception(f'Failed to update news update date: {ex}')
            return False

    def update_income_sheet_update_date(self, stock_id):
        data_update_date = self.get_data_update_date(stock_id)

        try:
            data_update_date.income_sheet_last_update = date.today()
            db.session.commit()
            return True
        except Exception as ex:
            db.session.rollback()
            logger.exception(f'Failed to update news update date: {ex}')
            return False

    def update_earnings_call_update_date(self, stock_id):
        data_update_date = self.get_data_update_date(stock_id)

        try:
            data_update_date.earnings_call_last_update = date.today()
            db.session.commit()
            return True
        except Exception as ex:
            db.session.rollback()
            logger.exception(f'Failed to update news update date: {ex}')
            return False
