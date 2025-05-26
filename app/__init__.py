from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flasgger import Swagger
import logging

# extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    # Setup logging
    logging.basicConfig(level=logging.INFO)
    app.logger.info("Starting library management system")

    # Log the database URI (without exposing sensitive info)
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    if 'sqlite:///' in db_uri:
        app.logger.info(f"Using SQLite database at: {db_uri.replace('sqlite:///', '')}")
    else:
        app.logger.info("Using database connection from environment variable")

    # Enable CORS for all routes
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # init extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Initialize database with tables and admin user
    with app.app_context():
        app.logger.info("Creating database tables if they don't exist")
        db.create_all()
        app.logger.info("Database tables created successfully")

        # Import User model here to avoid circular imports
        from app.models import User

        try:
            # Use a simple count query first to verify the table exists
            user_count = db.session.query(db.func.count(User.id)).scalar()
            app.logger.info(f"Found {user_count} existing users")

            # Only after confirming the table works, check for admin
            admin_user = User.query.filter_by(username="admin").first()
            if not admin_user:
                app.logger.info("Creating admin user")
                admin_user = User(
                    username="admin",
                    password_hash=bcrypt.generate_password_hash("admin123").decode('utf-8'),
                    is_admin=True
                )
                db.session.add(admin_user)
                db.session.commit()
                app.logger.info("Admin user created successfully")
            else:
                app.logger.info("Admin user already exists")
        except Exception as e:
            app.logger.error(f"Error during database initialization: {str(e)}")
            # Continue app initialization despite DB errors
            # This allows the app to start and show proper error messages

    # swagger configuration with definitions
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec",
                "route": "/apispec.json",
                "rule_filter": lambda rule: True,  # all in
                "model_filter": lambda tag: True,  # all in
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/",
    }

    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "Library Management System API",
            "description": "API for managing books, users, and loans",
            "version": "1.0"
        },
        # Add authentication section to template
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: \"Bearer {token}\""
            }
        },
        "security": [
            {"Bearer": []}
        ],
        "definitions": {
            "Book": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "title": {"type": "string"},
                    "author": {"type": "string"},
                    "isbn": {"type": "string"},
                    "category": {"type": "string"},
                    "available": {"type": "boolean"},
                    "due_date": {"type": "string", "format": "date", "description": "Return date for borrowed books"},
                    "is_overdue": {"type": "boolean", "description": "Indicates if the book is past its due date"}
                }
            },
            "User": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "username": {"type": "string"},
                    "is_admin": {"type": "boolean"}
                }
            },
            "BorrowedBook": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "user_id": {"type": "integer"},
                    "book_id": {"type": "integer"},
                    "return_date": {"type": "string", "format": "date"},
                    "returned": {"type": "boolean"},
                    "is_overdue": {"type": "boolean"}
                }
            },
            "LoginCredentials": {
                "type": "object",
                "properties": {
                    "username": {"type": "string", "example": "admin"},
                    "password": {"type": "string", "example": "admin123"}
                },
                "required": ["username", "password"]
            },
            "Token": {
                "type": "object",
                "properties": {
                    "access_token": {"type": "string"}
                }
            }
        }
    }

    Swagger(app, config=swagger_config, template=swagger_template)

    # Register blueprints
    from app.auth import auth_bp
    from app.books import books_bp
    from app.loans import loans_bp
    from app.users import users_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(loans_bp)
    app.register_blueprint(users_bp)

    # Return the Flask application
    return app
