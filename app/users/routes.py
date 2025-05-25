from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from flasgger import swag_from
from app.decorators import admin_required
from app.models import User
from app import db, bcrypt

users_bp = Blueprint("users", __name__, url_prefix="/api/users")

@users_bp.route("", methods=["GET"])
@jwt_required()
@admin_required
@swag_from({
    'tags': ['Users'],
    'responses': {
        200: {
            'description': 'List of users',
            'schema': {
                'type': 'array',
                'items': {'$ref': '#/definitions/User'}
            }
        },
        403: {'description': 'Admin privilege required'}
    }
})
def list_users():
    """Retrieve all users."""
    users = User.query.all()
    return jsonify([u.to_dict() for u in users])

@users_bp.route("", methods=["POST"])
@jwt_required()
@admin_required
@swag_from({
    'tags': ['Users'],
    'parameters': [
        {
            'in': 'body',
            'name': 'user',
            'schema': {
                'type': 'object',
                'required': ['username', 'password'],
                'properties': {
                    'username': {'type': 'string'},
                    'password': {'type': 'string'},
                    'is_admin': {'type': 'boolean'}
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'User created',
            'schema': {'$ref': '#/definitions/User'}
        },
        400: {'description': 'Username already exists'},
        403: {'description': 'Admin privilege required'}
    }
})
def add_user():
    """Create a new user."""
    data = request.get_json() or {}
    if User.query.filter_by(username=data.get("username")).first():
        return jsonify({"msg": "Username already exists"}), 400

    pw_hash = bcrypt.generate_password_hash(data.get("password", "")).decode()
    user = User(
        username=data["username"],
        password_hash=pw_hash,
        is_admin=bool(data.get("is_admin", False))
    )
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201
