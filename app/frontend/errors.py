from app.log_config import get_logger

from flask import request, jsonify

from . import frontend


logger = get_logger(__name__)


@frontend.errorhandler(404)
def pageNotfound(error):
    logger.info('Page not found: %s', (request.path))
    return jsonify({"error": "Not found"}), 404


@frontend.errorhandler(500)
def internalServerError(error):
    logger.error('Server Error: %s', (error))
    return jsonify({"error": "Internal server error"}), 500