from app.log_config import get_logger
from datetime import datetime

from flask import request, jsonify
from flask.views import MethodView
from flask_jwt_extended import jwt_required

from app import db
from . import earnings_call
from .serializer import EarningsCallchema, EarningsCallSummarySchema
from .earnings_call_services import EarningsCallService
from app.decorators.auth import api_auth_required, admin_required

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

        earnings_calls = earnings_call_service.get_stock_all_earnings_call(
            stock_id=stock,
            meeting_date=meeting_date,
            date_from=date_from,
            date_to=date_to,
            score_min=score_min,
            score_max=score_max,
        )

        from app.database_setup import BasicInformation
        stock_ids = {ec.stock_id for ec in earnings_calls}
        name_map = {
            b.id: getattr(b, '公司簡稱', None)
            for b in BasicInformation.query.filter(BasicInformation.id.in_(stock_ids)).all()
        }

        result = []
        for ec in earnings_calls:
            item = EarningsCallchema().dump(ec)
            item['company_name'] = name_map.get(ec.stock_id)
            s = ec.summary
            item['summary'] = {
                'processing_status': s.processing_status if s else None,
                'score': s.score if s else None,
                'sentiment': s.sentiment if s else None,
            }
            result.append(item)

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


class EarningsCallSummaryApi(MethodView):
    """API for earnings call AI summary."""

    def get(self, earnings_call_id):
        """Get AI summary for an earnings call."""
        summary = earnings_call_service.get_earnings_call_summary(earnings_call_id)
        if not summary:
            return jsonify({"error": "Summary not found"}), 404

        return jsonify(EarningsCallSummarySchema().dump(summary))

    @api_auth_required
    def put(self, earnings_call_id):
        """Update summary with AI-generated content (Lambda callback)."""
        try:
            summary_data = request.get_json()
            if not summary_data:
                return jsonify({"error": "Request body is required"}), 400
        except Exception:
            return jsonify({"error": "Invalid JSON format"}), 400

        try:
            summary = earnings_call_service.update_earnings_call_summary(
                earnings_call_id, summary_data)
            if not summary:
                return jsonify({"error": "Summary not found"}), 404
        except Exception as e:
            logger.error(f"Error updating summary: {e}", exc_info=True)
            return jsonify({"error": "Failed to update summary"}), 400

        return jsonify(EarningsCallSummarySchema().dump(summary))

    @admin_required
    def post(self, earnings_call_id):
        """Trigger AI summary generation (creates pending record and sends to SQS)."""
        earnings_call = earnings_call_service.get_earnings_call(earnings_call_id)
        if not earnings_call:
            return jsonify({"error": "Earnings call not found"}), 404

        try:
            summary = earnings_call_service.create_earnings_call_summary(
                earnings_call_id, earnings_call.stock_id)
        except Exception as e:
            logger.error(f"Error creating summary: {e}", exc_info=True)
            return jsonify({"error": "Failed to create summary"}), 400

        try:
            import json
            import boto3
            from flask import current_app
            queue_url = current_app.config.get('EARNINGS_CALL_SUMMARY_QUEUE_URL')
            if queue_url:
                sqs = boto3.client('sqs', region_name=current_app.config.get('AWS_REGION', 'ap-northeast-1'))
                sqs.send_message(
                    QueueUrl=queue_url,
                    MessageBody=json.dumps({
                        'earnings_call_id': earnings_call_id,
                        'stock_id': earnings_call.stock_id,
                        'meeting_date': earnings_call.meeting_date.isoformat(),
                        'days_after': 2,
                    })
                )
                logger.info(f"Sent earnings call {earnings_call_id} to SQS for AI processing")
            else:
                logger.warning("EARNINGS_CALL_SUMMARY_QUEUE_URL not configured, skipping SQS")
        except Exception as e:
            logger.error(f"Failed to send to SQS: {e}", exc_info=True)
            # Don't fail the request; record is created, Lambda trigger can pick it up

        return jsonify(EarningsCallSummarySchema().dump(summary)), 201


class EarningsCallPendingApi(MethodView):
    """API to get earnings calls pending AI summary."""

    @api_auth_required
    def get(self):
        """Get earnings calls that need AI summary processing."""
        meeting_date_str = request.args.get('meeting_date')
        if not meeting_date_str:
            return jsonify({"error": "meeting_date parameter is required"}), 400

        try:
            meeting_date = datetime.strptime(meeting_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400

        pending = earnings_call_service.get_pending_earnings_calls(meeting_date)
        return jsonify(EarningsCallchema(many=True).dump(pending))


earnings_call.add_url_rule('/pending',
    view_func=EarningsCallPendingApi.as_view('EarningsCallPendingApi'),
    methods=['GET'])

earnings_call.add_url_rule('',
    view_func=EarningsCallListApi.as_view('EarningsCallListApi'),
    methods=['GET', 'POST'])

class EarningsCallFeedsApi(MethodView):
    """API to get related feeds for an earnings call."""

    @api_auth_required
    def get(self, earnings_call_id):
        """Get related news feeds after an earnings call."""
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


earnings_call.add_url_rule('/<int:earnings_call_id>/summary',
    view_func=EarningsCallSummaryApi.as_view('EarningsCallSummaryApi'),
    methods=['GET', 'PUT', 'POST'])

earnings_call.add_url_rule('/<int:earnings_call_id>/feeds',
    view_func=EarningsCallFeedsApi.as_view('EarningsCallFeedsApi'),
    methods=['GET'])

# earnings_call.add_url_rule('/<earnings_call_id>',
#     view_func=EarningsCallDetailApi.as_view(
#     'earnings_call_detail_api'),
#     methods=['GET', 'PATCH'])