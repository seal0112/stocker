import logging
from datetime import datetime, timedelta

from ..database_setup import StockSearchCounts
from .. import db
from .. import redis_client


logger = logging.getLogger(__name__)


class StockSearchCountService:
    def __init__(self):
        pass

    def get_stock_search_count(self, stock_id):
        return StockSearchCounts.query.filter_by(stock_id=stock_id).one_or_none()

    def get_stock_search_counts(self):
        return StockSearchCounts.query.all()

    def create_stock_search_count(self, stock_id):
        stock_search_count = db.session.query(StockSearchCounts).filter_by(
            stock_id=stock_id).one_or_none()

        if stock_search_count is not None:
            return stock_search_count

        try:

            stock_search_count = StockSearchCounts()
            stock_search_count.stock_id = stock_id

            db.session.add(stock_search_count)
            db.session.commit()

            return stock_search_count
        except Exception as ex:
            db.session.rollback()
            logger.exception(f'Failed to create stock search count: {ex}')

            return None

    def increase_stock_search_count(self, user_email, stock_id):
        redis_search_count_key = f'{user_email}:search_count'
        if redis_client.sismember(redis_search_count_key, stock_id):
            return None

        redis_client.sadd(redis_search_count_key, stock_id)
        redis_client.expireat(
            redis_search_count_key,
            datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(1)
        )

        try:
            stock_search_count = StockSearchCounts.query.with_for_update().get(stock_id)
            stock_search_count.search_count += 1
            db.session.commit()
        except Exception as ex:
            db.session.rollback()
            logger.exception(f'Failed to increase stock {stock_id} search count: {ex}')
