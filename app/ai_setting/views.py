import boto3
from botocore.exceptions import BotoCoreError, ClientError

from flask import jsonify, request
from flask.views import MethodView

from app import db
from app.log_config import get_logger
from app.decorators.auth import admin_required, api_auth_required
from . import ai_setting
from .models import AiSetting

logger = get_logger(__name__)

VALID_PROVIDERS = {'gemini', 'claude'}

VALID_MODELS = {
    'gemini': {
        'gemini-3.5-flash',
        'gemini-3.1-pro-preview',
        'gemini-3-flash-preview',
        'gemini-3.1-flash-lite',
        'gemini-2.5-pro',
        'gemini-2.5-flash',
        'gemini-2.5-flash-lite',
    },
    'claude': {
        'claude-opus-4-7',
        'claude-sonnet-4-6',
        'claude-haiku-4-5-20251001',
    },
}


def _get_setting():
    setting = AiSetting.query.first()
    if not setting:
        setting = AiSetting(provider='gemini', updated_by='system')
        db.session.add(setting)
        db.session.commit()
    return setting


class AiSettingApi(MethodView):

    @api_auth_required
    def get(self):
        """Get current AI provider setting."""
        return jsonify(_get_setting().to_dict())

    @admin_required
    def put(self):
        """Update AI provider setting."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Request body is required'}), 400
        except Exception:
            return jsonify({'error': 'Invalid JSON format'}), 400

        provider = data.get('provider')
        if provider not in VALID_PROVIDERS:
            return jsonify({'error': f'Invalid provider. Must be one of: {", ".join(VALID_PROVIDERS)}'}), 400

        model = data.get('model') or None
        if model and model not in VALID_MODELS.get(provider, set()):
            return jsonify({'error': f'Invalid model for provider {provider}'}), 400

        from app.utils.jwt_utils import get_current_user
        try:
            current_user = get_current_user()
            updated_by = current_user.get('username', 'admin')
        except Exception:
            updated_by = 'admin'

        setting = _get_setting()
        setting.provider = provider
        setting.model = model
        setting.updated_by = updated_by

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error updating ai_setting: {e}', exc_info=True)
            return jsonify({'error': 'Failed to update setting'}), 500

        return jsonify(setting.to_dict())


SSM_KEY_MAP = {
    'gemini': '/stocker/gemini-api-key',
    'claude': '/stocker/claude-api-key',
}


@ai_setting.route('/token', methods=['PUT'])
@admin_required
def update_ai_token():
    """Store AI provider API key in SSM Parameter Store."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
    except Exception:
        return jsonify({'error': 'Invalid JSON format'}), 400

    provider = data.get('provider')
    token = data.get('token', '').strip()

    if provider not in VALID_PROVIDERS:
        return jsonify({'error': f'Invalid provider. Must be one of: {", ".join(VALID_PROVIDERS)}'}), 400
    if not token:
        return jsonify({'error': 'token is required'}), 400

    ssm_name = SSM_KEY_MAP[provider]
    try:
        ssm = boto3.client('ssm')
        ssm.put_parameter(
            Name=ssm_name,
            Value=token,
            Type='SecureString',
            Overwrite=True
        )
    except (BotoCoreError, ClientError) as e:
        logger.error(f'Failed to update SSM parameter {ssm_name}: {e}', exc_info=True)
        return jsonify({'error': 'Failed to update API key'}), 500

    return jsonify({'message': f'{provider} API key updated'}), 200


ai_setting.add_url_rule('',
    view_func=AiSettingApi.as_view('AiSettingApi'),
    methods=['GET', 'PUT'])
