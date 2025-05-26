from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from flasgger import swag_from
from app.models import User
from app import bcrypt

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.route("/login", methods=["POST"])
@swag_from({
    'tags': ['Authentication'],
    'parameters': [
        {
            'in': 'body',
            'name': 'credentials',
            'schema': {
                '$ref': '#/definitions/LoginCredentials'
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Access token',
            'schema': {
                '$ref': '#/definitions/Token'
            }
        },
        401: {'description': 'Bad credentials'}
    },
    'summary': 'Obtain JWT token for API authentication',
    'description': 'Use this endpoint to get a JWT token. After obtaining the token, click the "Authorize" button at the top of the page, enter "Bearer YOUR_TOKEN" in the value field, and click "Authorize" to enable testing of protected endpoints.'
})
def login():
    """Authenticate user and return JWT."""
    data = request.get_json() or {}
    user = User.query.filter_by(username=data.get("username")).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, data.get("password", "")):
        return jsonify({"msg": "Bad credentials"}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token), 200

@auth_bp.route("/test-auth", methods=["GET"])
@swag_from({
    'tags': ['Authentication'],
    'security': [{'Bearer': []}],
    'responses': {
        200: {'description': 'Authentication successful'},
        401: {'description': 'Authentication failed'}
    },
    'summary': 'Test if your token is valid',
    'description': 'Use this endpoint to verify if your JWT token is working properly. This endpoint requires authentication.'
})
def test_auth():
    """Test endpoint requiring authentication."""
    return jsonify({"msg": "Authentication successful"}), 200

