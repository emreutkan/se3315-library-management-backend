from app import create_app, db, bcrypt
from app.models import User, Book

app = create_app()

@app.before_first_request
def seed_data():
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password_hash=bcrypt.generate_password_hash('admin123').decode('utf-8'), is_admin=True)
        user = User(username='user1', password_hash=bcrypt.generate_password_hash('user123').decode('utf-8'), is_admin=False)
        db.session.add_all([admin, user])

    if not Book.query.first():
        sample_books = [
            Book(title='Suç ve Ceza', author='Fyodor Dostoyevski', isbn='9789754589078', category='Roman'),
            Book(title='1984', author='George Orwell', isbn='9789750718533', category='Distopya'),
            Book(title='Yabancı', author='Albert Camus', isbn='9789750726477', category='Roman'),
            Book(title='Dönüşüm', author='Franz Kafka', isbn='9789944885003', category='Roman')
        ]
        db.session.add_all(sample_books)

    db.session.commit()

if __name__ == "__main__":
    app.run(debug=True)