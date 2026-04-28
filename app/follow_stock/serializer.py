from .. import ma
from ..database_setup import BasicInformation, DataUpdateDate
from .models import Follow_Stock


class DataUpdateDateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = DataUpdateDate
        fields = (
            "month_revenue_last_update",
            "announcement_last_update",
            "news_last_update",
            "income_sheet_last_update",
            "earnings_call_last_update"
        )
        load_instance = False


class BasicInformationWithUpdateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = BasicInformation
        fields = ("id", "公司簡稱", "exchange_type", "data_update_date")
        load_instance = False

    data_update_date = ma.Nested(DataUpdateDateSchema)


class FollowStockSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Follow_Stock
        fields = (
            "id", "stock", "last_update_time",
            "comment", "long_or_short"
        )
        load_instance = False

    stock = ma.Nested(BasicInformationWithUpdateSchema)
