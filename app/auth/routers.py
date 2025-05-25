from flask import Blueprint, request, jsonify
from app import db, bcrypt
from app.models import User
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and bcrypt.check_password_hash(user.password_hash, data['password']):
        token = create_access_token(identity={'id': user.id, 'username': user.username, 'is_admin': user.is_admin})
        return jsonify({'token': token, 'is_admin': user.is_admin}), 200
    return jsonify({'error': 'Invalid credentials'}), 401