import time
from flask import request, g
from app.log_config import get_logger

logger = get_logger(__name__)

_SENSITIVE_FIELDS = {'password', 'token', 'api_key', 'secret', 'access_token', 'refresh_token'}
_MAX_BODY_LEN = 1000


def _safe_get_user():
    try:
        from flask_jwt_extended import get_jwt_identity, get_jwt
        identity = get_jwt_identity()
        if identity:
            claims = get_jwt()
            return claims.get('username') or str(identity)
    except Exception:
        pass
    return None


def _mask(data: dict) -> dict:
    return {k: '***' if k.lower() in _SENSITIVE_FIELDS else v for k, v in data.items()}


def _truncate(s: str) -> str:
    if len(s) > _MAX_BODY_LEN:
        return s[:_MAX_BODY_LEN] + f'...(+{len(s) - _MAX_BODY_LEN})'
    return s


def register_request_logging(app):

    @app.before_request
    def _before():
        g.req_start = time.monotonic()

        kwargs = {'method': request.method, 'path': request.path}

        if request.method == 'GET' and request.query_string:
            kwargs['query'] = request.query_string.decode('utf-8', errors='replace')

        if request.method in ('POST', 'PUT', 'PATCH'):
            body = request.get_json(silent=True, force=True)
            if isinstance(body, dict):
                kwargs['body'] = _mask(body)

        logger.info('request_in', **kwargs)

    @app.after_request
    def _after(response):
        elapsed = time.monotonic() - g.get('req_start', time.monotonic())
        kwargs = {
            'method': request.method,
            'path': request.path,
            'status': response.status_code,
            'duration_ms': round(elapsed * 1000),
        }

        user = _safe_get_user()
        if user:
            kwargs['user'] = user

        if 'application/json' in (response.content_type or ''):
            kwargs['response'] = _truncate(response.get_data(as_text=True))

        level = 'error' if response.status_code >= 500 else 'warning' if response.status_code >= 400 else 'info'
        getattr(logger, level)('request_out', **kwargs)

        return response
