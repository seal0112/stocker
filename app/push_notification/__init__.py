from flask import Blueprint

push_notification = Blueprint('push_notification', __name__)

from . import view