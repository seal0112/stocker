import logging
import json

from flask import request, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask.views import MethodView

from . import push_notification
from .. import db
from ..database_setup import PushNotification
from .serializer import PushNotificationSchema


class PushNotificationApi(MethodView):
    decorators = [jwt_required()]

    def get(self):
        current_user = get_jwt_identity()
        push_notification = PushNotification.query.filter_by(
            user_id=current_user['id']).one_or_none()
        return PushNotificationSchema().dumps(push_notification)

    def put(self):
        current_user = get_jwt_identity()
        push_notification = PushNotification.query.filter_by(
            user_id=current_user['id']).one_or_none()

        payload = json.loads(request.data)
        if push_notification is None:
            push_notification = PushNotification()
            push_notification.user_id = current_user['id']

        push_notification.notify_enabled = payload.get('notify_enabled', False)
        push_notification.gmail = payload.get('gmail', None)
        push_notification.gmail_token = payload.get('gmail_token', None)
        push_notification.notify_time = payload.get('notify_time', False)
        push_notification.notify_month_revenue = payload.get('notify_month_revenue', False)
        push_notification.notify_income_sheet = payload.get('notify_income_sheet', False)
        push_notification.notify_news = payload.get('notify_news', False)
        push_notification.notify_announcement = payload.get('notify_announcement', False)
        push_notification.notify_earnings_call = payload.get('notify_earnings_call', False)

        try:
            db.session.add(push_notification)
            db.session.commit()
        except Exception as ex:
            logging.error(
                f'Failed to update user {current_user["id"]} push notification: {ex}')
            db.session.rollback()
            return make_response({
                "status": "資料錯誤"
            }, 400)
        else:
            return PushNotificationSchema().dumps(push_notification)


push_notification.add_url_rule('/',
                  view_func=PushNotificationApi.as_view(
                      'push_notification_api'),
                  methods=['GET', 'PUT'])
