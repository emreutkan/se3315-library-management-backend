import pytest
from app import create_app
from app.models import db, User, Book
from app import bcrypt
import uuid
from flask_jwt_extended import create_access_token

@pytest.fixture(scope="module")
def app():
    # create the Flask app in testing mode
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "test-secret-key",
    })

    # set up the DB
    with app.app_context():
        db.create_all()
        # seed users only if they don't exist
        if not User.query.filter_by(username="admin").first():
            admin = User(
                username="admin",
                password_hash=bcrypt.generate_password_hash("admin123").decode(),
                is_admin=True
            )
            db.session.add(admin)

        if not User.query.filter_by(username="user1").first():
            user1 = User(
                username="user1",
                password_hash=bcrypt.generate_password_hash("user123").decode(),
                is_admin=False
            )
            db.session.add(user1)

        db.session.commit()

        # Generate unique ISBN to avoid conflicts between tests
        unique_isbn = f"seed-{uuid.uuid4().hex[:8]}"
        book = Book(
            title="SeedBook",
            author="Author",
            isbn=unique_isbn,
            category="Test"
        )
        db.session.add(book)
        db.session.commit()

    yield app

    # teardown
    with app.app_context():
        db.drop_all()

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def admin_token(app):
    # Create a token with admin claims directly
    with app.app_context():
        return create_access_token(identity=1, additional_claims={"is_admin": True})

@pytest.fixture()
def user_token(app):
    # Create a token with non-admin claims directly
    with app.app_context():
        return create_access_token(identity=2, additional_claims={"is_admin": False})
