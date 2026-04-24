from .. import ma
from ..database_setup import BasicInformation


class BasicInformationSchema(ma.SQLAlchemyAutoSchema):
    """Simple schema for nested references (e.g., in FollowStockSchema)."""
    class Meta:
        model = BasicInformation
        fields = (
            "id", "公司簡稱", "exchange_type"
        )
        load_instance = False


class BasicInformationDetailSchema(ma.SQLAlchemyAutoSchema):
    """Detailed schema for single stock basic information API."""
    class Meta:
        model = BasicInformation
        fields = (
            "id", "update_date", "exchange_type",
            "公司名稱", "公司簡稱", "產業類別",
            "住址", "董事長", "總經理",
            "發言人", "總機電話",
            "成立日期", "上市上櫃興櫃公開發行日期",
            "實收資本額", "已發行普通股數或TDR原發行股數",
            "編製財務報告類型", "簽證會計師事務所",
            "簽證會計師一", "簽證會計師二",
            "公司網址", "電子郵件信箱"
        )
        load_instance = False