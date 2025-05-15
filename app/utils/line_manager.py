import requests
import logging


logger = logging.getLogger(__name__)


class LineManager:

    def __init__(self, webhookToken):
        self.notifyUrl = 'https://notify-api.line.me/api/notify'
        self.headers = {
            'Authorization': f'Bearer {webhookToken}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

    def push_notification(self, messages):
        for message in messages:
            try:
                requests.post(
                    self.notifyUrl,
                    headers=self.headers,
                    data={'message': message})
            except Exception as ex:
                logger.exception(f'Failed to push notification: {ex}')
