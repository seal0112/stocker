import boto3
from botocore.exceptions import ClientError
from flask import request, jsonify, current_app

from .. import db
from . import ai_api_key
from .models import AiApiKey
from app.decorators.auth import admin_required


def _ssm_client():
    region = current_app.config.get('AWS_REGION', 'ap-northeast-1')
    return boto3.client('ssm', region_name=region)


def _put_ssm(ssm_path, key_value):
    _ssm_client().put_parameter(
        Name=ssm_path,
        Value=key_value,
        Type='SecureString',
        Overwrite=True,
    )


def _delete_ssm(ssm_path):
    try:
        _ssm_client().delete_parameter(Name=ssm_path)
    except ClientError as e:
        if e.response['Error']['Code'] != 'ParameterNotFound':
            raise


@ai_api_key.route('', methods=['GET'])
@admin_required
def list_keys():
    keys = AiApiKey.query.order_by(AiApiKey.provider, AiApiKey.name).all()
    return jsonify([k.to_dict() for k in keys]), 200


@ai_api_key.route('', methods=['POST'])
@admin_required
def create_key():
    data = request.get_json()
    required = ('name', 'provider', 'key_value')
    if not data or not all(data.get(f) for f in required):
        return jsonify({'error': 'name, provider, key_value are required'}), 400

    if AiApiKey.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Key name already exists'}), 409

    from flask_jwt_extended import get_jwt_identity
    try:
        identity = get_jwt_identity()
        owner = identity.get('username') if identity else None
    except Exception:
        owner = None

    ssm_path = f"/stocker/ai_key/{data['name']}"

    try:
        _put_ssm(ssm_path, data['key_value'])
    except Exception as e:
        return jsonify({'error': f'SSM error: {str(e)}'}), 500

    key = AiApiKey(
        name=data['name'],
        provider=data['provider'],
        owner=owner,
        ssm_path=ssm_path,
        is_active=data.get('is_active', True),
    )
    db.session.add(key)
    db.session.commit()
    return jsonify(key.to_dict()), 201


@ai_api_key.route('/<int:key_id>', methods=['PUT'])
@admin_required
def update_key(key_id):
    key = AiApiKey.query.get_or_404(key_id)
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body is required'}), 400

    # 更新 SSM（若有傳新的 key value）
    if data.get('key_value'):
        try:
            _put_ssm(key.ssm_path, data['key_value'])
        except Exception as e:
            return jsonify({'error': f'SSM error: {str(e)}'}), 500

    for field in ('owner', 'is_active'):
        if field in data:
            setattr(key, field, data[field])

    db.session.commit()
    return jsonify(key.to_dict()), 200


@ai_api_key.route('/<int:key_id>', methods=['DELETE'])
@admin_required
def delete_key(key_id):
    key = AiApiKey.query.get_or_404(key_id)

    try:
        _delete_ssm(key.ssm_path)
    except Exception as e:
        return jsonify({'error': f'SSM error: {str(e)}'}), 500

    db.session.delete(key)
    db.session.commit()
    return jsonify({'message': 'Deleted'}), 200
