import json
from datetime import datetime

from flask import request, jsonify
from flask.views import MethodView
from flask_jwt_extended import jwt_required

from .models import EarningsCall
from . import earnings_call
from .serializer import EarningsCallchema
from .earnings_call_services import EarningsCallService


earnings_call_service = EarningsCallService()

class EarningsCallListApi(MethodView):

    @jwt_required()
    def get(self):
        stock = request.args.get('stock', None)
        meeting_date = request.args.get('meeting_date', datetime.now())
        earnings_calls = earnings_call_service.get_stock_all_earnings_call(stock, meeting_date)
        return EarningsCallchema(many=True).dumps(earnings_calls)

    # @jwt_required()
    def post(self):
        try:
            earnings_call_data = request.get_json()
            if not earnings_call_data:
                return jsonify({"error": "Request body is required"}), 400
        except Exception:
            return jsonify({"error": "Invalid JSON format"}), 400

        earnings_calls = earnings_call_service.get_stock_earnings_call_by_date(
            earnings_call_data['stock_id'],
            earnings_call_data['meeting_date']
        )

        if earnings_calls:
            return jsonify({"status": "資料已存在"}), 200

        try:
            earnings_call = earnings_call_service.create_earnings_call(earnings_call_data)
        except Exception:
            return jsonify({"status": "資料錯誤"}), 400
        else:
            return EarningsCallchema().dumps(earnings_call), 201

class EarningsCallDetailApi(MethodView):

        @jwt_required()
        def get(self, earnings_call_id):
            return jsonify({"earnings_call": "GET"})

        @jwt_required()
        def put(self, earnings_call_id):
            try:
                earnings_call_data = request.get_json()
                if not earnings_call_data:
                    return jsonify({"error": "Request body is required"}), 400
            except Exception:
                return jsonify({"error": "Invalid JSON format"}), 400

            earnings_call = earnings_call_service.update_earnings_call(earnings_call_id, earnings_call_data)
            return EarningsCallchema().dumps(earnings_call)

        @jwt_required()
        def delete(self, earnings_call_id):
            earnings_call_service.delete_earnings_call(earnings_call_id)
            return jsonify({"earnings_call": "DELETE"}, 204)


earnings_call.add_url_rule('',
    view_func=EarningsCallListApi.as_view('EarningsCallListApi'),
    methods=['GET', 'POST'])

# earnings_call.add_url_rule('/<earnings_call_id>',
#     view_func=EarningsCallDetailApi.as_view(
#     'earnings_call_detail_api'),
#     methods=['GET', 'PATCH'])