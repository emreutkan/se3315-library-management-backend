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
        from app.models import User
        user = User.query.get(identity)
        return {"is_admin": user.is_admin}

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
