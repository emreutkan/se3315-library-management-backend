from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from flasgger import swag_from
from app.decorators import admin_required
from app.models import Book
from app import db

books_bp = Blueprint("books", __name__, url_prefix="/api/books")

@books_bp.route("", methods=["GET"])
@jwt_required()
@swag_from({
    'tags': ['Books'],
    'responses': {
        200: {
            'description': 'List of books',
            'schema': {
                'type': 'array',
                'items': {'$ref': '#/definitions/Book'}
            }
        }
    }
})
def list_books():
    """Retrieve all books."""
    books = Book.query.all()
    return jsonify([b.to_dict() for b in books])

@books_bp.route("", methods=["POST"])
@jwt_required()
@admin_required
@swag_from({
    'tags': ['Books'],
    'parameters': [
        {
            'in': 'body',
            'name': 'book',
            'schema': {
                'type': 'object',
                'required': ['title','author','isbn','category'],
                'properties': {
                    'title': {'type': 'string'},
                    'author': {'type': 'string'},
                    'isbn': {'type': 'string'},
                    'category': {'type': 'string'}
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Book created',
            'schema': {'$ref': '#/definitions/Book'}
        },
        400: {'description': 'ISBN already exists'},
        403: {'description': 'Admin privilege required'}
    }
})
def add_book():
    """Create a new book."""
    data = request.get_json() or {}
    if Book.query.filter_by(isbn=data.get("isbn")).first():
        return jsonify({"msg": "ISBN already exists"}), 400

    book = Book(
        title=data["title"],
        author=data["author"],
        isbn=data["isbn"],
        category=data["category"],
        available=True
    )
    db.session.add(book)
    db.session.commit()
    return jsonify(book.to_dict()), 201
