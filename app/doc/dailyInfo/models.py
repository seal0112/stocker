from email.policy import default
from flask_restx import Api, Namespace, Resource, fields

namespace = Namespace('daily_information', 
                'Daily Information Related Endpoint')

dailyInfoModel = namespace.model('DailyInfo', {
    'stock_id': fields.String(
        description = 'Company ID of basic information'
    ),
    'update_date': fields.String(
        description = 'Latest update date'
    ),
    '本日收盤價': fields.Float(
        default = 0.0
    ),
    '本日漲跌': fields.Float(
        default = 0.0
    ),
    '近四季每股盈餘': fields.Float(
        default = 0.0
    ),
    '本益比': fields.Float(
        default = 0.0
    )
})

dailyPriceModel = namespace.model('DailyPrice', {
    '本日收盤價': fields.Float(
        default = 0.0
    ),
    '本日漲跌': fields.Float(
        default = 0.0
    )
})