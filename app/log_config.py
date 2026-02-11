import os
from app.log_config import get_logger
import gzip
import shutil

from logging.handlers import TimedRotatingFileHandler
from app.utils.request_id import current_request_id

import structlog


def add_request_id(logger, method_name, event_dict):
    """Add request_id to log event if available."""
    request_id = current_request_id()
    if request_id:
        event_dict['request_id'] = request_id
    return event_dict


def setup_logging(log_dir='log', log_filename='app.log'):
    """
    Set up structured logging with structlog.

    - JSON format for Loki/ELK
    - Console format for human reading
    - File rotation with gzip compression
    - Automatic request_id injection

    Environment variables:
        LOG_FORMAT: 'json' or 'console' (default: 'console')
                    - json: JSON format, suitable for Loki/ELK
                    - console: Human-readable format
    """
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, log_filename)

    # Determine log format from environment variable
    # Default to 'console' for easier reading without Loki
    log_format = os.environ.get('LOG_FORMAT', 'console').lower()
    use_json = log_format == 'json'

    # Configure standard logging handler for file output
    file_handler = GZipTimedRotatingFileHandler(
        log_path,
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8',
        utc=True
    )
    file_handler.setLevel(logging.INFO)

    # Console handler for development
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # SQLAlchemy only logs warnings and above
    sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
    sqlalchemy_logger.setLevel(logging.WARNING)

    # Shared processors for structlog
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt='iso'),
        add_request_id,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    # Configure structlog
    structlog.configure(
        processors=shared_processors + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    if use_json:
        # JSON output for Loki/ELK
        formatter = structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=shared_processors,
            processors=[
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                structlog.processors.JSONRenderer(),
            ],
        )
    else:
        # Console output for human reading
        formatter = structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=shared_processors,
            processors=[
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                structlog.dev.ConsoleRenderer(colors=True),
            ],
        )

    # Apply formatter to handlers
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)


def get_logger(name=None):
    """
    Get a structlog logger instance.

    Usage:
        from app.log_config import get_logger
        logger = get_logger(__name__)
        logger.info("user_login", user_id=123, action="login")
    """
    return structlog.get_logger(name)


class GZipTimedRotatingFileHandler(TimedRotatingFileHandler):
    """TimedRotatingFileHandler with gzip compression for rotated files."""

    def rotate(self, source, dest):
        super().rotate(source, dest)

        if os.path.exists(dest):
            try:
                with open(dest, 'rb') as f_in:
                    with gzip.open(dest + '.gz', 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                os.remove(dest)
            except Exception as e:
                # Use structlog for error logging
                logger = get_logger(__name__)
                logger.error('log_rotation_error', error=str(e))
