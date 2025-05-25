from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.decorators import admin_required
from app.models import Book, BorrowedBook
from app import db
from datetime import datetime

loans_bp = Blueprint("loans", __name__, url_prefix="/api/loans")

@loans_bp.route("/assign", methods=["POST"])
@jwt_required()
@admin_required
def assign_book():
    data = request.get_json() or {}
    book = Book.query.get(data.get("book_id"))
    if not book or not book.available:
        return jsonify({"msg": "Book not available"}), 400

    # parse return_date
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
def return_book(book_id):
    loan = BorrowedBook.query.filter_by(book_id=book_id, returned=False).first()
    if not loan:
        return jsonify({"msg": "No active loan"}), 400

    loan.returned = True
    book = Book.query.get(book_id)
    book.available = True
    db.session.commit()
    return jsonify({"msg": "Book returned"}), 200
