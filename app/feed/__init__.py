from flask import Blueprint

feed = Blueprint('feed', __name__)

from . import feed_view
