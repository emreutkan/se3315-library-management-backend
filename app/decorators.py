from functools import wraps
from flask import abort
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def admin_required(fn):
    """Ensure the current JWT has is_admin=True."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if not claims.get("is_admin", False):
            abort(403, description="Admin privilege required")
        return fn(*args, **kwargs)
    return wrapper
