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

    def get_stock_all_earnings_call(self, stock_id, meeting_date):
        earning_call_query = EarningsCall.query
        if stock_id:
            earning_call_query = earning_call_query.filter_by(stock_id=stock_id)

        if meeting_date:
            earning_call_query = earning_call_query.filter(
                EarningsCall.meeting_date <= meeting_date)

        return earning_call_query.order_by(
                    EarningsCall.meeting_date.desc()).limit(self.earnings_call_data_size).all()

    def get_stock_earnings_call_by_date(self, stock_id, meeting_date):
        earning_call_query = EarningsCall.query
        if stock_id:
            earning_call_query = earning_call_query.filter_by(stock_id=stock_id)

        if meeting_date:
            earning_call_query = earning_call_query.filter(
                EarningsCall.meeting_date==meeting_date)

        return earning_call_query.all()

    def create_earnings_call(self, earnings_call_data):
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
        else:
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

    def get_related_feeds(self, stock_id, meeting_date, days_after=3):
        """Get related news feeds after the earnings call."""
        from datetime import timedelta
        end_date = meeting_date + timedelta(days=days_after)

        return Feed.query.filter(
            Feed.stock_id == stock_id,
            Feed.releaseTime >= meeting_date,
            Feed.releaseTime <= end_date
        ).order_by(Feed.releaseTime.desc()).all()

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
