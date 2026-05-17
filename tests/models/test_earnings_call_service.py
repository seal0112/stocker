"""Tests for EarningsCallService business logic."""
import pytest
from datetime import date, datetime, timedelta

from app import db
from app.earnings_call.models import EarningsCall, EarningsCallSummary
from app.earnings_call.earnings_call_services import EarningsCallService
from app.models import Feed


service = EarningsCallService()

MEETING_DATE = date(2024, 6, 15)


@pytest.fixture
def ec(test_app, sample_basic_info):
    obj = EarningsCall(
        stock_id=sample_basic_info.id,
        meeting_date=MEETING_DATE,
        meeting_end_date=MEETING_DATE,
        location='台北',
        description='法說會',
        file_name_chinese='test'
    )
    db.session.add(obj)
    db.session.commit()
    yield obj
    EarningsCall.query.filter_by(id=obj.id).delete()
    db.session.commit()


@pytest.fixture
def feeds_near_ec(test_app, sample_basic_info, ec):
    """Three feeds: one matching keyword, one not, one outside time window."""
    meeting_dt = datetime.combine(MEETING_DATE, datetime.min.time())
    f1 = Feed(
        stock_id=sample_basic_info.id,
        releaseTime=meeting_dt + timedelta(hours=2),
        title='台積電法說會：展望樂觀',
        link='https://test.com/feed1',
        source='mops', feedType='news'
    )
    f2 = Feed(
        stock_id=sample_basic_info.id,
        releaseTime=meeting_dt + timedelta(hours=4),
        title='台積電月營收公告',   # no keyword match
        link='https://test.com/feed2',
        source='mops', feedType='news'
    )
    f3 = Feed(
        stock_id=sample_basic_info.id,
        releaseTime=meeting_dt + timedelta(days=3),  # outside 1-day window
        title='台積電展望更新',
        link='https://test.com/feed3',
        source='mops', feedType='news'
    )
    db.session.add_all([f1, f2, f3])
    db.session.commit()
    yield f1, f2, f3
    for f in [f1, f2, f3]:
        Feed.query.filter_by(id=f.id).delete()
    db.session.commit()


class TestGetRelatedFeeds:

    def test_returns_feeds_within_window(self, test_app, ec, feeds_near_ec):
        f1, f2, f3 = feeds_near_ec
        results = service.get_related_feeds(ec.stock_id, MEETING_DATE, days_after=1)
        ids = [f.id for f in results]
        assert f1.id in ids
        assert f2.id in ids
        assert f3.id not in ids   # outside 1-day window

    def test_keyword_filter_or_logic(self, test_app, ec, feeds_near_ec):
        f1, f2, _ = feeds_near_ec
        results = service.get_related_feeds(
            ec.stock_id, MEETING_DATE, days_after=1, keywords=['法說會', '展望']
        )
        ids = [f.id for f in results]
        assert f1.id in ids   # title contains '法說會' and '展望'
        assert f2.id not in ids  # no keyword match

    def test_keyword_no_match_returns_empty(self, test_app, ec, feeds_near_ec):
        results = service.get_related_feeds(
            ec.stock_id, MEETING_DATE, days_after=1, keywords=['不存在關鍵字xyz']
        )
        assert results == []

    def test_extended_window_includes_later_feed(self, test_app, ec, feeds_near_ec):
        f1, f2, f3 = feeds_near_ec
        results = service.get_related_feeds(ec.stock_id, MEETING_DATE, days_after=5)
        ids = [f.id for f in results]
        assert f3.id in ids

    def test_limit_15(self, test_app, sample_basic_info, ec):
        """Should return at most 15 feeds."""
        meeting_dt = datetime.combine(MEETING_DATE, datetime.min.time())
        feeds = []
        for i in range(20):
            f = Feed(
                stock_id=sample_basic_info.id,
                releaseTime=meeting_dt + timedelta(hours=i),
                title=f'法說會新聞 {i}',
                link=f'https://test.com/bulk-{i}',
                source='mops', feedType='news'
            )
            feeds.append(f)
        db.session.add_all(feeds)
        db.session.commit()

        results = service.get_related_feeds(ec.stock_id, MEETING_DATE, days_after=1)
        assert len(results) <= 15

        for f in feeds:
            Feed.query.filter_by(id=f.id).delete()
        db.session.commit()


class TestGetPendingEarningsCalls:

    def test_no_summary_is_pending(self, test_app, ec):
        pending = service.get_pending_earnings_calls(MEETING_DATE)
        ids = [e.id for e in pending]
        assert ec.id in ids

    def test_completed_summary_excluded(self, test_app, ec):
        summary = EarningsCallSummary(
            earnings_call_id=ec.id,
            stock_id=ec.stock_id,
            processing_status='completed'
        )
        db.session.add(summary)
        db.session.commit()

        pending = service.get_pending_earnings_calls(MEETING_DATE)
        ids = [e.id for e in pending]
        assert ec.id not in ids

        EarningsCallSummary.query.filter_by(id=summary.id).delete()
        db.session.commit()

    def test_failed_summary_is_pending(self, test_app, ec):
        summary = EarningsCallSummary(
            earnings_call_id=ec.id,
            stock_id=ec.stock_id,
            processing_status='failed'
        )
        db.session.add(summary)
        db.session.commit()

        pending = service.get_pending_earnings_calls(MEETING_DATE)
        ids = [e.id for e in pending]
        assert ec.id in ids

        EarningsCallSummary.query.filter_by(id=summary.id).delete()
        db.session.commit()

    def test_different_date_excluded(self, test_app, ec):
        other_date = MEETING_DATE + timedelta(days=1)
        pending = service.get_pending_earnings_calls(other_date)
        ids = [e.id for e in pending]
        assert ec.id not in ids


class TestUpdateEarningsCallSummary:

    def test_updates_scoring_fields(self, test_app, ec):
        summary = EarningsCallSummary(
            earnings_call_id=ec.id,
            stock_id=ec.stock_id,
            processing_status='processing'
        )
        db.session.add(summary)
        db.session.commit()

        result = service.update_earnings_call_summary(ec.id, {
            'processing_status': 'completed',
            'score': 4,
            'sentiment': 'Strong Buy',
            'impact_duration': 'Long',
            'source_reliability': 'Official',
            'reasoning': '測試評分依據',
            'news_contributions': [{'feed_id': 1, 'title': '法說', 'score_delta': 4, 'key_insight': '利多'}],
        })

        assert result.processing_status == 'completed'
        assert result.score == 4
        assert result.sentiment == 'Strong Buy'
        assert result.impact_duration == 'Long'
        assert result.source_reliability == 'Official'
        assert result.reasoning == '測試評分依據'
        assert isinstance(result.news_contributions, list)

        EarningsCallSummary.query.filter_by(id=summary.id).delete()
        db.session.commit()

    def test_returns_none_when_not_found(self, test_app):
        result = service.update_earnings_call_summary(99999, {'score': 1})
        assert result is None
