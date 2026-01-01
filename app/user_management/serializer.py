from marshmallow import Schema, fields, validate


class RoleSchema(Schema):
    """Schema for role responses."""
    id = fields.Integer(dump_only=True)
    name = fields.String(dump_only=True)
    description = fields.String(dump_only=True)


class UserSchema(Schema):
    """Schema for user responses."""
    id = fields.Integer(dump_only=True)
    username = fields.String(dump_only=True)
    email = fields.String(dump_only=True)
    profile_pic = fields.String(dump_only=True)
    roles = fields.List(fields.String(), dump_only=True)
    active = fields.Boolean(dump_only=True)
    last_login_at = fields.DateTime(dump_only=True)


class UpdateUserRolesSchema(Schema):
    """Schema for updating user roles."""
    role_names = fields.List(
        fields.String(validate=validate.Length(min=1, max=50)),
        required=True,
        validate=validate.Length(min=1)
    )


user_schema = UserSchema()
users_schema = UserSchema(many=True)
role_schema = RoleSchema()
roles_schema = RoleSchema(many=True)
update_user_roles_schema = UpdateUserRolesSchema()
