from urllib import response
from flask import request
from flask_restx import Api, Namespace, Resource, fields
from http import HTTPStatus

from app.doc.incomeSheet.models import namespace, incomeSheetModel, incomeSheetQueryModel
from app.doc.incomeSheet.modelExample import incomeSheetResponseExample

@namespace.route('/<string:stock_id>')
@namespace.doc(params={'stock_id': 'Company ID (test w/ 2330)'})
class incomeSheet(Resource):
    @namespace.response(404, 'Income sheet of {stock_id} is not exist.')
    @namespace.marshal_with(incomeSheetModel)
    @namespace.expect(incomeSheetQueryModel)
    def get(self, stock_id):
        '''Get Income Sheet of stock_id (Latest / Designated Season / Multiple Years)'''
        if stock_id != '2330':
            return {}, 404
        return incomeSheetResponseExample, 200
    
    @namespace.response(200, 'Income Sheet of {stock_id} is up-to-date. Nothing is updated.')
    @namespace.response(201, 'New Income Sheet of {stock_id} is created.')
    @namespace.response(400, 'Fail to update {stock_id} Income sheet. (Unexpected Error)')
    @namespace.expect(incomeSheetModel)
    def post(self, stock_id):
        '''Add or Update Income Sheet of stock_id'''
        if stock_id != '2330':
            return 'Create/Update', 201
        return 'OK', 200

