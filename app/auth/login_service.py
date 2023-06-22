import requests

from flask import (
    current_app
)
from google.oauth2 import id_token
from google.auth.transport import requests as grequests


class LoginService():
    def __init__(self):
        self.verify_service = {
            'google': self.verify_google,
            'facebook': self.verify_facebook,
            'internal': self.verify_internal
        }

    def verify_google(self, login_data):
        # Specify the client_id of the app that accesses the backend:
        client_id = current_app.config[
            'CLIENT_SECRET']['google']['CLIENT_ID']
        social_media_info = id_token.verify_oauth2_token(
            login_data['token'],
            grequests.Request(),
            client_id
        )

        # Or, if multiple clients access the backend server:
        # idinfo = id_token.verify_oauth2_token(token, requests.Request())
        # if idinfo['aud'] not in [client_id_1, client_id_2, client_id_3]:
        #     raise ValueError('Could not verify audience.')
        if social_media_info['iss'] not in [
            'accounts.google.com', 'https://accounts.google.com'
        ]:
            raise ValueError('Wrong issuer.')

        if social_media_info['aud'] != client_id:
            raise Exception('Could not verify audience.')

        user_info = {
            'external_type': 'google',
            'external_id': social_media_info['sub'],
            'username': social_media_info['name'],
            'email': social_media_info['email'],
            'profile_pic': social_media_info['picture'],
        }

        return user_info

    def verify_facebook(self, login_data):
        app_id = current_app.config[
            'CLIENT_SECRET']['facebook']['app_id']
        app_secret = current_app.config[
            'CLIENT_SECRET']['facebook']['app_secret']

        url = "https://graph.facebook.com/oauth/access_token"
        user_data = {
            "client_id": app_id,
            "client_secret": app_secret,
            "fb_exchange_token": login_data['token'],
            "redirect_uri": "http://localhost:5000",
            "grant_type": "fb_exchange_token"
        }
        payload = requests.post(url, data=user_data, timeout=10)
        if payload.status_code != 200:
            raise Exception('Could not get facebook user data.')

        token = payload.json()['access_token']

        personal_url = (
            'https://graph.facebook.com/v7.0/me?'
            + f'access_token={token}&fields=name,id,email'
        )

        pic_url = (
            'https://graph.facebook.com/v7.0/me/picture?'
            f'access_token={token}&redirect=0&height=200&width=200'
        )

        social_media_info = requests.get(personal_url, timeout=10).json()
        picture_data = requests.get(pic_url, timeout=10).json()
        social_media_info['profile_pic'] = picture_data['data']['url']

        user_info = {
            'external_type': 'facebook',
            'external_id': social_media_info['id'],
            'username': social_media_info['name'],
            'email': social_media_info['email'],
            'profile_pic': social_media_info['profile_pic'],
        }

        return user_info

    def verify_internal(self, login_data):
        return login_data
