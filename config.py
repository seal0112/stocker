import os
import json

basedir = os.path.abspath(os.path.dirname(__file__))

with open('{}/critical_file/client_secret.json'.format(
        basedir)) as clientSecretReader:
    client_secret = json.loads(clientSecretReader.read())

with open('{}/critical_file/databaseAccount.json'.format(
        basedir)) as databaseAccountReader:
    database_account = json.loads(databaseAccountReader.read())

# DB_URL = """mysql+pymysql://%s:%s@%s/stocker?charset=utf8""" % (
#     os.getenv('DB_USER'),
#     os.getenv('DB_PASSWORD'),
#     os.getenv('DB_HOST'))

DB_URL = """mysql+pymysql://%s:%s@%s/stocker?charset=utf8""" % (
    database_account['username'],
    database_account['password'],
    database_account['ip'])

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
    JWT_SECRET_KEY = 'tmp-secret'
    CLIENT_SECRET = client_secret

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or DB_URL


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite://'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or DB_URL


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
