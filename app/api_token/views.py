import logging

from flask import request, jsonify
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app import db
from app.models import ApiToken
from app.decorators import moderator_required
from . import api_token
from .token_service import TokenService
from .serializer import api_token_schema, api_tokens_schema, create_token_schema

logger = logging.getLogger(__name__)
token_service = TokenService()


class ApiTokenListView(MethodView):
    """API for listing and creating tokens."""

    @jwt_required()
    def get(self):
        """List all tokens for the current user."""
        current_user = get_jwt_identity()
        tokens = token_service.get_user_tokens(current_user['id'])
        return jsonify(api_tokens_schema.dump(tokens)), 200

    @moderator_required
    def post(self):
        """Create a new API token. Requires admin or moderator role."""
        current_user = get_jwt_identity()
        user_id = current_user['id']

        # Check token limit
        if not token_service.can_create_token(user_id):
            return jsonify({
                "error": f"Maximum {ApiToken.MAX_TOKENS_PER_USER} tokens allowed per user"
            }), 400

        # Validate request body
        try:
            data = create_token_schema.load(request.get_json() or {})
        except ValidationError as err:
            return jsonify({"error": err.messages}), 400

        # Create token
        try:
            token_obj, plain_token = token_service.create_token(
                user_id=user_id,
                name=data['name'],
                scopes=data.get('scopes', []),
                expires_in_days=data.get('expires_in_days')
            )
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating token: {e}", exc_info=True)
            return jsonify({"error": "Failed to create token"}), 500

        # Return token with plain value (only time it's visible)
        result = api_token_schema.dump(token_obj)
        result['token'] = plain_token
        return jsonify(result), 201


class ApiTokenDetailView(MethodView):
    """API for managing individual tokens."""

    @jwt_required()
    def get(self, token_id):
        """Get a specific token."""
        current_user = get_jwt_identity()
        token_obj = token_service.get_token_by_id(token_id, current_user['id'])

        if not token_obj:
            return jsonify({"error": "Token not found"}), 404

        return jsonify(api_token_schema.dump(token_obj)), 200

    @jwt_required()
    def delete(self, token_id):
        """Revoke/delete a token."""
        current_user = get_jwt_identity()

        if not token_service.revoke_token(token_id, current_user['id']):
            return jsonify({"error": "Token not found"}), 404

        return '', 204


class ApiTokenRegenerateView(MethodView):
    """API for regenerating a token."""

    @jwt_required()
    def post(self, token_id):
        """Regenerate a token with a new value."""
        current_user = get_jwt_identity()

        try:
            plain_token = token_service.regenerate_token(token_id, current_user['id'])
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error regenerating token: {e}", exc_info=True)
            return jsonify({"error": "Failed to regenerate token"}), 500

        if not plain_token:
            return jsonify({"error": "Token not found or inactive"}), 404

        token_obj = token_service.get_token_by_id(token_id, current_user['id'])
        result = api_token_schema.dump(token_obj)
        result['token'] = plain_token
        return jsonify(result), 200


# Register URL rules
api_token.add_url_rule(
    '',
    view_func=ApiTokenListView.as_view('api_token_list'),
    methods=['GET', 'POST']
)

api_token.add_url_rule(
    '/<token_id>',
    view_func=ApiTokenDetailView.as_view('api_token_detail'),
    methods=['GET', 'DELETE']
)

api_token.add_url_rule(
    '/<token_id>/regenerate',
    view_func=ApiTokenRegenerateView.as_view('api_token_regenerate'),
    methods=['POST']
)
