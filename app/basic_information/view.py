import json
import logging
from datetime import datetime

from flask import request, jsonify, make_response
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError

from ..database_setup import BasicInformation
from ..utils.stock_search_count_service import StockSearchCountService
from .. import db
from . import basic_information


logger = logging.getLogger(__name__)
stock_search_count_service = StockSearchCountService()


class handleBasicInfo(MethodView):
    """
    Discription:
        this api is used to handle basic information request.
    Detail:
        According to the received stock_id and request method,
        if request method is GET, then return stock_id's basic information.
        if request method is POST, then according to the data entered,
        decide whether to update or add new data into database.
    Args:
        stock_id: a String of stock number.
    Return:
        if request method is GET,
            then return stock_id's basic information.
        if request method is POST,
            According to whether the data is written into the database.
            if true, then return http status 201(Create).
            if not, then return http status 200(Ok).
    Raises:
        Exception: An error occurred.
    """

    def get(self, stock_id):
        """
        GET stock's basic information
        swagger_from_file: BasicInformation_get.yml
        """
        basicInfo = db.session.query(BasicInformation).filter_by(
            id=stock_id).one_or_none()
        if basicInfo is None:
            return jsonify({"error": "Resource not found"}), 404
        else:
            return jsonify(basicInfo.serialize)

    def post(self, stock_id):
        """
        Add or Update stock basic information.
        swagger_from_file: BasicInformation_post.yml
        """
        basicInfo = db.session.query(BasicInformation).filter_by(
            id=stock_id).one_or_none()

        try:
            payload = request.get_json()
            if not payload:
                return make_response(json.dumps("Request body is required"), 400)
        except Exception:
            return make_response(json.dumps("Invalid JSON format"), 400)

        try:
            if basicInfo is not None:
                # typeConversSet is used to converse datatype from user input.
                typeConversSet = set(("實收資本額", "已發行普通股數或TDR原發行股數",
                                      "私募普通股", "特別股"))
                changeFlag = False
                for key in payload:
                    if key in typeConversSet:
                        payload[key] = int(payload[key])
                    if basicInfo[key] != payload[key]:
                        changeFlag = True
                        basicInfo[key] = payload[key]

                # If no data has been modified, then return 200
                if not changeFlag:
                    return jsonify({"message": "OK"}), 200

                # If any data is modified,
                # update update_date to today's date
                basicInfo['update_date'] = datetime.now(
                ).strftime("%Y-%m-%d")
            else:
                basicInfo = BasicInformation()
                basicInfo.id = stock_id
                for key in payload:
                    basicInfo[key] = payload[key]

            db.session.add(basicInfo)
            db.session.commit()
        except IntegrityError as ie:
            db.session.rollback()
            logging.warning(
                "400 %s is failed to update Basic Info. Reason: %s"
                % (stock_id, ie))
            return jsonify({"error": "Failed to update %s Basic Info" % stock_id}), 400
        except Exception as ex:
            logger.warning(
                "400 %s is failed to update basic_information. Reason: %s"
                % (stock_id, ex))
            return jsonify({"error": "Failed to update %s Basic Info" % stock_id}), 400

        stock_search_count_service.create_stock_search_count(stock_id)

        return jsonify({"message": "Created"}), 201

    def patch(self, stock_id):
        """
        Update stock basic information.
        swagger_from_file: BasicInformation_patch.yml
        """
        basicInfo = db.session.query(BasicInformation).filter_by(
            id=stock_id).one_or_none()

        try:
            payload = request.get_json()
            if not payload:
                return make_response(json.dumps("Request body is required"), 400)
        except Exception:
            return make_response(json.dumps("Invalid JSON format"), 400)

        try:
            if basicInfo is not None:
                basicInfo['exchange_type'] = payload['exchangeType']
                db.session.add(basicInfo)
                db.session.commit()
                return jsonify({"message": "OK"}), 200
            else:
                return jsonify({"error": "No such stock id"}), 404
        except Exception as ex:
            db.session.rollback()
            logger.warning(
                "400 %s is failed to update Basic information. Reason: %s"
                % (stock_id, ex))
            return jsonify({"error": "Failed to update %s Basic Information" % stock_id}), 400


basic_information.add_url_rule('/<stock_id>',
                  view_func=handleBasicInfo.as_view(
                      'basic_info_api'),
                  methods=['GET', 'POST', 'PATCH'])
