import pytest
import os

from sqlalchemy import create_engine, text
from app import create_app, db


@pytest.fixture(scope='session', autouse=True)
def clean_test_db():
    """Clean the test database at the start of the test session.

    This runs once before all tests, ensuring a completely clean state.
    """
    app = create_app('testing')
    with app.app_context():
        db.drop_all()
        db.create_all()
    yield
    # Optionally clean up after all tests too
    with app.app_context():
        db.drop_all()


@pytest.fixture(scope='module')
def dev_app():
    """development environment app fixture"""
    app = create_app('development')

    with app.app_context():
        yield app


@pytest.fixture(scope='module')
def test_app(clean_test_db):
    """Test app fixture that depends on clean_test_db.

    The clean_test_db fixture ensures the database is clean at session start.
    This fixture just provides the app context for each module.
    """
    app = create_app('testing')

    test_db_url = app.config['SQLALCHEMY_DATABASE_URI']
    db_name = os.environ.get('DB_NAME', 'stocker') + '_test'

    with app.app_context():
        # Create test database if not exists
        engine = create_engine(test_db_url.rsplit('/', 1)[0])
        with engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name}"))

        ctx = app.test_request_context()
        ctx.push()

        yield app

        # Cleanup session but don't drop tables (other modules may need them)
        ctx.pop()
        db.session.remove()


@pytest.fixture
def dev_client(dev_app):
    """test environment app fixture"""
    with dev_app.test_client() as client:
        yield client


@pytest.fixture
def app_context(test_app):
    """Provide a single app context for the entire test function.

    All fixtures and tests should depend on this fixture instead of
    creating their own app context with `with test_app.app_context():`.

    Note: Fixtures should clean up data at the START (before creating)
    to handle leftover data from crashed/interrupted tests.
    """
    with test_app.app_context():
        yield


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
    # 1. User-related models (用戶相關)
    'tests.fixtures.models.user',
    'tests.fixtures.models.permission',
    'tests.fixtures.models.api_token',
    'tests.fixtures.models.push_notification',
    # 2. Auth fixtures (認證相關)
    'tests.fixtures.auth',
    # 3. BasicInformation (股票基本資料)
    'tests.fixtures.models.basic_information',
    # 4. Stock-related models (股票財務資料)
    'tests.fixtures.models.daily_information',
    'tests.fixtures.models.balance_sheet',
    'tests.fixtures.models.income_sheet',
    'tests.fixtures.models.cash_flow',
    'tests.fixtures.models.month_revenue',
    'tests.fixtures.models.monthly_valuation',
    'tests.fixtures.models.stock_commodity',
    'tests.fixtures.models.data_update_date',
    'tests.fixtures.models.stock_search_counts',
    'tests.fixtures.models.earnings_call',
    'tests.fixtures.models.recommended_stock',
    # 5. Feed-related models (新聞/公告相關)
    'tests.fixtures.models.feed',
    'tests.fixtures.models.feed_tag',
    'tests.fixtures.models.announcement_income_sheet_analysis',
    # 6. User-Stock relations (用戶與股票的關聯)
    'tests.fixtures.models.follow_stock',
]
