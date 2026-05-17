from flask import Blueprint

ai_prompt = Blueprint('ai_prompt', __name__)

from . import views
