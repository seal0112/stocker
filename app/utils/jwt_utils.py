"""JWT utility functions for Flask-JWT-Extended 4.x compatibility.

In Flask-JWT-Extended 4.x, the JWT 'sub' claim must be a string.
We store user_id as the identity, and additional user info in custom claims.
"""
from flask_jwt_extended import get_jwt_identity, get_jwt


def get_current_user():
    """Get current user info from JWT claims.

    Returns a dict with user info (id, username, email, picture).
    For backward compatibility, this returns the same structure as
    the old get_jwt_identity() when identity was a dict.
    """
    jwt_claims = get_jwt()
    user_id = get_jwt_identity()

    return {
        'id': int(user_id) if user_id else None,
        'username': jwt_claims.get('username'),
        'email': jwt_claims.get('email'),
        'picture': jwt_claims.get('picture')
    }
