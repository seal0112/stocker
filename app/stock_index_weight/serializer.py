from marshmallow import fields

from .. import ma


class StockIndexWeightSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    stock_id = fields.String(required=True)
    year = fields.Integer(required=True)
    month = fields.Integer(required=True)
    index_type = fields.String(required=True)
    rank = fields.Integer(allow_none=True)
    weight = fields.Decimal(as_string=True, allow_none=True)
    create_time = fields.DateTime(dump_only=True)
