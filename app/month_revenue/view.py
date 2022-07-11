from flask import request, jsonify, make_response
from flask.views import MethodView
from ..database_setup import Month_Revenue
from .. import db
from . import month_revenue
import json


class handleMonthRevenue(MethodView):
    """
    Description:
        this api is used to handle month revenue request.
    Detail:
        According to the received stock_id and request method,
        if request method is GET, then return stock_id's month reveune.
        if request method is POST, then according to the data entered,
        decide whether to update or add new data into database.
    Args:
        stock_id: a String of stock number.
    Return:
        if request method is GET,
            then return stock_id's month revenue.
        if request method is POST,
            According to whether the data is written into the database
            if true, then return http status 201(Create).
            if not, then return http status 200(Ok).
    Raises:
        Exception: An error occurred.
    """

    def get(self, stock_id):
        """
        return stock's monthly revenue data for the last five years
        swagger_from_file: MonthRevenue_get.yml
        """
        monthReve = db.session.query(Month_Revenue).filter_by(
            stock_id=stock_id
        ).order_by(Month_Revenue.year.desc()).limit(60).all()
        if monthReve is None:
            return make_response(404)
        else:
            result = [i.serialize for i in monthReve]
            return jsonify(result)

    def post(self, stock_id):
        """
        Create or Update stock_id's month revenue data
        swagger_from_file: MonthRevenue_post.yml
        """
        payload = json.loads(request.data)
        monthReve = db.session.query(Month_Revenue).filter_by(
            stock_id=stock_id).filter_by(
                year=payload['year']).filter_by(
                    month=payload['month']).one_or_none()
        # check payload
        for key in payload:
            if payload[key] == '不適用':
                payload[key] = None

        try:
            if monthReve is not None:
                changeFlag = False
                for key in payload:
                    if monthReve[key] != payload[key]:
                        changeFlag = True
                        monthReve[key] = payload[key]
                # If there is no data to modify, then return 200
                if changeFlag is not True:
                    return make_response(json.dumps('OK'), 200)
                # if there is any data to modify,
                # then record currennt date for update_date
                monthReve['update_date'] = datetime.now(
                ).strftime("%Y-%m-%d")
            else:
                monthReve = Month_Revenue()
                for key in payload:
                    monthReve[key] = payload[key]

            db.session.add(monthReve)
            db.session.commit()
        except IntegrityError as ie:
            db.session.rollback()
            print("%s: %s" % (stock_id, ie))
            logging.warning(
                "400 %s is failed to update Month Revenue. Reason: %s"
                % (stock_id, ie))
            res = make_response(
                json.dumps(
                    'Failed to update %s Month Revenue.' % (stock_id)), 400)
            return res
        except Exception as ex:
            db.session.rollback()
            print("%s: %s" % (stock_id, ex))
            logging.warning(
                "400 %s is failed to update Month Revenue. Reason: %s"
                % (stock_id, ex))
            res = make_response(
                json.dumps(
                    'Failed to update %s Month Revenue.' % (stock_id)), 400)
            return res

        res = make_response(
            json.dumps('Create'), 201)
        return res


month_revenue.add_url_rule('/<stock_id>',
                  view_func=handleMonthRevenue.as_view(
                      'handleMonthRevenue'),
                  methods=['GET', 'POST'])