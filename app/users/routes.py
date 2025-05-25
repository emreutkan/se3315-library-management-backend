from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.decorators import admin_required
from app.models import User
from app import db, bcrypt

users_bp = Blueprint("users", __name__, url_prefix="/api/users")

@users_bp.route("", methods=["GET"])
@jwt_required()
@admin_required
def list_users():
    users = User.query.all()
    return jsonify([u.to_dict() for u in users])

@users_bp.route("", methods=["POST"])
@jwt_required()
@admin_required
def add_user():
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
