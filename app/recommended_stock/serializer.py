from marshmallow import fields, EXCLUDE

from .. import ma


class RecommendedStockSchema(ma.Schema):
    """Schema for RecommendedStock model serialization."""

    class Meta:
        unknown = EXCLUDE

    id = fields.Integer(dump_only=True)
    stock_id = fields.String(required=True)
    update_date = fields.Date(required=True)
    filter_model = fields.String(required=True)

    # Optional: include related basic information
    stock_name = fields.Method("get_stock_name")

    def get_stock_name(self, obj):
        """Get stock name from BasicInformation if relationship exists."""
        try:
            from app.database_setup import BasicInformation
            stock = BasicInformation.query.filter_by(id=obj.stock_id).first()
            return stock.公司簡稱 if stock else None
        except Exception:
            return None


class RecommendedStockDetailSchema(ma.Schema):
    """Detailed schema with stock information."""

    class Meta:
        unknown = EXCLUDE

    id = fields.Integer(dump_only=True)
    stock_id = fields.String(required=True)
    update_date = fields.Date(required=True)
    filter_model = fields.String(required=True)

    # Extended information
    stock_info = fields.Method("get_stock_info")

    def get_stock_info(self, obj):
        """Get detailed stock information."""
        try:
            from app.database_setup import BasicInformation, DailyInformation

            stock = BasicInformation.query.filter_by(id=obj.stock_id).first()
            if not stock:
                return None

            info = {
                'stock_id': stock.id,
                'name': stock.公司名稱,
                'short_name': stock.公司簡稱,
                'industry': stock.產業類別,
                'exchange_type': stock.exchange_type
            }

            # Add daily information if available
            if stock.daily_information:
                daily = stock.daily_information
                info['daily'] = {
                    'close_price': float(daily.本日收盤價) if daily.本日收盤價 else None,
                    'change': float(daily.本日漲跌) if daily.本日漲跌 else None,
                    'eps': float(daily.近四季每股盈餘) if daily.近四季每股盈餘 else None,
                    'pe_ratio': float(daily.本益比) if daily.本益比 else None,
                    'dividend_yield': float(daily.殖利率) if daily.殖利率 else None
                }

            return info
        except Exception as e:
            return None
