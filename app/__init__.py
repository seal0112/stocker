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

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix='/api/v0')

    from .frontend import frontend as frontend_blueprint
    app.register_blueprint(frontend_blueprint, url_prefix='/api/v0/f')

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/api/auth')

    from .doc import blueprint as doc_blueprint
    app.register_blueprint(doc_blueprint, url_prefix='/doc')


    return app
