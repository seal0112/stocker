from marshmallow import Schema, fields, validate


class ApiTokenSchema(Schema):
    """Schema for API token responses."""
    id = fields.String(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    token_prefix = fields.String(dump_only=True)
    token = fields.String(dump_only=True)  # Only included on creation
    scopes = fields.List(fields.String(), load_default=[])
    expires_at = fields.DateTime(allow_none=True)
    last_used_at = fields.DateTime(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    is_active = fields.Boolean(dump_only=True)


class CreateTokenSchema(Schema):
    """Schema for creating a new token."""
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    scopes = fields.List(fields.String(), load_default=[])
    expires_in_days = fields.Integer(
        allow_none=True,
        validate=validate.Range(min=1, max=365),
        load_default=None
    )


api_token_schema = ApiTokenSchema()
api_tokens_schema = ApiTokenSchema(many=True)
create_token_schema = CreateTokenSchema()
