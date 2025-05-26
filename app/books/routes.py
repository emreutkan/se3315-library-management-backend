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
                'items': {
                    '$ref': '#/definitions/Book',
                    'properties': {
                        'id': {'type': 'integer'},
                        'title': {'type': 'string'},
                        'author': {'type': 'string'},
                        'isbn': {'type': 'string'},
                        'category': {'type': 'string'},
                        'available': {'type': 'boolean'},
                        'due_date': {'type': 'string', 'format': 'date', 'description': 'Return date for borrowed books'},
                        'is_overdue': {'type': 'boolean', 'description': 'Indicates if the book is past its due date'}
                    }
                }
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

@books_bp.route("/search", methods=["GET"])
@jwt_required()
@swag_from({
    'tags': ['Books'],
    'parameters': [
        {
            'name': 'title',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Title to search for (partial match)'
        },
        {
            'name': 'author',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Author to search for (partial match)'
        },
        {
            'name': 'isbn',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'ISBN to search for (exact match)'
        },
        {
            'name': 'category',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Category to filter by (partial match)'
        },
        {
            'name': 'available',
            'in': 'query',
            'type': 'boolean',
            'required': False,
            'description': 'Filter by availability status'
        }
    ],
    'responses': {
        200: {
            'description': 'List of matching books',
            'schema': {
                'type': 'array',
                'items': {'$ref': '#/definitions/Book'}
            }
        }
    }
})
def search_books():
    """Search for books using various filters."""
    query = Book.query

    # Apply filters based on query parameters
    if request.args.get('title'):
        query = query.filter(Book.title.ilike(f'%{request.args.get("title")}%'))

    if request.args.get('author'):
        query = query.filter(Book.author.ilike(f'%{request.args.get("author")}%'))

    if request.args.get('isbn'):
        query = query.filter(Book.isbn == request.args.get('isbn'))

    if request.args.get('category'):
        query = query.filter(Book.category.ilike(f'%{request.args.get("category")}%'))

    if 'available' in request.args:
        available = request.args.get('available').lower() in ('true', '1', 't')
        query = query.filter(Book.available == available)

    books = query.all()
    return jsonify([b.to_dict() for b in books])

