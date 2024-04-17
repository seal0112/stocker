import uuid
from datetime import datetime


def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")


def get_UUID():
    return uuid.uuid4().hex
