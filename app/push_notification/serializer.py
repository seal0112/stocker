from .. import ma


class PushNotificationSchema(ma.Schema):
    class Meta:
        fields = (
            "notify_enabled", "line_notify_token", "notify_time",
            "notify_month_revenue", "notify_income_sheet", "notify_news",
            "notify_announcement"
        )
