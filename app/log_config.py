import os
import logging

from logging.handlers import TimedRotatingFileHandler
from flask_log_request_id import RequestIDLogFilter


def setup_logging(log_dir='log', log_filename='app.log'):
    """
    Set up logging configuration.
    """
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, log_filename)

    handler = TimedRotatingFileHandler(
        log_path,
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8',
        utc=True
    )

    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s [%(request_id)s] [%(name)s] %(message)s'
    )
    handler.setFormatter(formatter)
    handler.addFilter(RequestIDLogFilter())

    logger = logging.getLogger('sqlalchemy.engine')
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
