from datetime import date, timedelta

def test_assign_book_forbidden(client, user_token):
    due = date.today().isoformat()
    res = client.post("/api/loans/assign", json={
        "book_id": 1, "user_id": 2, "return_date": due
    }, headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 403

def test_assign_and_return_cycle(client, admin_token, app):
    due = (date.today() + timedelta(days=7)).isoformat()
    # assign
    res = client.post("/api/loans/assign", json={
        "book_id": 1, "user_id": 2, "return_date": due
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    with app.app_context():
        from app.models import BorrowedBook
        loan = BorrowedBook.query.filter_by(book_id=1, returned=False).first()
        assert loan is not None

    # return
    res2 = client.post("/api/loans/return/1", headers={
        "Authorization": f"Bearer {admin_token}"
    })
    assert res2.status_code == 200
    with app.app_context():
        from app.models import BorrowedBook
        loan = BorrowedBook.query.filter_by(book_id=1, returned=True).first()
        assert loan is not None
