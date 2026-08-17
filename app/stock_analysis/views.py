from flask import jsonify, make_response
from flask.views import MethodView

from app.log_config import get_logger
from . import stock_analysis
from .services import StockAnalysisService

logger = get_logger(__name__)
_service = StockAnalysisService()


class StockQualitativeAnalysisApi(MethodView):

    def get(self, stock_id: str):
        try:
            report = _service.analyze(stock_id)
            return make_response(jsonify(_service.to_dict(report)), 200)
        except ValueError as e:
            return make_response(jsonify({'error': str(e)}), 422)
        except Exception as e:
            logger.error(f"Error in GET /stock_analysis/{stock_id}: {e}", exc_info=True)
            return make_response(jsonify({'error': 'Internal server error'}), 500)


stock_analysis.add_url_rule(
    '/<string:stock_id>',
    view_func=StockQualitativeAnalysisApi.as_view('stock_qualitative_analysis_api'),
    methods=['GET'],
)
