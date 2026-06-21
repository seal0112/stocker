from app.log_config import get_logger
from datetime import date, datetime, timedelta

import pytz

from .. import db
from .models import AiReport
from ..ai_prompt.models import AiPrompt
from ..models import Feed

logger = get_logger(__name__)

TAIWAN_TZ = pytz.timezone('Asia/Taipei')


class AiReportService:

    def get_ai_report(self, report_id):
        return AiReport.query.filter_by(id=report_id).one_or_none()

    def get_ai_report_by_ref(self, ref_id):
        """Get earnings_call type report by earnings_call_id."""
        return AiReport.query.filter_by(
            report_type='earnings_call', ref_id=ref_id
        ).one_or_none()

    def list_ai_reports(self, report_type=None, subject=None, ref_id=None,
                        processing_status=None, date_from=None, date_to=None,
                        page=None, page_size=20):
        query = AiReport.query
        if report_type:
            query = query.filter(AiReport.report_type == report_type)
        if subject:
            query = query.filter(AiReport.subject == subject)
        if ref_id is not None:
            query = query.filter(AiReport.ref_id == ref_id)
        if processing_status:
            query = query.filter(AiReport.processing_status == processing_status)
        if date_from:
            query = query.filter(AiReport.period_start >= date_from)
        if date_to:
            query = query.filter(AiReport.period_end <= date_to)
        query = query.order_by(AiReport.period_start.desc())
        if page is not None:
            return query.paginate(page=page, per_page=page_size, error_out=False)
        return query.limit(100).all()

    def create_ai_report(self, data):
        report = AiReport(
            report_type=data['report_type'],
            subject=data['subject'],
            period_start=data['period_start'],
            period_end=data['period_end'],
            prompt_name=data.get('prompt_name', ''),
            ref_id=data.get('ref_id'),
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

    # Fields that belong inside key_points JSON (not top-level columns)
    _KEY_POINT_FIELDS = {
        'earnings_call': {
            'capex', 'capex_industry', 'outlook', 'concerns_and_risks',
            'impact_duration', 'source_reliability',
            'news_contributions', 'source_feed_ids',
        }
    }
    # Field name remapping: Lambda field → model column
    _FIELD_REMAP = {
        'reasoning': 'summary',
    }

    def update_ai_report(self, report_id, data):
        report = self.get_ai_report(report_id)
        if not report:
            return None

        kp_fields = self._KEY_POINT_FIELDS.get(report.report_type, set())
        key_points = dict(report.key_points or {})

        for key, value in data.items():
            remapped = self._FIELD_REMAP.get(key, key)
            if key in kp_fields:
                key_points[key] = value
            elif hasattr(report, remapped):
                setattr(report, remapped, value)

        if key_points:
            report.key_points = key_points

        try:
            db.session.commit()
        except Exception as ex:
            db.session.rollback()
            logger.error(ex)
            raise ex
        return report

    def get_due_reports(self):
        """Return list of AiPrompt schedules that are due now (Taiwan time)."""
        now_tw = datetime.now(TAIWAN_TZ)
        prompts = AiPrompt.query.filter_by(schedule_enabled=True).all()
        due = []
        for p in prompts:
            if p.schedule_frequency == 'weekly':
                if now_tw.weekday() != p.schedule_day:
                    continue
            elif p.schedule_frequency == 'monthly':
                if now_tw.day != p.schedule_day:
                    continue
            if p.schedule_hour is not None and now_tw.hour != p.schedule_hour:
                continue
            days_back = p.schedule_days_back or 7
            period_start = now_tw.date() - timedelta(days=days_back)
            period_end = now_tw.date()
            # Skip if already completed for this period
            existing = AiReport.query.filter_by(
                report_type='news',
                subject=p.report_source,
                period_start=period_start,
                period_end=period_end,
            ).one_or_none()
            if existing and existing.processing_status == 'completed':
                continue
            due.append({
                'prompt_name': p.name,
                'source': p.report_source,
                'period_start': period_start.isoformat(),
                'period_end': period_end.isoformat(),
                'existing_report_id': existing.id if existing else None,
            })
        return due

    def get_completed_earnings_call_reports(self, date):
        """Get completed earnings_call ai_reports for a given meeting date."""
        return (
            AiReport.query
            .filter(
                AiReport.report_type == 'earnings_call',
                AiReport.processing_status == 'completed',
                AiReport.period_start == date,
            )
            .all()
        )

    def get_failed_earnings_call_reports(self, days_back=3):
        """Get failed earnings_call ai_reports from the past N days."""
        from datetime import timedelta
        date_from = date.today() - timedelta(days=days_back)
        return (
            AiReport.query
            .filter(
                AiReport.report_type == 'earnings_call',
                AiReport.processing_status == 'failed',
                AiReport.period_start >= date_from,
                AiReport.period_start < date.today(),
            )
            .all()
        )

    def get_news_feeds(self, source, period_start, period_end):
        """Get feeds for a given source and date range."""
        from datetime import datetime as dt
        start_dt = dt.combine(period_start, dt.min.time())
        end_dt = dt.combine(period_end, dt.max.time())
        feeds = Feed.query.filter(
            Feed.source == source,
            Feed.releaseTime >= start_dt,
            Feed.releaseTime <= end_dt,
        ).order_by(Feed.releaseTime.desc()).limit(100).all()
        return feeds
