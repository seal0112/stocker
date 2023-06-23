import json
import logging

from flask import make_response, request

from . import auth


logger = logging.getLogger()


@auth.errorhandler(404)
def page_not_found(error):
    logger.info('Page not found: %s, error: %s', request.path, error)
    return make_response(json.dumps('404 not foundss'), 404)


@auth.errorhandler(500)
def internal_server_error(error):
    logger.error('Server Error: %s', error)
    return make_response(json.dumps('500 server error'), 500)
