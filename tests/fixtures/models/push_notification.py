"""PushNotification model fixtures for testing.

Architecture:
- Depends on user fixtures and app_context
- Each fixture cleans up ONLY the records it creates
"""
import pytest
from datetime import time
from app import db
from app.database_setup import PushNotification


@pytest.fixture
def sample_push_notification_enabled(app_context, regular_user):
    """Create a push notification with all notifications enabled.

    Depends on: app_context, regular_user
    """
    notification = PushNotification(
        user_id=regular_user.id,
        notify_enabled=True,
        gmail='test@gmail.com',
        gmail_token='test_token_123',
        notify_time=time(hour=9, minute=0),
        notify_news=True,
        notify_announcement=True,
        notify_month_revenue=True,
        notify_income_sheet=True,
        notify_earnings_call=True
    )
    db.session.add(notification)
    db.session.commit()

    yield notification

    # Explicit cleanup
    PushNotification.query.filter_by(user_id=regular_user.id).delete()
    db.session.commit()


@pytest.fixture
def sample_push_notification_disabled(app_context, admin_user):
    """Create a push notification with notifications disabled.

    Depends on: app_context, admin_user
    """
    notification = PushNotification(
        user_id=admin_user.id,
        notify_enabled=False,
        gmail='admin@gmail.com',
        notify_time=time(hour=20, minute=0),
        notify_news=False,
        notify_announcement=False,
        notify_month_revenue=False,
        notify_income_sheet=False,
        notify_earnings_call=False
    )
    db.session.add(notification)
    db.session.commit()

    yield notification

    # Explicit cleanup
    PushNotification.query.filter_by(user_id=admin_user.id).delete()
    db.session.commit()


@pytest.fixture
def sample_push_notification_partial(app_context, moderator_user):
    """Create a push notification with partial notifications enabled.

    Depends on: app_context, moderator_user
    """
    notification = PushNotification(
        user_id=moderator_user.id,
        notify_enabled=True,
        gmail='moderator@gmail.com',
        notify_time=time(hour=18, minute=30),
        notify_news=True,
        notify_announcement=True,
        notify_month_revenue=False,
        notify_income_sheet=False,
        notify_earnings_call=True
    )
    db.session.add(notification)
    db.session.commit()

    yield notification

    # Explicit cleanup
    PushNotification.query.filter_by(user_id=moderator_user.id).delete()
    db.session.commit()
