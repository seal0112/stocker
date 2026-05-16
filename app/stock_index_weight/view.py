from app.log_config import get_logger

from flask import request, jsonify
from flask.views import MethodView

from app import db
from app.decorators.auth import api_auth_required
from .services import StockIndexWeightService
from .serializer import StockIndexWeightSchema
from . import stock_index_weight

logger = get_logger(__name__)

service = StockIndexWeightService()


class StockIndexWeightApi(MethodView):
    decorators = [api_auth_required]

    def get(self):
        stock = request.args.get('stock', type=str)
        years = request.args.get('years', 5, type=int)

        if not stock or len(stock) > 10:
            return jsonify({"error": "Invalid stock parameter"}), 400
        if years < 1 or years > 20:
            return jsonify({"error": "years must be between 1 and 20"}), 400

        records = service.get_by_stock(stock, years)
        return jsonify(StockIndexWeightSchema(many=True).dump(records))

    def post(self):
        try:
            payload = request.get_json()
            if not payload:
                return jsonify({"error": "Request body is required"}), 400
        except Exception:
            return jsonify({"error": "Invalid JSON format"}), 400

        record = service.upsert(payload)
        if record:
            return jsonify(StockIndexWeightSchema().dump(record)), 201
        return jsonify({"error": "Failed to upsert stock index weight"}), 400


stock_index_weight.add_url_rule(
    '',
    view_func=StockIndexWeightApi.as_view('stock_index_weight_api'),
    methods=['GET', 'POST']
)
