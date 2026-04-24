from .. import ma
from ..database_setup import PushNotification


class PushNotificationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PushNotification
        fields = (
            "notify_enabled", "gmail", "gmail_token", "notify_time",
            "notify_month_revenue", "notify_income_sheet", "notify_news",
            "notify_announcement", "notify_earnings_call"
        )
        load_instance = False
