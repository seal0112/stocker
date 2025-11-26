"""API endpoints for recommended stocks."""
import json
import logging
from datetime import datetime

from flask import request, make_response, jsonify
from flask.views import MethodView
from marshmallow import ValidationError

from .services import RecommendedStockService
from .serializer import RecommendedStockSchema, RecommendedStockDetailSchema
from . import recommended_stock

logger = logging.getLogger(__name__)
recommended_stock_service = RecommendedStockService()


class RecommendedStockListApi(MethodView):
    """API for listing and creating recommended stocks."""

    def get(self):
        """
        Get recommended stocks with optional filters.

        Query Parameters:
            - date (str): Date in YYYY-MM-DD format (default: today)
            - filter_model (str): Filter model name
            - limit (int): Maximum number of results
            - detail (bool): Return detailed information (default: false)

        Returns:
            JSON array of recommended stocks
        """
        try:
            # Parse query parameters
            date_str = request.args.get('date')
            filter_model = request.args.get('filter_model')
            limit = request.args.get('limit', type=int)
            detail = request.args.get('detail', 'false').lower() == 'true'

            # Parse date
            target_date = None
            if date_str:
                try:
                    target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                except ValueError:
                    return make_response(jsonify({
                        "error": "Invalid date format. Use YYYY-MM-DD"
                    }), 400)

            # Get recommendations
            recommendations = recommended_stock_service.get_recommended_stocks(
                date=target_date,
                filter_model=filter_model,
                limit=limit
            )

            # Serialize
            schema = RecommendedStockDetailSchema() if detail else RecommendedStockSchema()
            return make_response(schema.dumps(recommendations, many=True), 200)

        except Exception as e:
            logger.error(f"Error in GET /recommended_stock: {e}", exc_info=True)
            return make_response(jsonify({
                "error": "Internal server error"
            }), 500)

    def post(self):
        """
        Create a new recommended stock.

        Request Body:
            {
                "stock_id": "2330",
                "filter_model": "月營收近一年次高",
                "update_date": "2025-01-15"  // optional, default: today
            }

        Returns:
            Created recommendation (201) or error (400)
        """
        try:
            # Parse request
            payload = json.loads(request.data)

            # Validate required fields
            if 'stock_id' not in payload or 'filter_model' not in payload:
                return make_response(jsonify({
                    "error": "Missing required fields: stock_id, filter_model"
                }), 400)

            # Parse date if provided
            if 'update_date' in payload and isinstance(payload['update_date'], str):
                try:
                    payload['update_date'] = datetime.strptime(
                        payload['update_date'], '%Y-%m-%d'
                    ).date()
                except ValueError:
                    return make_response(jsonify({
                        "error": "Invalid update_date format. Use YYYY-MM-DD"
                    }), 400)

            # Create recommendation
            recommendation = recommended_stock_service.create_recommendation(payload)

            return make_response(
                RecommendedStockSchema().dumps(recommendation),
                201
            )

        except ValueError as e:
            return make_response(jsonify({"error": str(e)}), 400)
        except Exception as e:
            logger.error(f"Error in POST /recommended_stock: {e}", exc_info=True)
            return make_response(jsonify({
                "error": "Failed to create recommendation"
            }), 500)


class RecommendedStockDetailApi(MethodView):
    """API for getting, updating, and deleting specific recommendations."""

    def get(self, recommendation_id):
        """
        Get a specific recommendation by ID.

        Args:
            recommendation_id: ID of the recommendation

        Returns:
            Recommendation details (200) or not found (404)
        """
        try:
            recommendation = recommended_stock_service.get_recommended_stock_by_id(
                recommendation_id
            )

            if not recommendation:
                return make_response(jsonify({
                    "error": "Recommendation not found"
                }), 404)

            return make_response(
                RecommendedStockDetailSchema().dumps(recommendation),
                200
            )

        except Exception as e:
            logger.error(f"Error in GET /recommended_stock/{recommendation_id}: {e}", exc_info=True)
            return make_response(jsonify({
                "error": "Internal server error"
            }), 500)

    def delete(self, recommendation_id):
        """
        Delete a recommendation.

        Args:
            recommendation_id: ID of the recommendation to delete

        Returns:
            Success message (200) or not found (404)
        """
        try:
            success = recommended_stock_service.delete_recommendation(recommendation_id)

            if not success:
                return make_response(jsonify({
                    "error": "Recommendation not found"
                }), 404)

            return make_response(jsonify({
                "message": "Recommendation deleted successfully"
            }), 200)

        except Exception as e:
            logger.error(f"Error in DELETE /recommended_stock/{recommendation_id}: {e}", exc_info=True)
            return make_response(jsonify({
                "error": "Failed to delete recommendation"
            }), 500)


class RecommendedStockByStockApi(MethodView):
    """API for getting recommendation history for a specific stock."""

    def get(self, stock_id):
        """
        Get recommendation history for a specific stock.

        Args:
            stock_id: Stock ID (e.g., '2330')

        Query Parameters:
            - days (int): Number of days to look back (default: 30)

        Returns:
            JSON array of recommendations for the stock
        """
        try:
            days = request.args.get('days', 30, type=int)

            recommendations = recommended_stock_service.get_stocks_by_stock_id(
                stock_id=stock_id,
                days=days
            )

            return make_response(
                RecommendedStockSchema().dumps(recommendations, many=True),
                200
            )

        except Exception as e:
            logger.error(f"Error in GET /recommended_stock/stock/{stock_id}: {e}", exc_info=True)
            return make_response(jsonify({
                "error": "Internal server error"
            }), 500)


class RecommendedStockStatisticsApi(MethodView):
    """API for getting recommendation statistics."""

    def get(self):
        """
        Get statistics for recommended stocks.

        Query Parameters:
            - date (str): Date in YYYY-MM-DD format (default: today)

        Returns:
            JSON object with statistics
        """
        try:
            date_str = request.args.get('date')

            target_date = None
            if date_str:
                try:
                    target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                except ValueError:
                    return make_response(jsonify({
                        "error": "Invalid date format. Use YYYY-MM-DD"
                    }), 400)

            stats = recommended_stock_service.get_statistics(date=target_date)

            return make_response(jsonify(stats), 200)

        except Exception as e:
            logger.error(f"Error in GET /recommended_stock/statistics: {e}", exc_info=True)
            return make_response(jsonify({
                "error": "Internal server error"
            }), 500)


class RecommendedStockFilterModelsApi(MethodView):
    """API for getting available filter models."""

    def get(self):
        """
        Get list of available filter models.

        Returns:
            JSON array of filter model names
        """
        try:
            models = recommended_stock_service.get_available_filter_models()

            return make_response(jsonify({
                "filter_models": models
            }), 200)

        except Exception as e:
            logger.error(f"Error in GET /recommended_stock/filter-models: {e}", exc_info=True)
            return make_response(jsonify({
                "error": "Internal server error"
            }), 500)


# Register routes
recommended_stock.add_url_rule(
    '',
    view_func=RecommendedStockListApi.as_view('recommended_stock_list_api'),
    methods=['GET', 'POST']
)

recommended_stock.add_url_rule(
    '/<int:recommendation_id>',
    view_func=RecommendedStockDetailApi.as_view('recommended_stock_detail_api'),
    methods=['GET', 'DELETE']
)

recommended_stock.add_url_rule(
    '/stock/<string:stock_id>',
    view_func=RecommendedStockByStockApi.as_view('recommended_stock_by_stock_api'),
    methods=['GET']
)

recommended_stock.add_url_rule(
    '/statistics',
    view_func=RecommendedStockStatisticsApi.as_view('recommended_stock_statistics_api'),
    methods=['GET']
)

recommended_stock.add_url_rule(
    '/filter-models',
    view_func=RecommendedStockFilterModelsApi.as_view('recommended_stock_filter_models_api'),
    methods=['GET']
)
