from app.log_config import get_logger

from flask import request, jsonify
from flask.views import MethodView

from app import db
from .monthly_valuation_services import MonthlyValuationService
from .serializer import MonthlyValuationSchema
from . import monthly_valuation

logger = get_logger(__name__)

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
        return jsonify(MonthlyValuationSchema(many=True).dump(follow_stocks))

    def post(self):
        try:
            payload = request.get_json()
            if not payload:
                return jsonify({"error": "Request body is required"}), 400
        except Exception:
            return jsonify({"error": "Invalid JSON format"}), 400

        try:
            monthly_valuation = monthly_valuation_service.create_monthly_valuation(payload)
            if monthly_valuation:
                return jsonify(MonthlyValuationSchema().dump(monthly_valuation)), 201
            else:
                db.session.rollback()
                return jsonify({"error": "Failed to create monthly valuation"}), 400
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating monthly valuation: {e}", exc_info=True)
            return jsonify({"error": "Failed to create monthly valuation"}), 400

    def patch(self):
        try:
            payload = request.get_json()
            if not payload:
                return jsonify({"error": "Request body is required"}), 400
        except Exception:
            return jsonify({"error": "Invalid JSON format"}), 400

        try:
            monthly_valuation = monthly_valuation_service.update_monthly_valuation(payload)
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating monthly valuation: {e}", exc_info=True)
            return jsonify({"error": "Failed to update monthly valuation"}), 400
        else:
            return jsonify(MonthlyValuationSchema().dump(monthly_valuation))


monthly_valuation.add_url_rule('',
    view_func=MonthlyValuationListApi.as_view(
        'monthly_valuation_list_api'), methods=['GET', 'POST', 'PATCH'])
