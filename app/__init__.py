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

    # Import models here to ensure they are registered before create_all()
    from app import models # Import all models

    # Initialize database with tables and admin user
    with app.app_context():
        app.logger.info("Creating database tables if they don't exist")
        db.create_all()
        app.logger.info("Database tables created successfully")

        # User model is now available via models.User
        try:
            # Use a simple count query first to verify the table exists
            user_count = db.session.query(db.func.count(models.User.id)).scalar()
            app.logger.info(f"Found {user_count} existing users")

            # Check for admin user
            admin_user = models.User.query.filter_by(username="admin").first()
            if not admin_user:
                app.logger.info("Creating admin user")
                admin_user = models.User(
                    username="admin",
                    password_hash=bcrypt.generate_password_hash("admin123").decode('utf-8'),
                    is_admin=True
                )
                db.session.add(admin_user)
                db.session.commit()
                app.logger.info("Admin user created successfully")
            else:
                app.logger.info("Admin user already exists")

            # Check for regular user
            regular_user = models.User.query.filter_by(username="user").first()
            if not regular_user:
                app.logger.info("Creating regular user")
                regular_user = models.User(
                    username="user",
                    password_hash=bcrypt.generate_password_hash("user123").decode('utf-8'),
                    is_admin=False
                )
                db.session.add(regular_user)
                db.session.commit()
                app.logger.info("Regular user created successfully")
            else:
                app.logger.info("Regular user already exists")

            # Check if books table is empty and populate with sample data if it is
            book_count = db.session.query(db.func.count(models.Book.id)).scalar()
            app.logger.info(f"Found {book_count} existing books")

            if book_count == 0:
                app.logger.info("Populating database with sample books")
                # Add sample books
                sample_books = [
                    models.Book(
                        title="To Kill a Mockingbird",
                        author="Harper Lee",
                        isbn="9780061120084",
                        category="Fiction",
                        available=True
                    ),
                    models.Book(
                        title="1984",
                        author="George Orwell",
                        isbn="9780451524935",
                        category="Science Fiction",
                        available=True
                    ),
                    models.Book(
                        title="The Great Gatsby",
                        author="F. Scott Fitzgerald",
                        isbn="9780743273565",
                        category="Fiction",
                        available=True
                    ),
                    models.Book(
                        title="Pride and Prejudice",
                        author="Jane Austen",
                        isbn="9780141439518",
                        category="Romance",
                        available=True
                    ),
                    models.Book(
                        title="The Hobbit",
                        author="J.R.R. Tolkien",
                        isbn="9780547928227",
                        category="Fantasy",
                        available=True
                    )
                ]

                db.session.bulk_save_objects(sample_books)
                db.session.commit()
                app.logger.info("Sample books added successfully")
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

    # Add a route to handle /robots*.txt requests
    @app.route('/robots<path:filename>.txt')
    def robots_txt(filename):
        return "User-agent: *\nDisallow:", 200, {'Content-Type': 'text/plain'}

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
