#!/bin/bash
cd $(dirname "$0")
source venv/bin/activate
gunicorn wsgi:app
exit 0
