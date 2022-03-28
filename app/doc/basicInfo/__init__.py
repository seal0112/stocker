from urllib import response
from flask import request
from flask_restx import Api, Namespace, Resource, fields
from http import HTTPStatus

from app.doc.basicInfo.models import namespace, basicInfoModel
from app.doc.basicInfo.modelExample import basicInfoResponseExample

@namespace.route('/<string:stock_id>')
@namespace.doc(params={'stock_id': 'Company ID (test w/ 2330)'})
class basicInfo(Resource):
    @namespace.response(404, 'Basic information of {stock_id} is not exist.')
    @namespace.marshal_with(basicInfoModel)
    def get(self, stock_id):
        '''Get Basic Information of stock_id'''
        if stock_id != '2330':
            return {},404
        return basicInfoResponseExample, 200
    
    @namespace.response(200, 'Basic information of {stock_id} is up-to-date. Nothing is updated.')
    @namespace.response(201, 'New Basic information of {stock_id} is created.')
    @namespace.response(400, 'Fail to update {stock_id} Basic Information. (Unexpected Error)')
    @namespace.expect(basicInfoModel)
    def post(self, stock_id):
        '''Create A New Basic Information of stock_id'''
        if stock_id != '2330':
            return 'Create', 201
        return 'OK', 200

    @namespace.response(200, 'Basic information of {stock_id} is updated.')
    @namespace.response(400, 'Fail to update {stock_id} Basic Information.')
    @namespace.response(404, 'Basic information of {stock_id} is not exist.')
    @namespace.expect(basicInfoModel)
    def patch(self, stock_id):
        '''Update An Existed Basic Information of stock_id'''
        if stock_id != '2330':
            return 'Stock number not found', 404
        return 'OK', 200