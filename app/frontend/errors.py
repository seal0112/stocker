from flask import render_template, request, jsonify, make_response
import json
import logging
from . import frontend

logger = logging.getLogger()

@frontend.errorhandler(404)
def pageNotfound(error):
    logger.info('Page not found: %s', (request.path))
    return make_response(json.dumps('404 not foundss'), 404)


@frontend.errorhandler(500)
def internalServerError(error):
    logger.error('Server Error: %s', (error))
    return make_response(json.dumps('500 server error'), 500)