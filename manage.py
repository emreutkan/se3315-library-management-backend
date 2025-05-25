import click
from flask.cli import with_appcontext

from app import create_app, db, bcrypt
from app.models import User, Book

app = create_app()

@app.cli.command("seed")
@with_appcontext
def seed():
    """Reset and seed the database with sample data."""
    click.echo("⚠️  Dropping and recreating database...")
    db.drop_all()
    db.create_all()

    click.echo("🔑 Creating users...")
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

    click.echo("📚 Adding sample books...")
    samples = [
        {"title": "Suç ve Ceza", "author": "Fyodor Dostoyevski", "isbn": "9789754589078", "category": "Roman"},
        {"title": "1984",          "author": "George Orwell",        "isbn": "9789750718533", "category": "Distopya"},
        {"title": "Yabancı",       "author": "Albert Camus",         "isbn": "9789750726477", "category": "Roman"},
    ]
    for b in samples:
        db.session.add(Book(**b))

    db.session.commit()
    click.echo("✅ Database seeded!")
