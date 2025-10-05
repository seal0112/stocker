import os
import json
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

from flask import (request, jsonify, make_response)
from flask_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint

from app import create_app, db
from app.utils.slack_manager import SlackManager
import traceback


app = create_app(os.getenv('FLASK_CONFIG') or 'default')

HOST = os.environ.get('HOST', '0.0.0.0')
PORT = os.environ.get('PORT')
app.config['JSON_AS_ASCII'] = False

# Logger setup
logger = logging.getLogger(__name__)
BASIC_FORMAT = '%(asctime)s %(levelname)- 8s in %(module)s: %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M'
formatter = logging.Formatter(BASIC_FORMAT, DATE_FORMAT)


@app.route("/spec")
def spec():
    base_path = os.path.join(app.root_path, 'docs')
    swag = swagger(app, from_file_keyword="swagger_from_file",
                   base_path=base_path)
    swag['info']['version'] = "v0.1"
    swag['info']['title'] = "Stocker API"
    swag['info']['$ref'] = 'resources.yml'
    return jsonify(swag)

# @app.after_request
# def setup_access_conrtol(response):
#     response.headers['Access-Control-Allow-Origin'] = 'https://localhost:3001'
#     response.headers['Access-Control-Allow-Credentials'] = 'true'
#     response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
#     response.headers['Access-Control-Allow-Headers'] =\
#         'Content-Type, Authorization'
#     return response


@app.errorhandler(404)
def pageNotfound(error):
    logging.info('Page not found: %s', (request.path))
    return make_response(json.dumps('404 not found'), 404)


@app.errorhandler(500)
def internalServerError(error):
    error_log = f'Server Error: {error}'
    SlackManager().push_notification('Stocker', error_log)
    logger.error(error_log)
    return make_response(json.dumps('500 server error'), 500)


@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db)


if __name__ == '__main__':
    app.debug = True

    app.run(
        host=HOST,
        port=PORT,
        threaded=True)
