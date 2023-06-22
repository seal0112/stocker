from ..database_setup import Data_Update_Date
import logging
from datetime import date
from .. import db

logger = logging.getLogger()


class DataUpdateDateService:
    def __init__(self):
        pass

    def get_data_update_date(self, stock_id):
        data_update_date = db.session.query(Data_Update_Date).filter_by(
            stock_id=stock_id).one_or_none()
        if not data_update_date:
            data_update_date = self.create_stock_data_update_date(stock_id)
        return data_update_date

    def create_stock_data_update_date(self, stock_id):
        data_update_date = Data_Update_Date()
        data_update_date.stock_id = stock_id
        db.session.add(data_update_date)
        db.session.commit()
        return data_update_date

    def update_feed_update_date(self, stock_id):
        data_update_date = self.get_data_update_date(stock_id)

        try:
            data_update_date.feed_last_update = date.today()
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
