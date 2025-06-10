from .. import ma


class PushNotificationSchema(ma.Schema):
    class Meta:
        fields = (
            "notify_enabled", "gmail", "gmail_token", "notify_time",
            "notify_month_revenue", "notify_income_sheet", "notify_news",
            "notify_announcement", "notify_earnings_call"
        )
