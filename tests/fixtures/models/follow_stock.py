"""Follow_Stock model fixtures for testing."""
import pytest
from datetime import datetime
from app import db
from app.follow_stock.models import Follow_Stock


@pytest.fixture
def sample_follow_stock_long(test_app, regular_user, sample_basic_info):
    """Create a sample follow stock (long position) for testing."""
    with test_app.app_context():
        follow = Follow_Stock(
            user_id=regular_user.id,
            stock_id=sample_basic_info.id,
            long_or_short='long',
            comment='看好台積電長期成長',
            is_delete=False
        )
        db.session.add(follow)
        db.session.commit()

        yield follow

        # Cleanup
        db.session.delete(follow)
        db.session.commit()


@pytest.fixture
def sample_follow_stock_short(test_app, regular_user, sample_basic_info_2):
    """Create a sample follow stock (short position) for testing."""
    with test_app.app_context():
        follow = Follow_Stock(
            user_id=regular_user.id,
            stock_id=sample_basic_info_2.id,
            long_or_short='short',
            comment='觀察鴻海走勢',
            is_delete=False
        )
        db.session.add(follow)
        db.session.commit()

        yield follow

        # Cleanup
        db.session.delete(follow)
        db.session.commit()


@pytest.fixture
def sample_follow_stock_deleted(test_app, regular_user, sample_basic_info):
    """Create a deleted follow stock for testing soft delete."""
    with test_app.app_context():
        follow = Follow_Stock(
            user_id=regular_user.id,
            stock_id=sample_basic_info.id,
            long_or_short='long',
            comment='已取消追蹤',
            is_delete=True,
            remove_time=datetime.utcnow()
        )
        db.session.add(follow)
        db.session.commit()

        yield follow

        # Cleanup
        db.session.delete(follow)
        db.session.commit()


@pytest.fixture
def sample_follow_stock_list(test_app, regular_user, sample_basic_info_list):
    """Create multiple follow stocks for testing."""
    with test_app.app_context():
        follows = []
        positions = ['long', 'short', 'long']
        comments = ['看好', '觀察', '長期持有']

        for stock, position, comment in zip(sample_basic_info_list, positions, comments):
            follow = Follow_Stock(
                user_id=regular_user.id,
                stock_id=stock.id,
                long_or_short=position,
                comment=comment,
                is_delete=False
            )
            follows.append(follow)
            db.session.add(follow)
        db.session.commit()

        yield follows

        # Cleanup
        for follow in follows:
            db.session.delete(follow)
        db.session.commit()


@pytest.fixture
def admin_follow_stock(test_app, admin_user, sample_basic_info):
    """Create a follow stock for admin user."""
    with test_app.app_context():
        follow = Follow_Stock(
            user_id=admin_user.id,
            stock_id=sample_basic_info.id,
            long_or_short='long',
            comment='Admin 追蹤',
            is_delete=False
        )
        db.session.add(follow)
        db.session.commit()

        yield follow

        # Cleanup
        db.session.delete(follow)
        db.session.commit()
