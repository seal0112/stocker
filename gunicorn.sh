#!/bin/bash
cd /home/ec2-user/project/stocker
source venv/bin/activate
gunicorn --bind=0.0.0.0:5000 --daemon --workers=2 wsgi:app
exit 0
