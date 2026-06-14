from app.log_config import get_logger

from .models import EarningsCall, EarningsCallSummary
from .. import db
from ..models import Feed
from ..utils.data_update_date_service import DataUpdateDateService


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
        from sqlalchemy.orm import joinedload

        query = EarningsCall.query.options(joinedload(EarningsCall.summary))

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
                EarningsCallSummary,
                EarningsCall.id == EarningsCallSummary.earnings_call_id
            )
            if score_min is not None:
                query = query.filter(EarningsCallSummary.score >= score_min)
            if score_max is not None:
                query = query.filter(EarningsCallSummary.score <= score_max)

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

    # Summary related methods
    def get_completed_summaries(self, date):
        """Get all completed summaries for a given date (for notification Lambda)."""
        from sqlalchemy.orm import joinedload
        summaries = (
            EarningsCallSummary.query
            .join(EarningsCall, EarningsCallSummary.earnings_call_id == EarningsCall.id)
            .options(joinedload(EarningsCallSummary.earnings_call))
            .filter(
                EarningsCallSummary.processing_status == 'completed',
                EarningsCall.meeting_date == date,
            )
            .all()
        )
        return summaries

    def get_earnings_call_summary(self, earnings_call_id):
        """Get summary for a specific earnings call."""
        return EarningsCallSummary.query.filter_by(
            earnings_call_id=earnings_call_id).one_or_none()

    def create_earnings_call_summary(self, earnings_call_id, stock_id):
        """Create a pending summary record for an earnings call."""
        existing = self.get_earnings_call_summary(earnings_call_id)
        if existing:
            return existing

        summary = EarningsCallSummary(
            earnings_call_id=earnings_call_id,
            stock_id=stock_id,
            processing_status='pending'
        )

        try:
            db.session.add(summary)
            db.session.commit()
        except Exception as ex:
            db.session.rollback()
            logger.error(ex)
            raise ex

        return summary

    def update_earnings_call_summary(self, earnings_call_id, summary_data):
        """Update summary with AI-generated content."""
        summary = self.get_earnings_call_summary(earnings_call_id)
        if not summary:
            return None

        # Update fields
        for key, value in summary_data.items():
            if hasattr(summary, key):
                setattr(summary, key, value)

        try:
            db.session.commit()
        except Exception as ex:
            db.session.rollback()
            logger.error(ex)
            raise ex

        return summary

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
        """Return feeds bound to this earnings call via news_contributions in summary."""
        summary = self.get_earnings_call_summary(earnings_call_id)
        if not summary or not summary.news_contributions:
            return []

        feed_id_to_contribution = {
            nc['feed_id']: nc
            for nc in summary.news_contributions
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

    def get_pending_earnings_calls(self, meeting_date):
        """Get earnings calls that need AI summary processing."""
        from sqlalchemy import or_

        # Find earnings calls on the given date that:
        # 1. Have no summary record, OR
        # 2. Have summary with status 'pending' or 'failed'
        earnings_calls = EarningsCall.query.filter(
            EarningsCall.meeting_date == meeting_date
        ).all()

        pending = []
        for ec in earnings_calls:
            summary = self.get_earnings_call_summary(ec.id)
            if summary is None or summary.processing_status in ('pending', 'failed'):
                pending.append(ec)

        return pending
