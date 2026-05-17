from flask import request, jsonify

from .. import db
from . import ai_prompt
from .models import AiPrompt
from app.decorators.auth import admin_required, api_auth_required


@ai_prompt.route('', methods=['GET'])
@admin_required
def list_prompts():
    prompts = AiPrompt.query.order_by(AiPrompt.name, AiPrompt.provider).all()
    return jsonify([p.to_dict() for p in prompts]), 200


@ai_prompt.route('/<name>', methods=['GET'])
@api_auth_required
def get_prompt(name):
    provider = request.args.get('provider')
    query = AiPrompt.query.filter_by(name=name, is_active=True)
    if provider:
        query = query.filter_by(provider=provider)
    prompt = query.first()
    if not prompt:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(prompt.to_dict()), 200


@ai_prompt.route('', methods=['POST'])
@admin_required
def create_prompt():
    data = request.get_json()
    if not data or not data.get('name') or not data.get('content'):
        return jsonify({'error': 'name and content are required'}), 400

    existing = AiPrompt.query.filter_by(
        name=data['name'], provider=data.get('provider')
    ).first()
    if existing:
        return jsonify({'error': 'Prompt with this name and provider already exists'}), 409

    from flask_jwt_extended import get_jwt_identity
    try:
        identity = get_jwt_identity()
        created_by = identity.get('username') if identity else None
    except Exception:
        created_by = None

    prompt = AiPrompt(
        name=data['name'],
        provider=data.get('provider'),
        content=data['content'],
        is_active=data.get('is_active', True),
        description=data.get('description'),
        created_by=created_by,
    )
    db.session.add(prompt)
    db.session.commit()
    return jsonify(prompt.to_dict()), 201


@ai_prompt.route('/<int:prompt_id>', methods=['PUT'])
@admin_required
def update_prompt(prompt_id):
    prompt = AiPrompt.query.get_or_404(prompt_id)
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body is required'}), 400

    for field in ('content', 'description', 'is_active'):
        if field in data:
            setattr(prompt, field, data[field])

    db.session.commit()
    return jsonify(prompt.to_dict()), 200


@ai_prompt.route('/<int:prompt_id>', methods=['DELETE'])
@admin_required
def delete_prompt(prompt_id):
    prompt = AiPrompt.query.get_or_404(prompt_id)
    db.session.delete(prompt)
    db.session.commit()
    return jsonify({'message': 'Deleted'}), 200
