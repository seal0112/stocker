from app.log_config import get_logger
from datetime import datetime

from flask import request, jsonify, current_app
from flask.views import MethodView
from flask_jwt_extended import jwt_required

from . import ai_report
from .serializer import AiReportSchema
from .ai_report_service import AiReportService
from ..decorators.auth import api_auth_required
from ..schemas.feed_schema import FeedSchema
from ..earnings_call.serializer import EarningsCallchema

logger = get_logger(__name__)
ai_report_service = AiReportService()


class AiReportListApi(MethodView):

    @jwt_required()
    def get(self):
        report_type = request.args.get('report_type')
        subject = request.args.get('subject')
        ref_id = request.args.get('ref_id', type=int)
        processing_status = request.args.get('processing_status')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        page = request.args.get('page', None, type=int)
        page_size = request.args.get('page_size', 20, type=int)

        result = ai_report_service.list_ai_reports(
            report_type=report_type,
            subject=subject,
            ref_id=ref_id,
            processing_status=processing_status,
            date_from=date_from,
            date_to=date_to,
            page=page,
            page_size=page_size,
        )

        if page is not None:
            return jsonify({
                'reports': AiReportSchema(many=True).dump(result.items),
                'total': result.total,
                'page': result.page,
                'pages': result.pages,
                'has_next': result.has_next,
            })
        return jsonify(AiReportSchema(many=True).dump(result))

    @api_auth_required
    def post(self):
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Request body is required"}), 400
        except Exception:
            return jsonify({"error": "Invalid JSON format"}), 400

        try:
            if 'period_start' in data and isinstance(data['period_start'], str):
                data['period_start'] = datetime.strptime(data['period_start'], '%Y-%m-%d').date()
            if 'period_end' in data and isinstance(data['period_end'], str):
                data['period_end'] = datetime.strptime(data['period_end'], '%Y-%m-%d').date()

            # For earnings_call type, look up meeting_date if not provided
            if data.get('report_type') == 'earnings_call' and data.get('ref_id'):
                from ..earnings_call.models import EarningsCall
                ec = EarningsCall.query.get(data['ref_id'])
                if not ec:
                    return jsonify({"error": "Earnings call not found"}), 404
                if 'subject' not in data:
                    data['subject'] = ec.stock_id
                if 'period_start' not in data:
                    data['period_start'] = ec.meeting_date
                if 'period_end' not in data:
                    data['period_end'] = ec.meeting_date
                if 'prompt_name' not in data:
                    data['prompt_name'] = 'earnings-call-summary'

            existing = ai_report_service.get_ai_report_by_ref(data['ref_id']) if data.get('ref_id') and data.get('report_type') == 'earnings_call' else None
            if existing:
                return jsonify(AiReportSchema().dump(existing)), 200

            report = ai_report_service.create_ai_report(data)
        except Exception as e:
            logger.error(f"Error creating ai_report: {e}", exc_info=True)
            return jsonify({"error": "Failed to create report"}), 400

        # For earnings_call type, also send to SQS for AI processing
        if data.get('report_type') == 'earnings_call':
            try:
                import json, boto3
                queue_url = current_app.config.get('EARNINGS_CALL_SUMMARY_QUEUE_URL')
                if queue_url:
                    sqs = boto3.client('sqs', region_name=current_app.config.get('AWS_REGION', 'ap-northeast-1'))
                    sqs.send_message(
                        QueueUrl=queue_url,
                        MessageBody=json.dumps({
                            'ai_report_id': report.id,
                            'earnings_call_id': report.ref_id,
                            'stock_id': report.subject,
                            'meeting_date': report.period_start.isoformat(),
                            'days_after': data.get('days_after', 2),
                        })
                    )
                    logger.info(f"Sent ai_report {report.id} (earnings_call {report.ref_id}) to SQS")
            except Exception as e:
                logger.error(f"Failed to send to SQS: {e}", exc_info=True)

        return jsonify(AiReportSchema().dump(report)), 201


class AiReportDetailApi(MethodView):

    @jwt_required()
    def get(self, report_id):
        report = ai_report_service.get_ai_report(report_id)
        if not report:
            return jsonify({"error": "Report not found"}), 404
        return jsonify(AiReportSchema().dump(report))

    @api_auth_required
    def put(self, report_id):
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Request body is required"}), 400
        except Exception:
            return jsonify({"error": "Invalid JSON format"}), 400

        try:
            report = ai_report_service.update_ai_report(report_id, data)
            if not report:
                return jsonify({"error": "Report not found"}), 404
        except Exception as e:
            logger.error(f"Error updating ai_report {report_id}: {e}", exc_info=True)
            return jsonify({"error": "Failed to update report"}), 400

        return jsonify(AiReportSchema().dump(report))


class AiReportDueApi(MethodView):
    decorators = [api_auth_required]

    def get(self):
        due = ai_report_service.get_due_reports()
        return jsonify(due)


class AiReportFeedsApi(MethodView):
    decorators = [api_auth_required]

    def get(self):
        source = request.args.get('source')
        start_str = request.args.get('start')
        end_str = request.args.get('end')

        if not source or not start_str or not end_str:
            return jsonify({"error": "source, start, end are required"}), 400

        try:
            period_start = datetime.strptime(start_str, '%Y-%m-%d').date()
            period_end = datetime.strptime(end_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400

        feeds = ai_report_service.get_news_feeds(source, period_start, period_end)
        return jsonify(FeedSchema(many=True).dump(feeds))


class AiReportCompletedApi(MethodView):
    """Return completed earnings_call ai_reports for a given date (for notification Lambda)."""
    decorators = [api_auth_required]

    def get(self):
        date_str = request.args.get('date')
        if not date_str:
            return jsonify({"error": "date parameter is required"}), 400

        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400

        from ..database_setup import BasicInformation
        from ..earnings_call.models import EarningsCall

        reports = ai_report_service.get_completed_earnings_call_reports(target_date)
        stock_ids = {r.subject for r in reports}
        name_map = {
            b.id: getattr(b, '公司簡稱', None)
            for b in BasicInformation.query.filter(BasicInformation.id.in_(stock_ids)).all()
        }
        ec_map = {
            ec.id: ec
            for ec in EarningsCall.query.filter(
                EarningsCall.id.in_([r.ref_id for r in reports if r.ref_id])
            ).all()
        }

        result = []
        for r in reports:
            kp = r.key_points or {}
            ec = ec_map.get(r.ref_id)
            result.append({
                'ai_report_id': r.id,
                'earnings_call_id': r.ref_id,
                'stock_id': r.subject,
                'company_name': name_map.get(r.subject),
                'meeting_date': ec.meeting_date.isoformat() if ec else None,
                'score': r.score,
                'sentiment': r.sentiment,
                'impact_duration': kp.get('impact_duration'),
                'source_reliability': kp.get('source_reliability'),
                'outlook': kp.get('outlook'),
                'concerns_and_risks': kp.get('concerns_and_risks'),
                'capex': kp.get('capex'),
                'capex_industry': kp.get('capex_industry'),
                'reasoning': r.summary,
            })
        return jsonify(result)


class AiReportFailedRetryApi(MethodView):
    """Return earnings calls with failed ai_reports for retry (for trigger Lambda)."""
    decorators = [api_auth_required]

    def get(self):
        days_back = request.args.get('days_back', 3, type=int)
        from ..earnings_call.models import EarningsCall
        failed_reports = ai_report_service.get_failed_earnings_call_reports(days_back=days_back)
        ref_ids = [r.ref_id for r in failed_reports if r.ref_id]
        if not ref_ids:
            return jsonify([])
        ec_map = {ec.id: ec for ec in EarningsCall.query.filter(EarningsCall.id.in_(ref_ids)).all()}
        report_by_ref = {r.ref_id: r for r in failed_reports}

        result = []
        for ref_id in ref_ids:
            ec = ec_map.get(ref_id)
            r = report_by_ref.get(ref_id)
            if ec and r:
                result.append({
                    'id': ec.id,
                    'stock_id': ec.stock_id,
                    'meeting_date': ec.meeting_date.isoformat(),
                    'ai_report_id': r.id,
                })
        return jsonify(result)


ai_report.add_url_rule('',
    view_func=AiReportListApi.as_view('AiReportListApi'),
    methods=['GET', 'POST'])

ai_report.add_url_rule('/due',
    view_func=AiReportDueApi.as_view('AiReportDueApi'),
    methods=['GET'])

ai_report.add_url_rule('/feeds',
    view_func=AiReportFeedsApi.as_view('AiReportFeedsApi'),
    methods=['GET'])

ai_report.add_url_rule('/completed',
    view_func=AiReportCompletedApi.as_view('AiReportCompletedApi'),
    methods=['GET'])

ai_report.add_url_rule('/failed_retry',
    view_func=AiReportFailedRetryApi.as_view('AiReportFailedRetryApi'),
    methods=['GET'])

ai_report.add_url_rule('/<int:report_id>',
    view_func=AiReportDetailApi.as_view('AiReportDetailApi'),
    methods=['GET', 'PUT'])
