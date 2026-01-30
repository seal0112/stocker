import logging

from flask import jsonify, request

from . import auth


logger = logging.getLogger(__name__)


@auth.errorhandler(404)
def page_not_found(error):
    logger.info('Page not found: %s, error: %s', request.path, error)
    return jsonify({"error": "Not found"}), 404


@auth.errorhandler(500)
def internal_server_error(error):
    logger.error('Server Error: %s', error)
    return jsonify({"error": "Internal server error"}), 500
