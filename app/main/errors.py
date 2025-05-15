import logging
import json

from flask import make_response
from . import main


logger = logging.getLogger(__name__)


# @main.errorhandler(404)
# def pageNotfound(error):
#     return make_response(json.dumps('404 not foundss'), 404)


# @main.errorhandler(500)
# def internalServerError(error):
#     logging.error('Server Error: %s', (error))
#     return make_response(json.dumps('500 server error'), 500)
