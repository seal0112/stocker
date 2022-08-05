from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from config import config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'https://localhost:3001/login'
jwt = JWTManager()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    login_manager.init_app(app)
    jwt.init_app(app)

    from .basic_information import basic_information
    from .income_sheet import income_sheet
    from .balance_sheet import balance_sheet
    from .cash_flow import cash_flow
    from .month_revenue import month_revenue
    from .feed import feed

    app.register_blueprint(basic_information, url_prefix='/api/v0/basic_information')
    app.register_blueprint(income_sheet, url_prefix='/api/v0/income_sheet')
    app.register_blueprint(balance_sheet, url_prefix='/api/v0/balance_sheet')
    app.register_blueprint(cash_flow, url_prefix='/api/v0/cash_flow')
    app.register_blueprint(month_revenue, url_prefix='/api/v0/month_revenue')
    app.register_blueprint(feed, url_prefix='/api/v0/feed')

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix='/api/v0')

    from .frontend import frontend as frontend_blueprint
    app.register_blueprint(frontend_blueprint, url_prefix='/api/v0/f')

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/api/auth')

    from .doc import blueprint as doc_blueprint
    app.register_blueprint(doc_blueprint, url_prefix='/doc')


    return app
