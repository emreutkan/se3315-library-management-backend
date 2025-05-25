from flask_jwt_extended import get_jwt_identity
from functools import wraps
from flask import jsonify

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = get_jwt_identity()
        if not user or not user.get('is_admin', False):
            return jsonify({'error': 'Admin access required'}), 403
        return fn(*args, **kwargs)
    return wrapper