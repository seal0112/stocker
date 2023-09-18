from flask import request, jsonify, make_response
from flask.views import MethodView
from ..database_setup import Balance_Sheet
from .. import db
from . import balance_sheet
import json
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import logging

logger = logging.getLogger()


class handleBalanceSheet(MethodView):
    """
    Description:
        this api is used to handle balance sheet request.
    Detail:
        According to the received stock_id and request method,
        if request method is GET, then return stock_id's balance sheet.
        if request method is POST, then according to the data entered,
        decide whether to update or add new balance sheet data into database.
    Args:
        stock_id: a String of stock number.
    Return:
        if request method is GET,
            then return stock_id's balance sheet.
        if request method is POST,
            According to whether the data is written into the database
            if true, then return http status 201(Create).
            if not, then return http status 200(Ok).
    Raises:
        Exception: An error occurred.
    """

    def get(self, stock_id):
        return 'balance_sheet: %s' % stock_id

    def post(self, stock_id):
        payload = json.loads(request.data)
        balanceSheet = db.session.query(Balance_Sheet).filter_by(
            stock_id=stock_id).filter_by(
                year=payload['year']).filter_by(
                    season=payload['season']).one_or_none()
        try:
            if balanceSheet is not None:
                changeFlag = False
                for key in payload:
                    if balanceSheet[key] != payload[key]:
                        changeFlag = True
                        balanceSheet[key] = payload[key]
                # If there is no data to modify, then return 200
                if changeFlag is not True:
                    return make_response(json.dumps('OK'), 200)
                # if there is any data to modify,
                # then record currennt date for update_date
                balanceSheet['update_date'] = datetime.now(
                ).strftime("%Y-%m-%d")
            else:
                balanceSheet = Balance_Sheet()
                balanceSheet['stock_id'] = stock_id
                for key in payload:
                    balanceSheet[key] = payload[key]

            db.session.add(balanceSheet)
            db.session.commit()
        except IntegrityError as ie:
            db.session.rollback()
            logging.warning(
                "400 %s is failed to update Balance Sheet. Reason: %s"
                % (stock_id, ie))
            res = make_response(
                json.dumps(
                    'Failed to update %s Balance Sheet.' % (stock_id)), 400)
            return res
        except Exception as ex:
            db.session.rollback()
            logger.warning(
                "400 %s is failed to update Balance Sheett. Reason: %s"
                % (stock_id, ex))
            res = make_response(
                json.dumps(
                    'Failed to update %s Balance Sheet.' % (stock_id)), 400)
            return res

        res = make_response(
            json.dumps('Create'), 201)
        return res


balance_sheet.add_url_rule('/<stock_id>',
                  view_func=handleBalanceSheet.as_view(
                      'handleBalanceSheet'),
                  methods=['GET', 'POST'])
