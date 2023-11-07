import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
import redis

from config import config

db = SQLAlchemy()
jwt = JWTManager()
ma = Marshmallow()
migrate = Migrate()

redis_client = redis.Redis(
    host=os.environ.get('REDIS_HOST') or 'localhost',
    password=os.environ.get('REDIS_PASSWORD') or '',
    port=6379,
    db=os.environ.get('REDIS_DB_NUMBER') or '0'
)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    ma.init_app(app)

    from .basic_information import basic_information
    from .income_sheet import income_sheet
    from .balance_sheet import balance_sheet
    from .cash_flow import cash_flow
    from .month_revenue import month_revenue
    from .feed import feed
    from .follow_stock import follow_stock
    from .push_notification import push_notification

    app.register_blueprint(basic_information, url_prefix='/api/v0/basic_information')
    app.register_blueprint(income_sheet, url_prefix='/api/v0/income_sheet')
    app.register_blueprint(balance_sheet, url_prefix='/api/v0/balance_sheet')
    app.register_blueprint(cash_flow, url_prefix='/api/v0/cash_flow')
    app.register_blueprint(month_revenue, url_prefix='/api/v0/month_revenue')
    app.register_blueprint(feed, url_prefix='/api/v0/feed')
    app.register_blueprint(follow_stock, url_prefix='/api/v0/follow_stock')
    app.register_blueprint(push_notification, url_prefix='/api/v0/push_notification')

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix='/api/v0')

    from .frontend import frontend as frontend_blueprint
    app.register_blueprint(frontend_blueprint, url_prefix='/api/v0/f')

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/api/auth')

    return app
