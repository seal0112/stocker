from app import db
from app.models import User, Role, UserRole


class UserService:
    """Service for managing users and their roles."""

    def get_all_users(self, page=None, per_page=None):
        """Get all users with their roles, with optional pagination."""
        query = User.query.order_by(User.id)

        if page is not None and per_page is not None:
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            return {
                'items': pagination.items,
                'total': pagination.total,
                'page': pagination.page,
                'per_page': pagination.per_page,
                'pages': pagination.pages
            }

        return {'items': query.all(), 'total': query.count()}

    def get_user_by_id(self, user_id):
        """Get a specific user by ID."""
        return User.query.filter_by(id=user_id).first()

    def get_all_roles(self):
        """Get all available roles."""
        return Role.query.order_by(Role.id).all()

    def update_user_roles(self, user_id, role_names, assigned_by=None):
        """
        Update user roles.

        Args:
            user_id: The user ID to update
            role_names: List of role names to assign
            assigned_by: The user ID who is assigning the roles

        Returns:
            Updated User object or None if user not found

        Raises:
            ValueError: If any role name is invalid
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        # Validate all role names exist
        roles = []
        for role_name in role_names:
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                raise ValueError(f"Role '{role_name}' not found")
            roles.append(role)

        # Ensure 'user' role is always included
        user_role = Role.query.filter_by(name='user').first()
        if user_role and user_role not in roles:
            roles.append(user_role)

        # Clear existing roles and add new ones
        UserRole.query.filter_by(user_id=user_id).delete()

        for role in roles:
            user_role_entry = UserRole(
                user_id=user_id,
                role_id=role.id,
                assigned_by=assigned_by
            )
            db.session.add(user_role_entry)

        db.session.commit()

        # Refresh user to get updated roles
        db.session.refresh(user)
        return user

    def update_user_status(self, user_id, active):
        """
        Update user active status.

        Args:
            user_id: The user ID to update
            active: Boolean indicating if user should be active

        Returns:
            Updated User object or None if user not found
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        user.active = active
        db.session.commit()
        db.session.refresh(user)
        return user
