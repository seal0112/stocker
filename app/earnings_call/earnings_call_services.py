from app.log_config import get_logger

from .models import EarningsCall
from .. import db
from ..models import Feed
from ..utils.data_update_date_service import DataUpdateDateService
from ..ai_report.models import AiReport


data_update_date_service = DataUpdateDateService()
logger = get_logger(__name__)


class EarningsCallService():

    def __init__(self):
        self.earnings_call_data_size = 20

    def get_stock_all_earnings_call(
        self, stock_id=None, meeting_date=None,
        date_from=None, date_to=None,
        score_min=None, score_max=None,
        page=None, page_size=20,
    ):
        from datetime import date, timedelta

        query = EarningsCall.query

        if stock_id:
            query = query.filter(EarningsCall.stock_id == stock_id)

        if meeting_date:
            query = query.filter(EarningsCall.meeting_date == meeting_date)
        elif not stock_id:
            # 全局列表才套預設日期範圍；個股頁不限制
            start = date_from or date.today()
            end = date_to or (date.today() + timedelta(days=90))
            query = query.filter(
                EarningsCall.meeting_date >= start,
                EarningsCall.meeting_date <= end,
            )
        elif date_from or date_to:
            if date_from:
                query = query.filter(EarningsCall.meeting_date >= date_from)
            if date_to:
                query = query.filter(EarningsCall.meeting_date <= date_to)

        if score_min is not None or score_max is not None:
            query = query.join(
                AiReport,
                (EarningsCall.id == AiReport.ref_id) & (AiReport.report_type == 'earnings_call')
            )
            if score_min is not None:
                query = query.filter(AiReport.score >= score_min)
            if score_max is not None:
                query = query.filter(AiReport.score <= score_max)

        query = query.order_by(EarningsCall.meeting_date.desc())

        if page is not None:
            return query.paginate(page=page, per_page=page_size, error_out=False)

        return query.limit(100).all()

    def get_stock_earnings_call_by_date(self, stock_id, meeting_date):
        earning_call_query = EarningsCall.query
        if stock_id:
            earning_call_query = earning_call_query.filter_by(stock_id=stock_id)

        if meeting_date:
            earning_call_query = earning_call_query.filter(
                EarningsCall.meeting_date==meeting_date)

        return earning_call_query.all()

    def create_earnings_call(self, earnings_call_data):
        from datetime import date
        earnings_call = EarningsCall()
        earnings_call.stock_id = earnings_call_data['stock_id']
        earnings_call.meeting_date = earnings_call_data['meeting_date']
        earnings_call.meeting_end_date = earnings_call_data['meeting_end_date']
        earnings_call.location = earnings_call_data['location']
        earnings_call.description = earnings_call_data['description']
        earnings_call.file_name_chinese = earnings_call_data['file_name_chinese']

        try:
            db.session.add(earnings_call)
            db.session.commit()
        except Exception as ex:
            db.session.rollback()
            logger.error(ex)
            raise ex

        meeting_date = earnings_call_data['meeting_date']
        if isinstance(meeting_date, str):
            from datetime import datetime
            meeting_date = datetime.strptime(meeting_date, '%Y-%m-%d').date()
        if meeting_date == date.today():
            data_update_date_service.update_earnings_call_update_date(earnings_call.stock_id)

        return earnings_call

    def get_earnings_call(self, earnings_call_id=None):
        return EarningsCall.query.filter_by(id=earnings_call_id).one_or_none()

    def update_earnings_call(self, earnings_call_id, earnings_call_data):
        earnings_call = self.get_earnings_call(earnings_call_id)
        if not earnings_call:
            return

        for key in earnings_call_data:
            earnings_call[key] = earnings_call_data[key]

        try:
            db.session.commit()
        except Exception as ex:
            db.session.rollback()
            logger.error(ex)

        return earnings_call

    def delete_earnings_call(self, earnings_call_id):
        try:
            EarningsCall.query.filter_by(id=earnings_call_id).delete()
        except Exception as ex:
            logger.error(ex)

    # Summary related methods (backed by AiReport table)
    def get_completed_summaries(self, date):
        """Get all completed ai_reports of earnings_call type for a given meeting date."""
        return (
            AiReport.query
            .filter(
                AiReport.report_type == 'earnings_call',
                AiReport.processing_status == 'completed',
                AiReport.period_start == date,
            )
            .all()
        )

    def get_earnings_call_summary(self, earnings_call_id):
        """Get ai_report for a specific earnings call."""
        return AiReport.query.filter_by(
            report_type='earnings_call', ref_id=earnings_call_id
        ).one_or_none()

    def create_earnings_call_summary(self, earnings_call_id, stock_id):
        """Create a pending ai_report for an earnings call."""
        existing = self.get_earnings_call_summary(earnings_call_id)
        if existing:
            return existing

        ec = self.get_earnings_call(earnings_call_id)
        meeting_date = ec.meeting_date if ec else None

        report = AiReport(
            report_type='earnings_call',
            subject=stock_id,
            period_start=meeting_date,
            period_end=meeting_date,
            prompt_name='earnings-call-summary',
            ref_id=earnings_call_id,
            processing_status='pending',
        )
        try:
            db.session.add(report)
            db.session.commit()
        except Exception as ex:
            db.session.rollback()
            logger.error(ex)
            raise ex
        return report

    def update_earnings_call_summary(self, earnings_call_id, summary_data):
        """Update ai_report with AI-generated content from Lambda."""
        report = self.get_earnings_call_summary(earnings_call_id)
        if not report:
            return None

        # Map flat summary_data fields into ai_report columns + key_points
        top_level = {
            'processing_status', 'error_message', 'score', 'sentiment',
            'raw_ai_response', 'input_tokens', 'output_tokens', 'total_tokens',
            'cost_usd', 'cost_twd', 'model_name',
        }
        key_point_fields = {
            'impact_duration', 'source_reliability', 'capex', 'capex_industry',
            'outlook', 'concerns_and_risks', 'news_contributions', 'source_feed_ids',
        }

        kp = dict(report.key_points or {})
        for key, value in summary_data.items():
            if key == 'reasoning':
                report.summary = value
            elif key in top_level:
                setattr(report, key, value)
            elif key in key_point_fields:
                kp[key] = value
        report.key_points = kp

        try:
            db.session.commit()
        except Exception as ex:
            db.session.rollback()
            logger.error(ex)
            raise ex
        return report

    def get_related_feeds(self, stock_id, meeting_date, days_after=1, keywords=None):
        """Get related news feeds after the earnings call."""
        from datetime import timedelta
        from sqlalchemy import or_
        end_date = meeting_date + timedelta(days=days_after)

        query = Feed.query.filter(
            Feed.stock_id == stock_id,
            Feed.releaseTime >= meeting_date,
            Feed.releaseTime <= end_date,
        )

        if keywords:
            query = query.filter(
                or_(*[Feed.title.contains(kw) for kw in keywords])
            )

        return query.order_by(Feed.releaseTime.desc()).limit(15).all()

    def get_bound_feeds(self, earnings_call_id):
        """Return feeds bound to this earnings call via news_contributions in ai_report."""
        report = self.get_earnings_call_summary(earnings_call_id)
        if not report or not report.key_points:
            return []
        news_contributions = report.key_points.get('news_contributions') or []
        if not news_contributions:
            return []

        feed_id_to_contribution = {
            nc['feed_id']: nc
            for nc in news_contributions
            if nc.get('feed_id')
        }
        if not feed_id_to_contribution:
            return []

        feeds = Feed.query.filter(Feed.id.in_(feed_id_to_contribution.keys())).all()

        result = []
        for feed in feeds:
            nc = feed_id_to_contribution[feed.id]
            result.append({
                'feed_id': feed.id,
                'title': feed.title,
                'link': feed.link,
                'releaseTime': feed.releaseTime.isoformat() if feed.releaseTime else None,
                'score_delta': nc.get('score_delta'),
                'key_insight': nc.get('key_insight'),
            })

        result.sort(key=lambda x: -(x['score_delta'] or 0))
        return result

    def get_failed_for_retry(self, days_back=3):
        """Get earnings calls with failed ai_reports from the past N days for retry."""
        from datetime import date, timedelta
        from sqlalchemy.orm import joinedload
        date_from = date.today() - timedelta(days=days_back)
        failed_reports = (
            AiReport.query
            .filter(
                AiReport.report_type == 'earnings_call',
                AiReport.processing_status == 'failed',
                AiReport.period_start >= date_from,
                AiReport.period_start < date.today(),
            )
            .all()
        )
        ref_ids = [r.ref_id for r in failed_reports if r.ref_id]
        if not ref_ids:
            return []
        return (
            EarningsCall.query
            .filter(EarningsCall.id.in_(ref_ids))
            .all()
        )

    def get_pending_earnings_calls(self, meeting_date):
        """Get earnings calls that need AI summary processing."""
        earnings_calls = EarningsCall.query.filter(
            EarningsCall.meeting_date == meeting_date
        ).all()

        pending = []
        for ec in earnings_calls:
            report = self.get_earnings_call_summary(ec.id)
            if report is None or report.processing_status in ('pending', 'failed'):
                pending.append(ec)

        return pending
