import json
import logging

from flask import make_response, request, jsonify
from . import auth

logger = logging.getLogger()

@auth.errorhandler(404)
def pageNotfound(error):
    logger.info('Page not found: %s', (request.path))
    return make_response(json.dumps('404 not foundss'), 404)


@auth.errorhandler(500)
def internalServerError(error):
    logger.error('Server Error: %s', (error))
    return make_response(json.dumps('500 server error'), 500)