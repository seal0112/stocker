"""Flask 3.0 compatible request ID middleware.

Replaces flask-log-request-id which is incompatible with Flask 3.0+.
"""
import uuid
from flask import g, request, has_request_context


def current_request_id():
    """Get the current request ID from Flask's g object."""
    if has_request_context():
        return getattr(g, 'request_id', None)
    return None


class RequestID:
    """Middleware to generate and track request IDs.

    Usage:
        app = Flask(__name__)
        RequestID(app)
    """

    def __init__(self, app=None, header_name='X-Request-ID'):
        self.header_name = header_name
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.before_request(self._before_request)
        app.after_request(self._after_request)

    def _before_request(self):
        # Use existing request ID from header or generate new one
        request_id = request.headers.get(self.header_name)
        if not request_id:
            request_id = str(uuid.uuid4())
        g.request_id = request_id

    def _after_request(self, response):
        # Add request ID to response headers
        request_id = getattr(g, 'request_id', None)
        if request_id:
            response.headers[self.header_name] = request_id
        return response
