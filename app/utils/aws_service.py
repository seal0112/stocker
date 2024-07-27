import boto3
from flask import current_app


class AWSService:
    def __init__(self):
        self.sqs = boto3.client('sqs')

    def send_message_to_sqs(self, message):
        response = self.sqs.send_message(
            QueueUrl=current_app.config['AWS_SQS_URL'],
            DelaySeconds=3,
            MessageBody=message
        )
        return response
