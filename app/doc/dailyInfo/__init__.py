from urllib import response
from flask import request
from flask_restx import Api, Namespace, Resource, fields
from http import HTTPStatus

from app.doc.dailyInfo.models import namespace, dailyInfoModel, dailyPriceModel
from app.doc.dailyInfo.modelExample import dailyInfoResponseExample


@namespace.route('/<string:stock_id>')
@namespace.doc(params={'stock_id': 'Company ID (test w/ 2330)'})
class dailyInfo(Resource):
    @namespace.response(404, 'Daily information of {stock_id} is not exist.')
    @namespace.marshal_with(dailyInfoModel)
    def get(self, stock_id):
        '''Get Daily Information of stock_id'''
        if stock_id != '2330':
            return {}, 404
        return dailyInfoResponseExample, 200
    
    @namespace.response(400, 'Fail to update daily price of {stock_id}. (Unexpected Error)')
    def post(self, stock_id):
        '''Update Daily Price of stock_id'''
        if stock_id != '2330':
            return 'Fail to update daily price of '+str(stock_id), 400
        return "OK", 200