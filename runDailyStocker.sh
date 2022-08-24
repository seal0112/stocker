#!/bin/bash
cd /home/ec2-user/project/stocker
source venv/bin/activate
python3 crawlerInterface.py
deactivate
exit 0
