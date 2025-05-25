from flask import Blueprint, request, jsonify
from app import db
from app.models import Book
from flask_jwt_extended import jwt_required

books_bp = Blueprint('books', __name__)

@books_bp.route('/', methods=['GET'])
@jwt_required()
def get_books():
    books = Book.query.all()
    return jsonify([{
        'id': b.id, 'title': b.title, 'author': b.author,
        'isbn': b.isbn, 'category': b.category, 'available': b.available
    } for b in books])

@books_bp.route('/', methods=['POST'])
@jwt_required()
def add_book():
    data = request.get_json()
    if Book.query.filter_by(isbn=data['isbn']).first():
        return jsonify({'error': 'ISBN already exists'}), 409
    book = Book(
        title=data['title'], author=data['author'],
        isbn=data['isbn'], category=data['category'], available=True
    )
    db.session.add(book)
    db.session.commit()
    return jsonify({'message': 'Book added successfully'}), 201
