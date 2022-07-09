from flask import Blueprint

basic_information = Blueprint('basic_information', __name__)

from . import view
