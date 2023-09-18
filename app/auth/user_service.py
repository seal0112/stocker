import logging

from .models import User
from .. import db


logger = logging.getLogger()


class UserService():

    def __init__(self):
        pass

    def get_user_id(self, external_id, external_type):
        try:
            user = db.session.query(User).filter_by(
                external_id=external_id).filter_by(
                    external_type=external_type).one()
            return user.id
        except Exception as ex:
            logger.exception('Failed to get user id: %s', ex)
            return None

    def get_user(self, user_id):
        user = db.session.query(User).filter_by(id=user_id).one()
        return user

    def create_user(self, personal_data, external_type):
        new_user = User()
        new_user['external_type'] = external_type
        new_user['username'] = personal_data['username']
        if external_type == 'internal':
            print(personal_data['password'])
            new_user.set_password(personal_data['password'])
        else:
            new_user['external_id'] = personal_data['external_id']
            new_user['email'] = personal_data['email']
            new_user['profile_pic'] = personal_data['profile_pic']

        new_user['authenticate'] = True
        new_user['active'] = False

        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception as ex:
            db.session.rollback()
            logger.exception(f'fail create User: {personal_data.name}, exception: {ex}')
            return None
        user_id = self.get_user_id(new_user['external_id'], external_type)
        return user_id
