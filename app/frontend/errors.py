from flask import render_template, request, jsonify
from . import frontend

@frontend.errorhandler(404)
def pageNotfound(error):
    logging.info('Page not found: %s', (request.path))
    return make_response(json.dumps('404 not foundss'), 404)


@frontend.errorhandler(500)
def internalServerError(error):
    logging.error('Server Error: %s', (error))
    return make_response(json.dumps('500 server error'), 500)