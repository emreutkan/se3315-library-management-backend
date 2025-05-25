import pytest
from app import create_app, db, bcrypt
from app.models import User, Book
from flask_jwt_extended import create_access_token

@pytest.fixture(scope="module")
def app():
    """Create and configure a new app instance for each test module."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "test-secret-key"
    })

    with app.app_context():
        db.create_all()
        # seed users
        admin = User(
            username="admin",
            password_hash=bcrypt.generate_password_hash("admin123").decode(),
            is_admin=True
        )
        user1 = User(
            username="user1",
            password_hash=bcrypt.generate_password_hash("user123").decode(),
            is_admin=False
        )
        db.session.add_all([admin, user1])
        # seed one book
        book = Book(
            title="SeedBook", author="Author", isbn="seed-123", category="Test"
        )
        db.session.add(book)
        db.session.commit()

    yield app

    # Teardown
    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def admin_token(app):
    with app.app_context():
        user = User.query.filter_by(username="admin").first()
        return create_access_token(identity=user.id)

@pytest.fixture
def user_token(app):
    with app.app_context():
        user = User.query.filter_by(username="user1").first()
        return create_access_token(identity=user.id)
