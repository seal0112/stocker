from marshmallow import fields

from .. import ma


class MonthlyValuationSchema(ma.Schema):
    stock_id = fields.String(required=True)
    year = fields.Integer(required=True)
    month = fields.String(required=True)
    本益比 = fields.Decimal(as_string=True, allow_none=True)
    淨值比 = fields.Decimal(as_string=True, allow_none=True)
    殖利率 = fields.Decimal(as_string=True, allow_none=True)
    均價 = fields.Decimal(as_string=True, allow_none=True)
