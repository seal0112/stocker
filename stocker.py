import os
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
from flasgger import Swagger
import logging
from logging.handlers import TimedRotatingFileHandler
import json
from datetime import datetime

import time
from flask_login import (
    LoginManager, UserMixin, login_user,
    current_user, login_required, logout_user
)

from app import create_app, db

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

swagger = Swagger(app)

app.config['JSON_AS_ASCII'] = False
app.secret_key = 'my-secret-key'

# Setup the Flask-JWT-Extended extension
app.config['JWT_SECRET_KEY'] = 'tmp-secret'
jwt = JWTManager(app)

login_manager = LoginManager(app)
login_manager.init_app(app)
#  假裝是我們的使用者
users = {'test': {'password': 'test'}}

# Logger setup
logger = logging.getLogger()
BASIC_FORMAT = '%(asctime)s %(levelname)- 8s in %(module)s: %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M'
formatter = logging.Formatter(BASIC_FORMAT, DATE_FORMAT)

# console = logging.StreamHandler()
# console.setLevel(logging.INFO)
# console.setFormatter(formatter)
# logger.addHandler(console)

def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3001'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] =\
        'Content-Type, Authorization'
    return response


@app.route('/testerror')
def testerror():
    """
    This is using to test error.
    ---
    parameters:
    definitions:
    responses:
      400:
        description: A list of colors (may be filtered by palette)
        schema:
          $ref: '#/definitions/Palette'
        examples:
          rgb: ['red', 'green', 'blue']
    """
    logging.warning("this is a test")
    res = make_response(json.dumps("test error"), 400)

    return res


@app.route('/testsetcookie')
def test():
    res = make_response(json.dumps("for set cookie"), 200)
    res.set_cookie(key='coo2', value='haha', expires=time.time()+5)

    print(res.headers)
    return res


class User(UserMixin):
    username = ""

    def __repr__(self):
        return self.username

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username


@login_manager.user_loader
def user_loader(username):
    if username not in users:
        return
    user = User()
    user.id = username
    return user


@app.route('/testforlogin')
@login_required
def testlogin():
    print(current_user.username)
    return json.dumps("test for login")


@app.route('/login', methods=['POST'])
def login():
    data = json.loads(request.data)
    username = data['username']
    if data['password'] == users[username]['password']:
        print('password: %s' % users[username]['password'])
        user = User()
        user.username = username
        print(user)
        print(user.is_authenticated())
        login_user(user, remember=True)

    return json.dumps('login_test')


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return json.dumps('Logged out')


@jwt.user_claims_loader
def add_claims_to_access_token(identity):
    return {
        'hello': identity,
        'foo': [datetime.now()]
    }


@app.route('/login_jwt', methods=['POST'])
def login_jwt():
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
    return make_response(json.dumps('500 server error'), 500)


if __name__ == '__main__':
    app.debug = True
    app.after_request(after_request)

    log_filename = datetime.now().strftime("log/app %Y-%m-%d.log")
    fileHandler = TimedRotatingFileHandler(
        log_filename, when='D', interval=1,
        backupCount=30, encoding='UTF-8', delay=False, utc=False)
    fileHandler.setFormatter(formatter)

    if app.debug is True:
        fileHandler.setLevel(logging.WARNING)
    else:
        fileHandler.setLevel(logging.WARNING)
    logger.addHandler(fileHandler)
    app.run(host='0.0.0.0', port=5000)

