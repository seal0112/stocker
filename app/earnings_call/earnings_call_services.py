import logging

from .models import EarningsCall
from .. import db
from ..utils.data_update_date_service import DataUpdateDateService


data_update_date_service = DataUpdateDateService()
logger = logging.getLogger()


class EarningsCallService():

    def __init__(self):
        self.earnings_call_data_size = 20

    def get_stock_all_earnings_call(self, stock_id, meeting_date):
        earning_call_query = EarningsCall.query
        if stock_id:
            earning_call_query = earning_call_query.filter_by(stock_id=stock_id)

        if meeting_date:
            earning_call_query = earning_call_query.filter(
                EarningsCall.meeting_date <= meeting_date)

        return earning_call_query.order_by(
                    EarningsCall.meeting_date.desc()).limit(self.earnings_call_data_size).all()

    def create_earnings_call(self, earnings_call_data):
        earnings_call = EarningsCall()
        earnings_call.stock_id = earnings_call_data['stock_id']
        earnings_call.meeting_date = earnings_call_data['meeting_date']
        earnings_call.location = earnings_call_data['location']
        earnings_call.description = earnings_call_data['description']

        try:
            db.session.add(earnings_call)
            db.session.commit()
        except Exception as ex:
            db.session.rollback()
            logger.error(ex)
            raise ex
        else:
            data_update_date_service.update_earnings_call_update_date(earnings_call.stock_id)
            return earnings_call

    def get_earnings_call(self, earnings_call_id=None):
        return EarningsCall.query.filter_by(id=earnings_call_id).one_or_none()

    def update_earnings_call(self, earnings_call_id, earnings_call_data):
        earnings_call = self.get_earnings_call(earnings_call_id)
        if not earnings_call:
            return

        for key in earnings_call_data:
            earnings_call[key] = earnings_call_data[key]

        try:
            db.session.commit()
        except Exception as ex:
            db.session.rollback()
            logger.error(ex)

        return earnings_call

    def delete_earnings_call(self, earnings_call_id):
        try:
            EarningsCall.query.filter_by(id=earnings_call_id).delete()
        except Exception as ex:
            logger.error(ex)
