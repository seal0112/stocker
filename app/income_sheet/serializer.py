from marshmallow import fields

from .. import ma
from ..database_setup import IncomeSheet


class IncomeSheetSchema(ma.SQLAlchemyAutoSchema):
    """Schema for IncomeSheet with essential financial fields."""
    # Decimal fields must be explicitly defined to avoid JSON serialization issues
    營業毛利率 = fields.Decimal(as_string=True, allow_none=True)
    營業費用率 = fields.Decimal(as_string=True, allow_none=True)
    營業利益率 = fields.Decimal(as_string=True, allow_none=True)
    稅前淨利率 = fields.Decimal(as_string=True, allow_none=True)
    本期淨利率 = fields.Decimal(as_string=True, allow_none=True)

    class Meta:
        model = IncomeSheet
        fields = (
            "id", "stock_id", "year", "season", "update_date",
            "營業收入合計", "營業成本合計", "營業毛利", "營業毛利率",
            "營業費用", "營業費用率", "營業利益", "營業利益率",
            "稅前淨利", "稅前淨利率", "本期淨利", "本期淨利率",
            "基本每股盈餘", "稀釋每股盈餘"
        )
        load_instance = False
        include_fk = True
