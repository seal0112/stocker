import json
from app.log_config import get_logger

from flask import (
    request, make_response, jsonify
)
from flask_jwt_extended import (
    jwt_required, create_access_token, create_refresh_token,
    set_access_cookies, set_refresh_cookies,
    unset_jwt_cookies
)

from . import auth
from . import user_service
from . import login_service
from app.utils.jwt_utils import get_current_user


user_serv = user_service.UserService()
login_serv = login_service.LoginService()
logger = get_logger(__name__)


# @jwt.user_lookup_loader
# def user_lookup_callback(_jwt_header, jwt_data):
#     identity = jwt_data["sub"]
#     print('********************************************************')
#     print(identity)
#     print('********************************************************')

#     return User.query.filter_by(id=identity['id']).one_or_none()

def make_jwt_repsonse(user_id, additional_claims=None):
    """Create JWT response with user_id as identity and additional claims."""
    access_token = create_access_token(
        identity=str(user_id),
        additional_claims=additional_claims or {}
    )
    response = make_response(
        jsonify(access_token=access_token), 200
    )
    set_access_cookies(response, access_token)
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
        # Update last login time
        user_serv.update_last_login(user_id)

        # Flask-JWT-Extended 4.x: identity must be string, use additional_claims for extra data
        additional_claims = {
            'username': user.username,
            'email': user.email,
            'picture': user.profile_pic
        }
        response = make_jwt_repsonse(user.id, additional_claims)
        refresh_token = create_refresh_token(
            identity=str(user.id),
            additional_claims=additional_claims
        )
        set_refresh_cookies(response, refresh_token)

        return response

    return make_response(
        jsonify('Account is not active'), 403)


@auth.route('/refresh')
@jwt_required(locations=["cookies"], refresh=True)
def refresh():
    current_user = get_current_user()
    additional_claims = {
        'username': current_user['username'],
        'email': current_user['email'],
        'picture': current_user['picture']
    }
    response = make_jwt_repsonse(current_user['id'], additional_claims)

    return response


@auth.route("/logout")
@jwt_required()
def logout():
    response = make_response(
        jsonify({'isAuth': False})
    )
    unset_jwt_cookies(response)

    return response


@auth.route("/user_info")
@jwt_required()
def get_user_info():
    current_user = get_current_user()
    user = user_serv.get_user(current_user['id'])

    return jsonify({
        **current_user,
        'roles': user.role_names if user else []
    }), 200
