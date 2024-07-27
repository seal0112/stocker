from app import ma
from app.utils.model_utilities import get_current_date
from .models import Feed, AnnouncementIncomeSheetAnalysis


class FeedSchema(ma.Schema):
    class Meta:
        fields = (
            "id", "update_date", "releaseTime",
            "title", "link", "description", "feedType", "source"
        )


class AnnouncementIncomeSheetAnalysisSchema(ma.Schema):
    class Meta:
        model = AnnouncementIncomeSheetAnalysis

    feed_id = ma.Integer(required=True)
    stock_id = ma.String(required=True)
    update_date = ma.Date(default=get_current_date)
    year = ma.Integer(required=True)
    season = ma.String(required=True)
    營業收入合計 = ma.Number()
    營業收入合計年增率 = ma.Decimal()
    營業毛利 = ma.Number()
    營業毛利率 = ma.Decimal()
    營業毛利率年增率 = ma.Decimal()
    營業利益 = ma.Number()
    營業利益率 = ma.Decimal()
    營業利益率年增率 = ma.Decimal()
    稅前淨利 = ma.Number()
    稅前淨利率 = ma.Decimal()
    稅前淨利率年增率 = ma.Decimal()
    本期淨利 = ma.Number()
    本期淨利率 = ma.Decimal()
    本期淨利率年增率 = ma.Decimal()
    母公司業主淨利 = ma.Number()
    基本每股盈餘 = ma.Decimal()
    基本每股盈餘年增率 = ma.Decimal()
