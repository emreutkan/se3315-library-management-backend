from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

# Create extensions
bcrypt = Bcrypt()
db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
    app.config['JWT_SECRET_KEY'] = 'super-secret-key'

    CORS(app)
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    from app.auth.routes import auth_bp
    from app.users.routes import users_bp
    from app.books.routes import books_bp
    from app.loans.routes import loans_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(books_bp, url_prefix='/api/books')
    app.register_blueprint(loans_bp, url_prefix='/api/loans')

    with app.app_context():
        db.create_all()

    return app