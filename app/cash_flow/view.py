from flask import request, jsonify, make_response
from flask.views import MethodView
from ..database_setup import Cash_Flow
from .. import db
from . import cash_flow
import json


class handleCashFlow(MethodView):
    """
    Description:
        this api is used to handle cash flow request.
    Detail:
        According to the received stock_id and request method,
        if request method is GET, then return stock_id's cash flow.
        if request method is POST, then according to the data entered,
        decide whether to update or add new cash flow data into database.
    Args:
        stock_id: a String of stock number.
    Return:
        if request method is GET,
            then return stock_id's cash flow.
        if request method is POST,
            According to whether the data is written into the database
            if true, then return http status 201(Create).
            if not, then return http status 200(Ok).
    Raises:
        Exception: An error occurred.
    """

    def get(self, stock_id):
        return 'cash_flow: %s' % stock_id

    def post(self, stock_id):
        payload = json.loads(request.data)
        cashFlow = db.session.query(Cash_Flow).filter_by(
            stock_id=stock_id).filter_by(
                year=payload['year']).filter_by(
                    season=payload['season']).one_or_none()
        try:
            if cashFlow is not None:
                changeFlag = False
                for key in payload:
                    if cashFlow[key] != payload[key]:
                        changeFlag = True
                        cashFlow[key] = payload[key]
                # If there is no data to modify, then return 200
                if changeFlag is not True:
                    return make_response(json.dumps('OK'), 200)
                # if there is any data to modify,
                # then record currennt date for update_date
                cashFlow['update_date'] = datetime.now(
                ).strftime("%Y-%m-%d")
            else:
                cashFlow = Cash_Flow()
                cashFlow['stock_id'] = stock_id
                for key in payload:
                    cashFlow[key] = payload[key]

            db.session.add(cashFlow)
            db.session.commit()
        except IntegrityError as ie:
            db.session.rollback()
            print("%s: %s" % (stock_id, ie))
            logging.warning(
                "400 %s is failed to update Cash Flowe. Reason: %s"
                % (stock_id, ie))
            res = make_response(
                json.dumps(
                    'Failed to update %s Cash Flow.' % (stock_id)), 400)
            return res
        except Exception as ex:
            db.session.rollback()
            print(ex)
            logger.warning(
                "400 %s is failed to update Cash Flow. Reason: %s"
                % (stock_id, ex))
            res = make_response(
                json.dumps(
                    'Failed to update %s Cash Flow.' % (stock_id)), 400)
            return res

        res = make_response(
            json.dumps('Create'), 201)
        return res


cash_flow.add_url_rule('/<stock_id>',
                  view_func=handleCashFlow.as_view(
                      'handleCashFlow'),
                  methods=['GET', 'POST'])