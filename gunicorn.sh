#!/bin/bash
cd /home/ec2-user/project/stocker
source venv/bin/activate
gunicorn -c gunicorn.conf.py wsgi:app
exit 0
