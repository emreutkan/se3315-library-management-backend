from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flasgger import Swagger

# extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    # init extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # swagger
    Swagger(app)

    from flask_jwt_extended import get_jwt
    from flask_jwt_extended import verify_jwt_in_request

    @jwt.additional_claims_loader
    def add_claims(identity):
        # This function is only called when creating new tokens
        # In tests, we directly provide the claims
        from app.models import User
        try:
            # Using Session.get() instead of Query.get() to fix SQLAlchemy warning
            user = db.session.get(User, identity)
            if user:
                return {"is_admin": user.is_admin}
        except Exception:
            # If any error occurs, return default non-admin claims
            pass
        return {"is_admin": False}

    @jwt.user_identity_loader
    def user_identity_lookup(identity):
        # Convert to string to ensure it works consistently
        return str(identity)

    # register blueprints
    from app.auth.routes  import auth_bp
    from app.users.routes import users_bp
    from app.books.routes import books_bp
    from app.loans.routes import loans_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(loans_bp)

    return app
