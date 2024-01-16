import json

from flask import request, jsonify
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity

from .models import EarningsCall
from . import earnings_call



class EarningsCallListApi(MethodView):

    @jwt_required()
    def get(self):
        stock = request.args.get('stock', None)
        return jsonify({"earnings_call": "GET"})

    @jwt_required()
    def post(self):
        return jsonify({"earnings_call": "POST"})


earnings_call.add_url_rule('',
    view_func=EarningsCallListApi.as_view('EarningsCallListApi'),
    methods=['GET', 'POST'])