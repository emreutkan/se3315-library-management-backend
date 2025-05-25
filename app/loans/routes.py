from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from flasgger import swag_from
from app.decorators import admin_required
from app.models import Book, BorrowedBook
from app import db
from datetime import datetime

loans_bp = Blueprint("loans", __name__, url_prefix="/api/loans")

@loans_bp.route("/assign", methods=["POST"])
@jwt_required()
@admin_required
@swag_from({
    'tags': ['Loans'],
    'parameters': [
        {
            'in': 'body',
            'name': 'loan',
            'schema': {
                'type': 'object',
                'required': ['book_id','user_id','return_date'],
                'properties': {
                    'book_id': {'type': 'integer'},
                    'user_id': {'type': 'integer'},
                    'return_date': {'type': 'string', 'format': 'date'}
                }
            }
        }
    ],
    'responses': {
        200: {'description': 'Book assigned'},
        400: {'description': 'Book not available or invalid date'},
        403: {'description': 'Admin privilege required'}
    }
})
def assign_book():
    """Assign a book to a user."""
    data = request.get_json() or {}
    # Using db.session.get() instead of Query.get()
    book = db.session.get(Book, data.get("book_id"))
    if not book or not book.available:
        return jsonify({"msg": "Book not available"}), 400

    try:
        due = datetime.fromisoformat(data.get("return_date")).date()
    except Exception:
        return jsonify({"msg": "Invalid return_date format"}), 400

    book.available = False
    loan = BorrowedBook(
        user_id=data["user_id"],
        book_id=book.id,
        return_date=due
    )
    db.session.add(loan)
    db.session.commit()
    return jsonify({"msg": "Book assigned"}), 200

@loans_bp.route("/return/<int:book_id>", methods=["POST"])
@jwt_required()
@admin_required
@swag_from({
    'tags': ['Loans'],
    'parameters': [
        {
            'in': 'path',
            'name': 'book_id',
            'type': 'integer',
            'required': True,
            'description': 'ID of the book to return'
        }
    ],
    'responses': {
        200: {'description': 'Book returned'},
        400: {'description': 'No active loan'},
        403: {'description': 'Admin privilege required'}
    }
})
def return_book(book_id):
    """Return a borrowed book."""
    loan = BorrowedBook.query.filter_by(book_id=book_id, returned=False).first()
    if not loan:
        return jsonify({"msg": "No active loan"}), 400

    loan.returned = True
    # Using db.session.get() instead of Query.get()
    book = db.session.get(Book, book_id)
    book.available = True
    db.session.commit()
    return jsonify({"msg": "Book returned"}), 200
