from datetime import datetime
import logging

from .models import Follow_Stock
# from ..database_setup import Daily_Information
from .. import db


class FollowStockService():

    def __init__(self):
        pass

    def get_all_follow_stock(self, user_id, show_delete):
        query = db.session.query(Follow_Stock).filter_by(user_id=user_id)
        # query = db.session.query(Follow_Stock, Daily_Information).filter(Follow_Stock.stock_id == Daily_Information.stock_id).filter_by(
        #     user_id=user_id)
        if not show_delete:
            query = query.filter_by(is_delete=False)

        follow_stocks = query.order_by(Follow_Stock.create_time.desc()).all()
        return follow_stocks

    def get_follow_stock(self, user_id, stock_id):
        follow_stock = db.session.query(Follow_Stock).filter_by(
            user_id=user_id).filter_by(
                stock_id=stock_id).filter_by(
                    is_delete=False).order_by(
                        Follow_Stock.create_time).one_or_none()
        return follow_stock

    def create_follow_stock(self, user_id, stock_id, long_or_short, comment):
        follow_stock =  self.get_follow_stock(user_id, stock_id)
        if follow_stock:
            return follow_stock

        new_follow_stock = Follow_Stock()
        new_follow_stock['user_id'] = user_id
        new_follow_stock['stock_id'] = stock_id
        new_follow_stock['long_or_short'] = long_or_short
        new_follow_stock['comment'] = comment

        try:
            db.session.add(new_follow_stock)
            db.session.commit()
            return new_follow_stock
        except Exception as ex:
            db.session.rollback()
            logging.exception(
                f'fail create user-stock: {user_id}-{stock_id}, ex: {ex}')
            return None

    def update_follow_stock(self, user_id, follow_stock_id, long_or_short, comment):
        follow_data = db.session.query(Follow_Stock).filter_by(
            user_id=user_id).filter_by(
                id=follow_stock_id).filter_by(
                    is_delete=False).one()
        follow_data['long_or_short'] = long_or_short
        follow_data['comment'] = comment
        follow_data['last_update_time'] = datetime.utcnow()
        try:
            db.session.commit()
            return follow_data
        except Exception as ex:
            db.session.rollback()
            logging.exception(
                f'fail update user-stock: {user_id}-{self.stock_id}, ex: {ex}')
            return None


    def delete_follow_stock(self, user_id, follow_stock_id):
        follow_stock = db.session.query(Follow_Stock).filter_by(
            user_id=user_id).filter_by(
                id=follow_stock_id).one()
        follow_stock.is_delete = True
        follow_stock.remove_time = datetime.now()
        try:
            db.session.commit()
            return None
        except Exception as ex:
            db.session.rollback()
            logging.exception(
                f'fail delete user-stock: {user_id}-{stock_id}, ex: {ex}')
            return None
