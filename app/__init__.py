import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from redis import Redis

from config import config
from app.tasks import celery_init_app


db = SQLAlchemy()
jwt = JWTManager()
ma = Marshmallow()
migrate = Migrate()
celery = celery_init_app(__name__, os.getenv('FLASK_CONFIG'))


redis_client = Redis(
    host=os.environ.get('REDIS_HOST') or 'localhost',
    password=os.environ.get('REDIS_PASSWORD') or '',
    port=os.environ.get('REDIS_PORT') or 6379,
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
    celery.conf.update(app.config)

    from app.basic_information import basic_information
    from app.income_sheet import income_sheet
    from app.balance_sheet import balance_sheet
    from app.cash_flow import cash_flow
    from app.month_revenue import month_revenue
    from app.feed import feed
    from app.follow_stock import follow_stock
    from app.push_notification import push_notification
    from app.earnings_call import earnings_call
    from app.monthly_valuation import monthly_valuation

    app.register_blueprint(basic_information, url_prefix='/api/v0/basic_information')
    app.register_blueprint(income_sheet, url_prefix='/api/v0/income_sheet')
    app.register_blueprint(balance_sheet, url_prefix='/api/v0/balance_sheet')
    app.register_blueprint(cash_flow, url_prefix='/api/v0/cash_flow')
    app.register_blueprint(month_revenue, url_prefix='/api/v0/month_revenue')
    app.register_blueprint(feed, url_prefix='/api/v0/feed')
    app.register_blueprint(follow_stock, url_prefix='/api/v0/follow_stock')
    app.register_blueprint(push_notification, url_prefix='/api/v0/push_notification')
    app.register_blueprint(earnings_call, url_prefix='/api/v0/earnings_call')
    app.register_blueprint(monthly_valuation, url_prefix='/api/v0/monthly_valuation')

    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix='/api/v0')

    from app.frontend import frontend as frontend_blueprint
    app.register_blueprint(frontend_blueprint, url_prefix='/api/v0/f')

    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/api/auth')

    return app
