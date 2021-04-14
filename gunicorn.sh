#!/bin/bash
cd /home/ec2-user/project/stocker
source venv/bin/activate
nohup gunicorn --bind=0.0.0.0:5000 --workers=2 wsgi:app > log/stocker.out 2> stocker.err &
exit 0
