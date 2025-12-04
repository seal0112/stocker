import json

from flask import request, make_response, jsonify
from flask.views import MethodView
from flask_jwt_extended import jwt_required

import logging

from .monthly_valuation_services import MonthlyValuationService
from .serializer import MonthlyValuationSchema
from . import monthly_valuation

monthly_valuation_service = MonthlyValuationService()



class MonthlyValuationListApi(MethodView):

    def get(self):
        stock = request.args.get('stock', '2330', type=str)
        years = request.args.get('years', 5, type=int)

        # Validate parameters
        if not stock or len(stock) > 10:
            return jsonify({"error": "Invalid stock parameter"}), 400
        if years is None or years < 1 or years > 20:
            return jsonify({"error": "Invalid years parameter. Must be between 1 and 20"}), 400

        follow_stocks = monthly_valuation_service.get_stock_monthly_valuations(
            stock, years)
        return MonthlyValuationSchema().dumps(follow_stocks, many=True)

    def post(self):
        payload = json.loads(request.data)
        monthly_valuation = monthly_valuation_service.create_monthly_valuation(payload)
        if monthly_valuation:
            return make_response(MonthlyValuationSchema().dumps(monthly_valuation), 201)
        else:
            return make_response({
                "status": "monthly valuation資料建立錯誤"
            }, 400)

    def patch(self):
        payload = json.loads(request.data)
        try:
            monthly_valuation = monthly_valuation_service.update_monthly_valuation(payload)
        except Exception as ex:
            logging.error(f'fail update monthly_valuation: {ex}')
            return make_response({
                "status": "monthly valuation資料建立錯誤"
            }, 400)
        else:
            return make_response(MonthlyValuationSchema().dumps(monthly_valuation), 200)


monthly_valuation.add_url_rule('',
    view_func=MonthlyValuationListApi.as_view(
        'monthly_valuation_list_api'), methods=['GET', 'POST', 'PATCH'])
