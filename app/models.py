from datetime import date
from app import db

class User(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin      = db.Column(db.Boolean, default=False, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "is_admin": self.is_admin
        }

class Book(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    title     = db.Column(db.String(200), nullable=False)
    author    = db.Column(db.String(120), nullable=False)
    isbn      = db.Column(db.String(20), unique=True, nullable=False)
    category  = db.Column(db.String(80), nullable=False)
    available = db.Column(db.Boolean, default=True, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "category": self.category,
            "available": self.available
        }

class BorrowedBook(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    book_id     = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    return_date = db.Column(db.Date, nullable=False)
    returned    = db.Column(db.Boolean, default=False, nullable=False)
