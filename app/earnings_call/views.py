from app.log_config import get_logger
from datetime import datetime

from flask import request, jsonify
from flask.views import MethodView
from flask_jwt_extended import jwt_required

from app import db
from . import earnings_call
from .serializer import EarningsCallchema
from .earnings_call_services import EarningsCallService
from app.decorators.auth import api_auth_required
from app.ai_report.models import AiReport

logger = get_logger(__name__)
earnings_call_service = EarningsCallService()


class EarningsCallListApi(MethodView):

    @jwt_required()
    def get(self):
        stock = request.args.get('stock', None)
        meeting_date = request.args.get('meeting_date', None)
        date_from = request.args.get('date_from', None)
        date_to = request.args.get('date_to', None)
        score_min = request.args.get('score_min', None, type=int)
        score_max = request.args.get('score_max', None, type=int)
        page = request.args.get('page', None, type=int)
        page_size = request.args.get('page_size', 20, type=int)

        pagination_or_list = earnings_call_service.get_stock_all_earnings_call(
            stock_id=stock,
            meeting_date=meeting_date,
            date_from=date_from,
            date_to=date_to,
            score_min=score_min,
            score_max=score_max,
            page=page,
            page_size=page_size,
        )

        is_paginated = page is not None
        earnings_calls = pagination_or_list.items if is_paginated else pagination_or_list

        from app.database_setup import BasicInformation
        stock_ids = {ec.stock_id for ec in earnings_calls}
        name_map = {
            b.id: getattr(b, '公司簡稱', None)
            for b in BasicInformation.query.filter(BasicInformation.id.in_(stock_ids)).all()
        }

        ec_ids = [ec.id for ec in earnings_calls]
        report_map = {
            r.ref_id: r
            for r in AiReport.query.filter(
                AiReport.report_type == 'earnings_call',
                AiReport.ref_id.in_(ec_ids),
            ).all()
        } if ec_ids else {}

        result = []
        for ec in earnings_calls:
            item = EarningsCallchema().dump(ec)
            item['company_name'] = name_map.get(ec.stock_id)
            r = report_map.get(ec.id)
            item['summary'] = {
                'processing_status': r.processing_status if r else None,
                'score': r.score if r else None,
                'sentiment': r.sentiment if r else None,
            }
            result.append(item)

        if is_paginated:
            return jsonify({
                'earnings_calls': result,
                'total': pagination_or_list.total,
                'page': pagination_or_list.page,
                'pages': pagination_or_list.pages,
                'has_next': pagination_or_list.has_next,
            })

        return jsonify(result)

    @api_auth_required
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
            return jsonify({"error": "Resource already exists"}), 409

        try:
            earnings_call = earnings_call_service.create_earnings_call(earnings_call_data)
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating earnings call: {e}", exc_info=True)
            return jsonify({"error": "Failed to create earnings call"}), 400
        else:
            return jsonify(EarningsCallchema().dump(earnings_call)), 201


class EarningsCallDetailApi(MethodView):
    @jwt_required()
    def get(self):
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
        return jsonify(EarningsCallchema().dump(earnings_call))

    @jwt_required()
    def delete(self, earnings_call_id):
        earnings_call_service.delete_earnings_call(earnings_call_id)
        return '', 204


class EarningsCallPendingApi(MethodView):
    """API to get earnings calls pending AI summary."""

    @api_auth_required
    def get(self):
        meeting_date_str = request.args.get('meeting_date')
        if not meeting_date_str:
            return jsonify({"error": "meeting_date parameter is required"}), 400

        try:
            meeting_date = datetime.strptime(meeting_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400

        pending = earnings_call_service.get_pending_earnings_calls(meeting_date)
        return jsonify(EarningsCallchema(many=True).dump(pending))


class EarningsCallFeedsApi(MethodView):
    """API to get related feeds for an earnings call."""

    @api_auth_required
    def get(self, earnings_call_id):
        from app.schemas.feed_schema import FeedSchema

        earnings_call = earnings_call_service.get_earnings_call(earnings_call_id)
        if not earnings_call:
            return jsonify({"error": "Earnings call not found"}), 404

        days_after = request.args.get('days_after', 1, type=int)
        keywords_str = request.args.get('keywords', None)
        keywords = [kw.strip() for kw in keywords_str.split(',') if kw.strip()] if keywords_str else None

        feeds = earnings_call_service.get_related_feeds(
            earnings_call.stock_id,
            earnings_call.meeting_date,
            days_after=days_after,
            keywords=keywords,
        )

        return jsonify({
            "earnings_call_id": earnings_call_id,
            "stock_id": earnings_call.stock_id,
            "meeting_date": earnings_call.meeting_date.isoformat(),
            "feeds_count": len(feeds),
            "feeds": FeedSchema(many=True).dump(feeds)
        })


class EarningsCallBoundFeedsApi(MethodView):
    """Return feeds that were actually used in the AI analysis for this earnings call."""
    decorators = [jwt_required()]

    def get(self, earnings_call_id):
        earnings_call = earnings_call_service.get_earnings_call(earnings_call_id)
        if not earnings_call:
            return jsonify({"error": "Earnings call not found"}), 404

        bound_feeds = earnings_call_service.get_bound_feeds(earnings_call_id)
        return jsonify(bound_feeds)


earnings_call.add_url_rule('/pending',
    view_func=EarningsCallPendingApi.as_view('EarningsCallPendingApi'),
    methods=['GET'])

earnings_call.add_url_rule('',
    view_func=EarningsCallListApi.as_view('EarningsCallListApi'),
    methods=['GET', 'POST'])

earnings_call.add_url_rule('/<int:earnings_call_id>/feeds',
    view_func=EarningsCallFeedsApi.as_view('EarningsCallFeedsApi'),
    methods=['GET'])

earnings_call.add_url_rule('/<int:earnings_call_id>/bound_feeds',
    view_func=EarningsCallBoundFeedsApi.as_view('EarningsCallBoundFeedsApi'),
    methods=['GET'])
