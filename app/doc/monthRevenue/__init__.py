from urllib import response
from flask import request
from flask_restx import Api, Namespace, Resource, fields
from http import HTTPStatus

from app.doc.monthRevenue.models import namespace, monthRevenueModel, monthRevenueModelList
from app.doc.monthRevenue.modelExample import monthRevenueResponseExample

@namespace.route('/<string:stock_id>')
@namespace.doc(params={'stock_id': 'Company ID (test w/ 2330)'})
class incomeSheet(Resource):
    @namespace.response(404, 'Month Revenue of {stock_id} is not exist.')
    @namespace.marshal_list_with(monthRevenueModelList)
    def get(self, stock_id):
        '''Get Latest 5 Years Month Revenue of stock_id'''
        if stock_id != '2330':
            return {}, 404
        return monthRevenueResponseExample, 200

    @namespace.response(200, 'Month Revenue of {stock_id} is up-to-date. Nothing is updated.')
    @namespace.response(201, 'New Month Revenue of {stock_id} is created.')
    @namespace.response(400, 'Fail to update {stock_id} Month Revenue. (Unexpected Error)')
    @namespace.expect(monthRevenueModel)
    def post(self, stock_id):
        '''Add or Update Month Revenue of stock_id'''
        if stock_id != '2330':
            return 'Create/Update', 201
        return 'OK', 200