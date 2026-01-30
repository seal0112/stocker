import logging

from flask import request, jsonify
from flask_jwt_extended import jwt_required
from flask.views import MethodView

from app.utils.jwt_utils import get_current_user
from . import push_notification
from .. import db
from ..database_setup import PushNotification
from .serializer import PushNotificationSchema


class PushNotificationApi(MethodView):
    decorators = [jwt_required()]

    def get(self):
        current_user = get_current_user()
        user_notification = PushNotification.query.filter_by(
            user_id=current_user['id']).one_or_none()
        return jsonify(PushNotificationSchema().dump(user_notification))

    def put(self):
        current_user = get_current_user()
        user_notification = PushNotification.query.filter_by(
            user_id=current_user['id']).one_or_none()

        try:
            payload = request.get_json()
            if not payload:
                return jsonify({"error": "Request body is required"}), 400
        except Exception:
            return jsonify({"error": "Invalid JSON format"}), 400

        if user_notification is None:
            user_notification = PushNotification()
            user_notification.user_id = current_user['id']

        user_notification.notify_enabled = payload.get('notify_enabled', False)
        user_notification.gmail = payload.get('gmail', None)
        user_notification.gmail_token = payload.get('gmail_token', None)
        user_notification.notify_time = payload.get('notify_time', False)
        user_notification.notify_month_revenue = payload.get('notify_month_revenue', False)
        user_notification.notify_income_sheet = payload.get('notify_income_sheet', False)
        user_notification.notify_news = payload.get('notify_news', False)
        user_notification.notify_announcement = payload.get('notify_announcement', False)
        user_notification.notify_earnings_call = payload.get('notify_earnings_call', False)

        try:
            db.session.add(user_notification)
            db.session.commit()
        except Exception as ex:
            logging.error(
                f'Failed to update user {current_user["id"]} push notification: {ex}')
            db.session.rollback()
            return jsonify({"error": "Failed to update push notification"}), 400
        else:
            return jsonify(PushNotificationSchema().dump(user_notification))


push_notification.add_url_rule('/',
                  view_func=PushNotificationApi.as_view(
                      'push_notification_api'),
                  methods=['GET', 'PUT'])
