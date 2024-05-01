#!/bin/bash
cd $(dirname "$0")
source venv/bin/activate
gunicorn wsgi:app
# nohup celery -A celery_worker.celery worker &
exit 0
