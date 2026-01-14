"""Follow_Stock model fixtures for testing.

Architecture:
- Depends on sample_basic_info (which depends on app_context) and user fixtures
- Each fixture cleans up ONLY the records it creates
"""
import pytest
from datetime import datetime
from app import db
from app.follow_stock.models import Follow_Stock


@pytest.fixture
def sample_follow_stock_long(app_context, regular_user, sample_basic_info):
    """Create a sample follow stock (long position) for testing.

    Depends on: app_context, regular_user, sample_basic_info
    """
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

    # Explicit cleanup
    Follow_Stock.query.filter_by(
        user_id=regular_user.id,
        stock_id=sample_basic_info.id,
        long_or_short='long'
    ).delete()
    db.session.commit()


@pytest.fixture
def sample_follow_stock_short(app_context, regular_user, sample_basic_info_2):
    """Create a sample follow stock (short position) for testing.

    Depends on: app_context, regular_user, sample_basic_info_2
    """
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

    # Explicit cleanup
    Follow_Stock.query.filter_by(
        user_id=regular_user.id,
        stock_id=sample_basic_info_2.id,
        long_or_short='short'
    ).delete()
    db.session.commit()


@pytest.fixture
def sample_follow_stock_deleted(app_context, regular_user, sample_basic_info):
    """Create a deleted follow stock for testing soft delete.

    Depends on: app_context, regular_user, sample_basic_info
    """
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

    # Explicit cleanup
    Follow_Stock.query.filter_by(
        user_id=regular_user.id,
        stock_id=sample_basic_info.id,
        is_delete=True
    ).delete()
    db.session.commit()


@pytest.fixture
def sample_follow_stock_list(app_context, regular_user, sample_basic_info_list):
    """Create multiple follow stocks for testing.

    Depends on: app_context, regular_user, sample_basic_info_list
    """
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

    # Explicit cleanup
    stock_ids = [stock.id for stock in sample_basic_info_list]
    Follow_Stock.query.filter(
        Follow_Stock.user_id == regular_user.id,
        Follow_Stock.stock_id.in_(stock_ids)
    ).delete()
    db.session.commit()


@pytest.fixture
def admin_follow_stock(app_context, admin_user, sample_basic_info):
    """Create a follow stock for admin user.

    Depends on: app_context, admin_user, sample_basic_info
    """
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

    # Explicit cleanup
    Follow_Stock.query.filter_by(
        user_id=admin_user.id,
        stock_id=sample_basic_info.id
    ).delete()
    db.session.commit()
