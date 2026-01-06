import os
from dotenv import load_dotenv

load_dotenv()

bind = f'{os.environ.get("HOST")}:{os.environ.get("PORT")}'
http2 = True
daemon = True
pidfile = '/tmp/gunicorn_stocker.pid'
graceful_timeout = 30

workers = 2
