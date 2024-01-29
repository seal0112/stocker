import os
import json
import requests
import logging


logger = logging.getLogger()


class SlackManager:

    def __init__(self, webhookToken):
        self.notify_url = os.environ.get("slack-hook")
        self.headers = {
            "content-type": "application/json"
        }

    def push_notification(self, username, content):
        requests.post(
        url=self.notify_url,
        data=json.dumps({
            "username": username,
            "text": content
        }),
        headers={"content-type": "application/json"})
