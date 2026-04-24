import uuid
from datetime import date


def get_current_date() -> date:
    """Return current date as a date object."""
    return date.today()


def get_UUID() -> str:
    """Return a random UUID hex string."""
    return uuid.uuid4().hex
