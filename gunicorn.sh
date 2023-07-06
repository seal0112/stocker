#!/bin/bash
cd $(dirname "$0")
source venv/bin/activate
gunicorn -c gunicorn.conf.py wsgi:app
exit 0
