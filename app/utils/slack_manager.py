import os
import json
import requests
from app.log_config import get_logger


logger = get_logger(__name__)


class SlackManager:

    def __init__(self, webhookToken=None):
        self.notify_url = webhookToken or os.environ.get("SLACK_HOOK")
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
