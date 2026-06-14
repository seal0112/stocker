from app.log_config import get_logger
from datetime import date, datetime, timedelta

from flask import request, jsonify
from flask_jwt_extended import jwt_required
from flask.views import MethodView
from sqlalchemy import or_

from app.utils.jwt_utils import get_current_user
from app.decorators.auth import api_auth_required
from . import push_notification
from .. import db
from ..database_setup import PushNotification, DataUpdateDate
from ..follow_stock.models import Follow_Stock
from .serializer import PushNotificationSchema

logger = get_logger(__name__)


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
        user_notification.notify_earnings_call_summary = payload.get('notify_earnings_call_summary', False)

        try:
            db.session.add(user_notification)
            db.session.commit()
        except Exception as ex:
            logger.error(
                f'Failed to update user {current_user["id"]} push notification: {ex}')
            db.session.rollback()
            return jsonify({"error": "Failed to update push notification"}), 400
        else:
            return jsonify(PushNotificationSchema().dump(user_notification))


class EarningsCallSummarySubscribersApi(MethodView):
    """Return users subscribed to earnings call summary notifications (for Lambda use)."""
    decorators = [api_auth_required]

    def get(self):
        subscribers = PushNotification.query.filter_by(
            notify_enabled=True,
            notify_earnings_call_summary=True
        ).filter(
            PushNotification.gmail.isnot(None),
            PushNotification.gmail != '',
            PushNotification.gmail_token.isnot(None),
            PushNotification.gmail_token != '',
        ).all()
        return jsonify([
            {'gmail': s.gmail, 'gmail_token': s.gmail_token}
            for s in subscribers
        ])


push_notification.add_url_rule('/',
                  view_func=PushNotificationApi.as_view(
                      'push_notification_api'),
                  methods=['GET', 'PUT'])

class PushNotificationDueApi(MethodView):
    """Return users whose notify_time falls in the current 15-min window, with their stock updates."""
    decorators = [api_auth_required]

    def get(self):
        now = datetime.utcnow() + timedelta(hours=8)  # Taiwan time (UTC+8)
        window_start = (now - timedelta(minutes=15)).strftime('%H:%M')
        window_end = (now + timedelta(minutes=14)).strftime('%H:%M')
        today = date.today()

        due = PushNotification.query.filter(
            PushNotification.notify_enabled == True,
            PushNotification.notify_time.between(window_start, window_end),
            PushNotification.gmail.isnot(None),
            PushNotification.gmail != '',
            PushNotification.gmail_token.isnot(None),
            PushNotification.gmail_token != '',
        ).all()

        result = []
        for pn in due:
            followed = Follow_Stock.query.filter_by(
                user_id=pn.user_id, is_delete=False
            ).all()
            stock_ids = [f.stock_id for f in followed]
            if not stock_ids:
                continue

            update_filters = []
            if pn.notify_month_revenue:
                update_filters.append(DataUpdateDate.month_revenue_last_update == today)
            if pn.notify_announcement:
                update_filters.append(DataUpdateDate.announcement_last_update == today)
            if pn.notify_income_sheet:
                update_filters.append(DataUpdateDate.income_sheet_last_update == today)
            if pn.notify_news:
                update_filters.append(DataUpdateDate.news_last_update == today)
            if pn.notify_earnings_call:
                update_filters.append(DataUpdateDate.earnings_call_last_update == today)

            if not update_filters:
                continue

            rows = DataUpdateDate.query.filter(
                DataUpdateDate.stock_id.in_(stock_ids),
                or_(*update_filters),
            ).all()

            if not rows:
                continue

            stocks = []
            for row in rows:
                stocks.append({
                    'stock_id': row.stock_id,
                    'month_revenue': pn.notify_month_revenue and row.month_revenue_last_update == today,
                    'announcement': pn.notify_announcement and row.announcement_last_update == today,
                    'income_sheet': pn.notify_income_sheet and row.income_sheet_last_update == today,
                    'news': pn.notify_news and row.news_last_update == today,
                    'earnings_call': pn.notify_earnings_call and row.earnings_call_last_update == today,
                })

            result.append({
                'gmail': pn.gmail,
                'gmail_token': pn.gmail_token,
                'stocks': stocks,
            })

        return jsonify(result)


push_notification.add_url_rule('/due',
                  view_func=PushNotificationDueApi.as_view(
                      'push_notification_due_api'),
                  methods=['GET'])

push_notification.add_url_rule('/earnings_call_summary_subscribers',
                  view_func=EarningsCallSummarySubscribersApi.as_view(
                      'earnings_call_summary_subscribers_api'),
                  methods=['GET'])
