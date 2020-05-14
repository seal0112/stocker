from flask import Blueprint

frontend = Blueprint('frontend', __name__)

from . import frontendModel, errors