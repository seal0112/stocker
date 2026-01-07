import pytest
import os

from sqlalchemy import create_engine, text
from app import create_app, db


@pytest.fixture(scope='module')
def dev_app():
    """development environment app fixture"""
    app = create_app('development')

    with app.app_context():
        yield app


@pytest.fixture(scope='module')
def test_app():
    app = create_app('testing')

    test_db_url = app.config['SQLALCHEMY_DATABASE_URI']
    db_name = os.environ.get('DB_NAME', 'stocker') + '_test'

    with app.app_context():
        # Create test database if not exists
        engine = create_engine(test_db_url.rsplit('/', 1)[0])
        with engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name}"))

        # Drop all tables first to ensure clean state
        db.drop_all()
        # Create all tables from models (skip migrations for tests)
        db.create_all()

        ctx = app.test_request_context()
        ctx.push()

        yield app

        # Cleanup
        ctx.pop()
        db.session.remove()
        db.drop_all()


@pytest.fixture
def dev_client(dev_app):
    """test environment app fixture"""
    with dev_app.test_client() as client:
        yield client


@pytest.fixture()
def client(test_app):
    with test_app.test_client() as client:
        yield client


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def db_session(app):
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()

        options = dict(bind=connection, binds={})
        session = db.create_scoped_session(options=options)
        db.session = session

        yield db.session

        transaction.rollback()
        connection.close()
        session.remove()


# ============================================================================
# Import fixtures from fixtures package
# ============================================================================
# Pytest automatically discovers fixtures from this file and conftest.py files
# in subdirectories. We use pytest_plugins to load fixtures from other modules.
# ============================================================================

pytest_plugins = [
    # Base models
    'tests.fixtures.models.basic_information',
    'tests.fixtures.models.user',
    'tests.fixtures.models.permission',
    # Stock-related models
    'tests.fixtures.models.stock',
    # Feed-related models
    'tests.fixtures.models.feed',
    'tests.fixtures.models.feed_tag',
    'tests.fixtures.models.announcement_income_sheet_analysis',
    # User-related models
    'tests.fixtures.models.api_token',
    'tests.fixtures.models.follow_stock',
    'tests.fixtures.models.push_notification',
]
