from marshmallow import fields

from .. import ma


class AnnouncementIncomeSheetAnalysisSchema(ma.Schema):
    feed_id = fields.Integer(required=True)
    stock_id = fields.String(required=True)
    update_date = fields.Date()
    year = fields.Integer(allow_none=True)
    season = fields.String(allow_none=True)
    processing_failed = fields.Boolean()

    # BigInteger fields
    營業收入合計 = fields.Integer(allow_none=True)
    營業毛利 = fields.Integer(allow_none=True)
    營業利益 = fields.Integer(allow_none=True)
    稅前淨利 = fields.Integer(allow_none=True)
    本期淨利 = fields.Integer(allow_none=True)
    母公司業主淨利 = fields.Integer(allow_none=True)

    # Decimal fields - use as_string=True for JSON serialization
    營業收入合計年增率 = fields.Decimal(as_string=True, allow_none=True)
    營業毛利率 = fields.Decimal(as_string=True, allow_none=True)
    營業毛利率年增率 = fields.Decimal(as_string=True, allow_none=True)
    營業利益率 = fields.Decimal(as_string=True, allow_none=True)
    營業利益率年增率 = fields.Decimal(as_string=True, allow_none=True)
    稅前淨利率 = fields.Decimal(as_string=True, allow_none=True)
    稅前淨利率年增率 = fields.Decimal(as_string=True, allow_none=True)
    本期淨利率 = fields.Decimal(as_string=True, allow_none=True)
    本期淨利率年增率 = fields.Decimal(as_string=True, allow_none=True)
    基本每股盈餘 = fields.Decimal(as_string=True, allow_none=True)
    基本每股盈餘年增率 = fields.Decimal(as_string=True, allow_none=True)
    本業佔比 = fields.Decimal(as_string=True, allow_none=True)
