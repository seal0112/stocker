import pytest
import os

from flask_migrate import upgrade, stamp
from sqlalchemy import create_engine, text
from app import create_app, db


@pytest.fixture(scope='module')
def dev_app():
    """development environment app fixture"""
    app = create_app('development')

    with app.app_context():
        yield app


@pytest.fixture(scope='session')
def test_app():
    app = create_app('testing')

    test_db_url = app.config['SQLALCHEMY_DATABASE_URI']
    db_name = os.environ.get('DB_NAME', 'stocker') + '_test'

    with app.app_context():
        try:
            engine = create_engine(test_db_url.rsplit('/', 1)[0])
            with engine.connect() as conn:
                conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name}"))

            upgrade()

            db.create_all()

            ctx = app.test_request_context()
            ctx.push()

            yield app

            ctx.pop()

        except Exception as e:
            print(f"Error creating test database: {e}")
        finally:
            with app.app_context():
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
    'tests.fixtures.models.basic_information',
    'tests.fixtures.models.feed',
    'tests.fixtures.models.announcement_income_sheet_analysis',
]
