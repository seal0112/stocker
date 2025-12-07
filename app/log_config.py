import os
import logging

import gzip
import shutil

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
    logger.setLevel(logging.WARNING)  # Only log warnings and errors, not SQL queries
    logger.addHandler(handler)

class GZipTimedRotatingFileHandler(TimedRotatingFileHandler):
    def rotate(self, source, dest):
        # 原本的 rotate 行為（移動檔案）
        super().rotate(source, dest)

        if os.path.exists(dest):
            try:
                with open(dest, 'rb') as f_in:
                    with gzip.open(dest + '.gz', 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                os.remove(dest)
            except Exception as e:
                # 可加上 logging 輸出錯誤訊息
                print(f'Log rotation error: {e}')
