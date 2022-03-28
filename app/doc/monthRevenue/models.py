from ast import Str
from email.policy import default
from pydoc import describe
from unicodedata import name
from flask_restx import Api, Namespace, Resource, fields

namespace = Namespace('month_revenue', 'Month Revene Related Endpoint')

monthRevenueModel = namespace.model('monthRevenueModel',{
    'id': fields.Integer(
        description = 'Unique ID'
    ),
    'update_date':fields.String(
        description = 'Latest update date'
    ),
    'year':fields.Integer(
        description = 'Accounting Year'
    ),
    'month': fields.String(
        description = 'Accounting Season',
        enum = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
    ),
    '當月營收': fields.Integer(),
    '上月營收': fields.Integer(),
    '去年當月營收': fields.Integer(),
    '上月比較增減': fields.Integer(),
    '去年同月增減': fields.Integer(),
    '當月累計營收': fields.Integer(),
    '去年累計營收': fields.Integer(),
    '前期比較增減': fields.Integer(),
    '備註': fields.String()
})

monthRevenueModelList = namespace.model('monthRevenueModeList', {
    'entities': fields.Nested(
        monthRevenueModel,
        description='List of monthRevenueModel',
        as_list=True
    )
})