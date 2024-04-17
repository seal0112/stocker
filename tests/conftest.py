import pytest
from app import create_app, db


@pytest.fixture(scope='session')
def app():
    app = create_app('testing')

    with app.app_context():
        db.create_all()

    ctx = app.test_request_context()
    ctx.push()

    yield app

    ctx.pop()

    with app.app_context():
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
