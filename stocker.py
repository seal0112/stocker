from flask import (
    Flask, request, redirect, url_for,
    jsonify, make_response, render_template
)
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from flask import Blueprint
from flask.views import MethodView
import logging
from logging.handlers import TimedRotatingFileHandler
import json
from datetime import datetime

from stockerModel import (
    showMain, getStockNumber,
    handleBasicInfo, handleMonthRevenue,
    handleIncomeSheet, handleBalanceSheet,
    handleCashFlow
)
import time
from flask_cors import cross_origin

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# Setup the Flask-JWT-Extended extension
app.config['JWT_SECRET_KEY'] = 'tmp-secret'
jwt = JWTManager(app)

# Logger setup
logger = logging.getLogger()
BASIC_FORMAT = '%(asctime)s %(levelname)-8s %(message)s'
DATE_FORMAT = '%m-%d %H:%M'
formatter = logging.Formatter(BASIC_FORMAT, DATE_FORMAT)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)
logger.addHandler(console)


app.add_url_rule('/',
                 'showMain',
                 view_func=showMain)
app.add_url_rule('/api/v0/stock_number',
                 'getStockNumber',
                 view_func=getStockNumber.as_view(
                     'getStockNumber_api'),
                 methods=['GET', 'POST'])
app.add_url_rule('/api/v0/basic_information/<string:stock_id>',
                 'handleBasicInfo',
                 view_func=handleBasicInfo.as_view(
                     'handleBasicInfo_api'),
                 methods=['GET', 'POST'])
app.add_url_rule('/api/v0/income_sheet/<string:stock_id>',
                 'handleIncomeSheet',
                 view_func=handleIncomeSheet.as_view(
                     'handleIncomeSheet'),
                 methods=['GET', 'POST'])
app.add_url_rule('/api/v0/balance_sheet/<string:stock_id>',
                 'handleBalanceSheet',
                 view_func=handleBalanceSheet.as_view(
                     'handleBalanceSheet'),
                 methods=['GET', 'POST'])
app.add_url_rule('/api/v0/cash_flow/<string:stock_id>',
                 'handleCashFlow',
                 view_func=handleCashFlow.as_view(
                     'handleCashFlow'),
                 methods=['GET', 'POST'])
app.add_url_rule('/api/v0/month_revenue/<string:stock_id>',
                 'handleMonthRevenue',
                 view_func=handleMonthRevenue.as_view(
                     'handleMonthRevenue'),
                 methods=['GET', 'POST'])


def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3001'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response

@app.route('/testsetcookie')
def test():
    res = make_response(json.dumps("for set cookie"), 200)
    res.headers["Set-Cookie"] = "coo=haha; Expires=%s" % str(time.time()+5)
    res.set_cookie(key='coo2', value='haha', expires=time.time()+5)

    print(res.headers)
    return res

@app.route('/testsetcookie2')
def test2():
    res = make_response(json.dumps("for set cookie2"), 200)
    res.set_cookie(key='me', value='chipupu', expires=time.time()+5)

    print(res.headers)
    return res

@jwt.user_claims_loader
def add_claims_to_access_token(identity):
    return {
        'hello': identity,
        'foo': [datetime.now()]
    }


@app.route('/login', methods=['POST'])
def login():
    print(request.is_json)
    print(request.data)
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    if username != 'test' or password != 'test':
        return jsonify({"msg": "Bad username or password"}), 401

    # Identity can be any data that is json serializable
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200


@app.route('/protected', methods=['GET'])
@jwt_required
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


@app.errorhandler(404)
def pageNotfound(error):
    logging.info('Page not found: %s', (request.path))
    return make_response(json.dumps('404 not foundss'), 404)


@app.errorhandler(500)
def internalServerError(error):
    logging.error('Server Error: %s', (error))
    return make_response(json.dumps('404 not found'), 404)


if __name__ == '__main__':
    app.debug = True
    app.after_request(after_request)

    fileHandler = TimedRotatingFileHandler(
        'log/app.log', when='D', interval=1,
        backupCount=30, encoding='UTF-8', delay=False, utc=True)
    fileHandler.setFormatter(formatter)
    if app.debug is True:
        fileHandler.setLevel(logging.WARNING)
    else:
        fileHandler.setLevel(logging.WARNING)
    logger.addHandler(fileHandler)

    app.run(host='0.0.0.0', port=5000)
