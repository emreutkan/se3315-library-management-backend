from datetime import date
from app import db

class User(db.Model):
    __tablename__ = 'user'  # Explicitly define the table name
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
    __tablename__ = 'book'  # Explicitly define the table name
    id        = db.Column(db.Integer, primary_key=True)
    title     = db.Column(db.String(200), nullable=False)
    author    = db.Column(db.String(120), nullable=False)
    isbn      = db.Column(db.String(20), unique=True, nullable=False)
    category  = db.Column(db.String(80), nullable=False)
    available = db.Column(db.Boolean, default=True, nullable=False)

    def to_dict(self):
        result = {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "category": self.category,
            "available": self.available
        }

        # If the book is not available, include the due date
        if not self.available:
            # Find the active loan for this book
            active_loan = BorrowedBook.query.filter_by(book_id=self.id, returned=False).first()
            if active_loan:
                result["due_date"] = str(active_loan.return_date)
                result["is_overdue"] = active_loan.is_overdue()

        return result

class BorrowedBook(db.Model):
    __tablename__ = 'borrowed_book'  # Explicitly define the table name
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    book_id     = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    return_date = db.Column(db.Date, nullable=False)
    returned    = db.Column(db.Boolean, default=False, nullable=False)

    def is_overdue(self):
        """Check if the book is overdue."""
        return not self.returned and date.today() > self.return_date

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "book_id": self.book_id,
            "return_date": str(self.return_date),
            "returned": self.returned,
            "is_overdue": self.is_overdue()
        }
