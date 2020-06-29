import os
from flask import (
    Flask, request, redirect, url_for,
    jsonify, make_response, render_template,)
from flask_migrate import Migrate
import logging
from logging.handlers import TimedRotatingFileHandler
import json
from datetime import datetime
from flask_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint
import time

from app import create_app, db

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

migrate = Migrate(app, db)
app.config['JSON_AS_ASCII'] = False
# Logger setup
logger = logging.getLogger()
BASIC_FORMAT = '%(asctime)s %(levelname)- 8s in %(module)s: %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M'
formatter = logging.Formatter(BASIC_FORMAT, DATE_FORMAT)

SWAGGER_URL = '/api/docs'
API_URL = '/spec'

swaggerui_blueprint = get_swaggerui_blueprint(
    # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    SWAGGER_URL,
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': "Stocker Application"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# console = logging.StreamHandler()
# console.setLevel(logging.INFO)
# console.setFormatter(formatter)
# logger.addHandler(console)


@app.route("/spec")
def spec():
    base_path = os.path.join(app.root_path, 'docs')
    swag = swagger(app, from_file_keyword="swagger_from_file",
                   base_path=base_path)
    swag['info']['version'] = "v0.1"
    swag['info']['title'] = "Stocker API"
    swag['info']['$ref'] = 'resources.yml'
    return jsonify(swag)


def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = 'https://localhost:3001'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] =\
        'Content-Type, Authorization'
    return response


app.after_request(after_request)


@app.errorhandler(404)
def pageNotfound(error):
    logging.info('Page not found: %s', (request.path))
    return make_response(json.dumps('404 not foundss'), 404)


@app.errorhandler(500)
def internalServerError(error):
    logging.error('Server Error: %s', (error))
    return make_response(json.dumps('500 server error'), 500)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db)


if __name__ == '__main__':
    app.debug = True

    basedir = os.path.abspath(os.path.dirname(__file__))
    logdir = os.path.join(basedir, 'log')
    if os.path.exists(logdir) is False:
        os.mkdir(logdir)
    log_filename = datetime.now().strftime("log/app %Y-%m-%d.log")
    fileHandler = TimedRotatingFileHandler(
        log_filename, when='D', interval=1,
        backupCount=30, encoding='UTF-8', delay=False, utc=False)
    fileHandler.setFormatter(formatter)

    fileHandler.setLevel(logging.WARNING)

    logger.addHandler(fileHandler)
    app.run(host='0.0.0.0', port=5000, threaded=True)
