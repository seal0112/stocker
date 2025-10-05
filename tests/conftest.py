import pytest
import os

from flask_migrate import upgrade, stamp
from sqlalchemy import create_engine, text
from app import create_app, db


@pytest.fixture(scope='session')
def app():
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


@pytest.fixture()
def client(app):
    with app.test_client() as client:
        yield client


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
