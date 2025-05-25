def test_list_books_success(client, admin_token):
    res = client.get("/api/books", headers={
        "Authorization": f"Bearer {admin_token}"
    })
    assert res.status_code == 200
    books = res.get_json()
    assert isinstance(books, list)
    # the seeded book is present
    assert any(b["title"] == "SeedBook" for b in books)

def test_add_book_forbidden(client, user_token):
    res = client.post("/api/books", json={
        "title":"B","author":"A","isbn":"1234","category":"C"
    }, headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 403

def test_add_book_success(client, admin_token):
    res = client.post("/api/books", json={
        "title":"New","author":"Auth","isbn":"isbn-456","category":"Cat"
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 201
    b = res.get_json()
    assert b["isbn"] == "isbn-456"

def test_add_book_conflict(client, admin_token, app):
    # First, get the seeded book's ISBN
    with app.app_context():
        from app.models import Book
        seeded_book = Book.query.filter_by(title="SeedBook").first()
        seeded_isbn = seeded_book.isbn

    # Try to add a book with that ISBN
    res = client.post("/api/books", json={
        "title":"Dup","author":"Auth","isbn": seeded_isbn,"category":"Cat"
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 400
