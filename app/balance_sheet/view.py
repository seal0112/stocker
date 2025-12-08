from flask import request, jsonify, make_response
from flask.views import MethodView
from ..database_setup import BalanceSheet
from .. import db
from . import balance_sheet
import json
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


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
        try:
            payload = request.get_json()
            if not payload:
                return make_response(json.dumps("Request body is required"), 400)
        except Exception:
            return make_response(json.dumps("Invalid JSON format"), 400)

        balanceSheet = db.session.query(BalanceSheet).filter_by(
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
                    return jsonify({"message": "OK"}), 200
                # if there is any data to modify,
                # then record currennt date for update_date
                balanceSheet['update_date'] = datetime.now(
                ).strftime("%Y-%m-%d")
            else:
                balanceSheet = BalanceSheet()
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
            return jsonify({"error": "Failed to update %s Balance Sheet" % stock_id}), 400
        except Exception as ex:
            db.session.rollback()
            logger.warning(
                "400 %s is failed to update Balance Sheet. Reason: %s"
                % (stock_id, ex))
            return jsonify({"error": "Failed to update %s Balance Sheet" % stock_id}), 400

        return jsonify({"message": "Created"}), 201


balance_sheet.add_url_rule('/<stock_id>',
                  view_func=handleBalanceSheet.as_view(
                      'handleBalanceSheet'),
                  methods=['GET', 'POST'])
