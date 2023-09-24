from ..database_setup import StockSearchCounts
import logging
from .. import db

logger = logging.getLogger()


class StockSearchCountService:
    def __init__(self):
        pass

    def get_stock_search_count(self, stock_id):
        return StockSearchCounts.query.filter_by(stock_id=stock_id).one_or_none()

    def get_stock_search_counts(self):
        return StockSearchCounts.query.all()

    def create_stock_search_count(self, stock_id):
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

    def increase_stock_search_count(self, stock_id):
        try:
            stock_search_count = StockSearchCounts.query.with_for_update().get(stock_id)
            stock_search_count.search_count += 1
            db.session.commit()
        except Exception as ex:
            db.session.rollback()
            logger.exception(f'Failed to increase stock {stock_id} search count: {ex}')
