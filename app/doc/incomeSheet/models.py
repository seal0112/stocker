from ast import Str
from email.policy import default
from pydoc import describe
from unicodedata import name
from flask_restx import Api, Namespace, Resource, fields

namespace = Namespace('income_sheet', 
                'Income Sheet Related Endpoint')

incomeSheetQueryModel = namespace.model('IncomeSheetQuery',{
    'stock_id': fields.String(
        description = 'Company ID'
    ),
    'mode': fields.String(
        description = 'Request latest season/single season/multiple season income sheet',
        enum = ['None', 'single', 'multiple']
    ),
    'year': fields.String(
        description = 'mode==\'single\': Designate specific year. \
            mode==\'multiple\': Decide how many years of data to return.'
    ),
    'season': fields.String(
        description = 'Specify season'
    )
})

incomeSheetModel = namespace.model('IncomeSheet (Update/Response)', {
    'id': fields.Integer(
        description = 'Unique ID'
    ),
    'season': fields.String(
        description = 'Accounting Season',
        enum = ['1', '2', '3', '4']
    ),
    'stock_id': fields.String(
        description = 'Company ID'
    ),
    'update_date':fields.String(
        description = 'Latest update date'
    ),
    'year':fields.Integer(
        description = 'Accounting Year'
    ),
    '基本每股盈餘': fields.String(),
    '所得稅費用': fields.String(),
    '所得稅費用率': fields.String(),
    '推銷費用': fields.String(),
    '推銷費用率': fields.String(),
    '本期淨利': fields.String(),
    '本期淨利率': fields.String(),
    '母公司業主淨利': fields.String(),
    '營業利益': fields.String(),
    '營業利益率': fields.String(),
    '營業外收入及支出合計': fields.String(),
    '營業成本合計': fields.String(),
    '營業收入合計': fields.String(),
    '營業毛利': fields.String(),
    '營業毛利率': fields.String(),
    '營業費用': fields.String(),
    '營業費用率': fields.String(),
    '研究發展費用': fields.String(),
    '研究發展費用率': fields.String(),
    '稀釋每股盈餘': fields.String(),
    '稅前淨利': fields.String(),
    '稅前淨利率': fields.String(),
    '管理費用': fields.String(),
    '管理費用率': fields.String()
})