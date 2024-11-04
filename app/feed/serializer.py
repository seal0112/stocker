from marshmallow import fields

from app import ma
from app.utils.model_utilities import get_current_date
from app.feed.models import Feed, AnnouncementIncomeSheetAnalysis


class FeedSchema(ma.Schema):
    class Meta:
        fields = (
            "id", "update_date", "releaseTime",
            "title", "link", "description", "feedType", "source"
        )


class AnnouncementIncomeSheetAnalysisSchema(ma.Schema):
    update_date = fields.DateTime(format='%Y-%m-%d')
    class Meta:
        model = AnnouncementIncomeSheetAnalysis
        fields = (
            "feed_id", "stock_id", "update_date", "year", "season",
            "營業收入合計", "營業收入合計年增率",
            "營業毛利", "營業毛利率", "營業毛利率年增率",
            "營業利益", "營業利益率", "營業毛利率年增率",
            "稅前淨利", "稅前淨利率", "稅前淨利率年增率",
            "本期淨利", "本期淨利率", "本期淨利率年增率",
            "母公司業主淨利", "基本每股盈餘", "基本每股盈餘年增率"
        )
