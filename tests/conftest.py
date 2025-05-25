import pytest
from app.run import create_app
from app.models import db, User, Book
from app import bcrypt

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
            title="SeedBook",
            author="Author",
            isbn="seed-123",
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
def admin_token(client):
    resp = client.post("/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    return resp.get_json()["access_token"]

@pytest.fixture()
def user_token(client):
    resp = client.post("/auth/login", json={
        "username": "user1",
        "password": "user123"
    })
    return resp.get_json()["access_token"]
