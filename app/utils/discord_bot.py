import os
import requests
import json

class DiscordBot:
    def __init__(self):
        self.webhooks = {
            "income-sheet": os.environ.get("DISCORD_WEBHOOK_INCOME_SHEET"),
            "revenue": os.environ.get("DISCORD_WEBHOOK_REVENUE"),
        }

    def __get_headers(self) -> dict:
        return {
            "content-type": "application/json"
        }

    def push_message(self, channel: str, message: str):
        if '營收' in channel:
            token = 'revenue'
        else:
            token = 'income-sheet'

        requests.post(
            url=self.webhooks[token],
            data=json.dumps({
                "username": channel,
                "content": message
            }),
            headers=self.__get_headers()
        )
