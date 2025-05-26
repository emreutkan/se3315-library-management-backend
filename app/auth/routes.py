from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token
from flasgger import swag_from
from app.models import User
from app import bcrypt
import os
import traceback

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
    try:
        # Log request details for debugging
        current_app.logger.info("Login attempt received")

        # Check database connection
        try:
            user_count = User.query.count()
            current_app.logger.info(f"Database connection successful. User count: {user_count}")
        except Exception as db_error:
            current_app.logger.error(f"Database error: {str(db_error)}")
            return jsonify({"error": "Database connection error", "details": str(db_error)}), 500

        # Check database file existence (for SQLite)
        if 'sqlite:///' in current_app.config['SQLALCHEMY_DATABASE_URI']:
            db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            if not os.path.isabs(db_path):
                # Make path absolute if it's relative
                db_path = os.path.join(current_app.root_path, '..', db_path)

            current_app.logger.info(f"Database path: {db_path}")
            current_app.logger.info(f"Database exists: {os.path.exists(db_path)}")

        data = request.get_json() or {}
        current_app.logger.info(f"Login attempt for user: {data.get('username')}")

        user = User.query.filter_by(username=data.get("username")).first()
        if not user or not bcrypt.check_password_hash(user.password_hash, data.get("password", "")):
            current_app.logger.info("Authentication failed: bad credentials")
            return jsonify({"msg": "Bad credentials"}), 401

        # Explicitly convert user ID to string to avoid JWT subject issues
        access_token = create_access_token(identity=str(user.id))
        current_app.logger.info(f"Authentication successful for user: {user.username}")
        return jsonify(access_token=access_token), 200
    except Exception as e:
        current_app.logger.error(f"Unexpected error in login: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

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

