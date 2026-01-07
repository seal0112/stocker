"""PushNotification model fixtures for testing."""
import pytest
from datetime import time
from app import db
from app.database_setup import PushNotification


@pytest.fixture
def sample_push_notification_enabled(test_app, regular_user):
    """Create a push notification with all notifications enabled."""
    with test_app.app_context():
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

        # Cleanup
        db.session.delete(notification)
        db.session.commit()


@pytest.fixture
def sample_push_notification_disabled(test_app, admin_user):
    """Create a push notification with notifications disabled."""
    with test_app.app_context():
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

        # Cleanup
        db.session.delete(notification)
        db.session.commit()


@pytest.fixture
def sample_push_notification_partial(test_app, moderator_user):
    """Create a push notification with partial notifications enabled."""
    with test_app.app_context():
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

        # Cleanup
        db.session.delete(notification)
        db.session.commit()
