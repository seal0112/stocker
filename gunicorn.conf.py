import os
import logging
from dotenv import load_dotenv

load_dotenv()

bind = f'{os.environ.get("HOST")}:{os.environ.get("PORT")}'
http2 = True
daemon = True
pidfile = '/tmp/gunicorn_stocker.pid'
graceful_timeout = 30

workers = 2

# Logging — route gunicorn access/error through rotating+gzip handlers
# so they follow the same 30-day retention policy as app.log.
accesslog = '-'   # send to stdout, intercepted by the custom logger below
errorlog = '-'    # send to stderr, intercepted by the custom logger below
loglevel = 'info'
capture_output = True


def on_starting(server):
    import gzip
    import shutil
    from logging.handlers import TimedRotatingFileHandler

    os.makedirs('log', exist_ok=True)

    class GZipRotatingHandler(TimedRotatingFileHandler):
        def rotate(self, source, dest):
            super().rotate(source, dest)
            if os.path.exists(dest):
                with open(dest, 'rb') as f_in, gzip.open(dest + '.gz', 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
                os.remove(dest)

        def getFilesToDelete(self):
            dir_name, base_name = os.path.split(self.baseFilename)
            prefix = base_name + '.'
            result = []
            for fn in os.listdir(dir_name):
                name = fn[:-3] if fn.endswith('.gz') else fn
                if name.startswith(prefix):
                    suffix = name[len(prefix):]
                    if self.extMatch.match(suffix):
                        result.append(os.path.join(dir_name, fn))
            result.sort()
            if len(result) < self.backupCount:
                return []
            return result[:len(result) - self.backupCount]

    def _add_rotating_handler(logger_name, filepath):
        h = GZipRotatingHandler(
            filepath, when='midnight', interval=1, backupCount=30,
            encoding='utf-8', utc=True
        )
        h.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
        logging.getLogger(logger_name).addHandler(h)

    _add_rotating_handler('gunicorn.access', 'log/gunicorn_access.log')
    _add_rotating_handler('gunicorn.error',  'log/gunicorn_error.log')
