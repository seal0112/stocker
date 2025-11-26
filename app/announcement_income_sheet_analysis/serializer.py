from .. import ma


class AnnouncementIncomeSheetAnalysisSchema(ma.Schema):
    class Meta:
        fields = (
            "feed_id", "stock_id", "update_date", "year", "season",
            "processing_failed",
            "營業收入合計", "營業收入合計年增率",
            "營業毛利", "營業毛利率", "營業毛利率年增率",
            "營業利益", "營業利益率", "營業利益率年增率",
            "稅前淨利", "稅前淨利率", "稅前淨利率年增率",
            "本期淨利", "本期淨利率", "本期淨利率年增率",
            "母公司業主淨利",
            "基本每股盈餘", "基本每股盈餘年增率",
            "本業佔比"
        )
