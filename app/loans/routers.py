from flask import Blueprint, request, jsonify
from app import db
from app.models import Book, BorrowedBook
from datetime import datetime, timedelta
from flask_jwt_extended import jwt_required

loans_bp = Blueprint('loans', __name__)

@loans_bp.route('/assign', methods=['POST'])
@jwt_required()
def assign_book():
    data = request.get_json()
    book = Book.query.get(data['book_id'])
    if not book or not book.available:
        return jsonify({'error': 'Book not available'}), 400

    return_days = int(data.get('days', 7))
    return_date = datetime.utcnow() + timedelta(days=return_days)

    loan = BorrowedBook(user_id=data['user_id'], book_id=data['book_id'], return_date=return_date)
    book.available = False
    db.session.add(loan)
    db.session.commit()
    return jsonify({'message': 'Book assigned successfully'}), 200

@loans_bp.route('/return/<int:book_id>', methods=['POST'])
@jwt_required()
def return_book(book_id):
    book = Book.query.get(book_id)
    if not book or book.available:
        return jsonify({'error': 'Book already returned or not found'}), 400
    book.available = True
    BorrowedBook.query.filter_by(book_id=book_id).delete()
    db.session.commit()
    return jsonify({'message': 'Book returned successfully'}), 200
