from flask import Blueprint, request, jsonify
from app import db, bcrypt
from app.models import User
from flask_jwt_extended import jwt_required

users_bp = Blueprint('users', __name__)

@users_bp.route('/', methods=['GET'])
@jwt_required()
def get_users():
    users = User.query.all()
    return jsonify([{'id': u.id, 'username': u.username, 'is_admin': u.is_admin} for u in users])

@users_bp.route('/', methods=['POST'])
@jwt_required()
def add_user():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 409
    hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(username=data['username'], password_hash=hashed_pw, is_admin=data.get('is_admin', False))
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201
