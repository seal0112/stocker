import json
import logging

from flask import (
    request, make_response, jsonify
)
from flask_jwt_extended import (
    jwt_required, create_access_token, create_refresh_token,
    get_jwt_identity, set_refresh_cookies
)

from . import auth
from . import user_service
from . import login_service


user_serv = user_service.UserService()
login_serv = login_service.LoginService()
logger = logging.getLogger()


# @jwt.user_lookup_loader
# def user_lookup_callback(_jwt_header, jwt_data):
#     identity = jwt_data["sub"]
#     print('********************************************************')
#     print(identity)
#     print('********************************************************')

#     return User.query.filter_by(id=identity['id']).one_or_none()

def make_jwt_repsonse(identity):
    access_token = create_access_token(identity=identity)
    response = make_response(
        jsonify(access_token=access_token), 200
    )
    return response


@auth.route('/login', methods=['POST'])
def login():
    try:
        login_data = request.get_json()
        user_info = login_serv.verify_service[
            login_data['external_type']](login_data)
    except Exception as ex:
        logger.exception('Failed to verify user: %s', ex)
        res = make_response(
            json.dumps(
                'Failed to upgrade the authorization code'), 401)
        return res

    user_id = user_serv.get_user_id(
        user_info.get('external_id', None),
        user_info['external_type']
    )
    if user_id is None:
        if user_info['external_type'] == 'internal':
            res = make_response(
                jsonify(
                    'Account is not exist'), 401)
            return res
        user_id = user_serv.create_user(user_info, login_data['external_type'])

    user = user_serv.get_user(user_id)
    if user.is_active:
        identity = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'picture': user.profile_pic
        }
        response = make_jwt_repsonse(identity)
        refresh_token = create_refresh_token(identity=identity)
        set_refresh_cookies(response, refresh_token)

        return response

    return make_response(
        jsonify('Account is not active'), 403)


@auth.route('/refresh')
@jwt_required(locations=["cookies"], refresh=True)
def refresh():
    identity = get_jwt_identity()
    response = make_jwt_repsonse(identity)

    return response


@auth.route("/logout")
@jwt_required()
def logout():
    response = make_response(
        jsonify({'isAuth': False})
    )
    response.delete_cookie("refresh_token")

    return response


@auth.route("/user_info")
@jwt_required()
def get_user_info():
    current_user = get_jwt_identity()
    return jsonify(current_user), 200
