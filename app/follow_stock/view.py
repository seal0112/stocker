import json

from flask import request, jsonify, make_response
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity

from .follow_stock_services import FollowStockService
from .models import Follow_Stock
from .. import db
from . import follow_stock

follow_stock_service = FollowStockService()


class FollowStockListApi(MethodView):

    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        show_delete = request.args.get('show_delete', False)
        follow_stocks = follow_stock_service.get_all_follow_stock(
            current_user['id'], show_delete)
        return jsonify([follow_data.serialize for follow_data in follow_stocks])

    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        payload = json.loads(request.data)
        follow_data = follow_stock_service.create_follow_stock(
            current_user['id'],
            payload['stock_id'],
            payload['long_or_short'],
            payload['comment']
        )
        return jsonify(follow_data.serialize)


class FollowStockDetailApi(MethodView):

    @jwt_required()
    def get(self, follow_stock_id):
        current_user = get_jwt_identity()
        follow_data = follow_stock_service.get_follow_stock(
            current_user['id'], follow_stock_id)

        if not follow_data:
            return jsonify(None), 200

        return jsonify(follow_data.serialize)

    @jwt_required()
    def patch(self, follow_stock_id):
        current_user = get_jwt_identity()
        payload = json.loads(request.data)
        try:
            follow_data = follow_stock_service.update_follow_stock(
                current_user['id'],
                follow_stock_id,
                payload['long_or_short'],
                payload['comment']
            )
            data = follow_data.serialize
            return jsonify(data)
        except Exception as ex:
            return jsonify({}), 404

    @jwt_required()
    def delete(self, follow_stock_id):
        current_user = get_jwt_identity()
        follow_data = follow_stock_service.delete_follow_stock(
            current_user['id'],
            follow_stock_id
        )
        return '', 204


follow_stock.add_url_rule('/',
                  view_func=FollowStockListApi.as_view(
                      'follow_stock_list_api'),
                  methods=['GET', 'POST'])

follow_stock.add_url_rule('/<follow_stock_id>',
                  view_func=FollowStockDetailApi.as_view(
                      'follow_stock_detail_api'),
                  methods=['GET', 'PATCH', 'DELETE'])
