import os
import json
import datetime
from dotenv import load_dotenv


load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))

with open('{}/critical_file/client_secret.json'.format(
        basedir)) as clientSecretReader:
    client_secret = json.loads(clientSecretReader.read())

DB_URL = (
    'mysql+pymysql://'
    + f'{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}'
    + f'@{os.getenv("DB_HOST")}/{os.getenv("DB_NAME")}?charset=UTF8MB4'
)

REDIS_URL = (
    'redis://'
    + f':{os.getenv("REDIS_PASSWORD")}'
    + f'@{os.getenv("REDIS_HOST")}'
    + f':{os.getenv("REDIS_PORT")}'
    + f'/{os.getenv("REDIS_DB_NUMBER")}'
)


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess db.String'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    SSL_REDIRECT = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    FLASKY_SLOW_DB_QUERY_TIME = 0.5
    SQLALCHEMY_ENGINE_OPTION = {
        'pool_pre_ping': True,
        'pool_recycle': 1800
    }

    # JWT config
    JWT_SECRET_KEY = os.environ.get('SECRET_KEY') or 'tmp-secret'
    #JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=180)
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(days=30)
    JWT_TOKEN_LOCATION = ['cookies', 'headers']
    JWT_REFRESH_COOKIE_PATH = '/api/auth/refresh'
    JWT_COOKIE_SECURE = True
    JWT_CSRF_IN_COOKIES = False

    # celery config
    broker_url = os.environ.get('CELERY_BROKER_URL') or REDIS_URL
    result_backend = os.environ.get('CELERY_RESULT_BACKEND') or REDIS_URL
    broker_connection_retry_on_startup = True
    result_expires = 1800
    worker_concurrency = os.environ.get('CELERY_WORKER_CONCURRENCY') or 2

    CLIENT_SECRET = client_secret

    AWS_SQS_URL = os.environ.get('AWS_SQS_URL')
    AWS_REGION = os.environ.get('AWS_REGION')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or DB_URL
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or DB_URL
    SQLALCHEMY_ECHO = True
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or DB_URL
    SQLALCHEMY_ECHO = True


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
