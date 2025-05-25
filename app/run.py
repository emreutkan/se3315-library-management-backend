# app/run.py

from app import create_app, db, bcrypt
from app.models import User, Book
from datetime import datetime

app = create_app()

if __name__ == "__main__":
    # only register this when running as a script, not on import
    @app.before_first_request
    def seed_data():
        with app.app_context():
            db.create_all()

            # seed users if not already present
            if not User.query.filter_by(username="admin").first():
                admin = User(
                    username="admin",
                    password_hash=bcrypt.generate_password_hash("admin123").decode("utf-8"),
                    is_admin=True,
                )
                user1 = User(
                    username="user1",
                    password_hash=bcrypt.generate_password_hash("user123").decode("utf-8"),
                    is_admin=False,
                )
                db.session.add_all([admin, user1])

            # seed books if empty
            if not Book.query.first():
                books = [
                    Book(title='Suç ve Ceza', author='Fyodor Dostoyevski', isbn='9789754589078', category='Roman'),
                    Book(title='1984', author='George Orwell', isbn='9789750718533', category='Distopya'),
                    Book(title='Yabancı', author='Albert Camus', isbn='9789750726477', category='Roman'),
                    Book(title='Dönüşüm', author='Franz Kafka', isbn='9789944885003', category='Roman'),
                    Book(title='Hayvan Çiftliği', author='George Orwell', isbn='9789750718618', category='Siyasi'),
                    Book(title='Sefiller', author='Victor Hugo', isbn='9786053329185', category='Tarihî Roman'),
                    Book(title='Bilinmeyen Bir Kadının Mektubu', author='Stefan Zweig', isbn='9786052950366',
                         category='Psikoloji'),
                    Book(title='Küçük Prens', author='Antoine de Saint-Exupéry', isbn='9789750719400',
                         category='Çocuk'),
                    Book(title='Tutunamayanlar', author='Oğuz Atay', isbn='9789754700114', category='Postmodern'),
                    Book(title='Bir İdam Mahkumunun Son Günü', author='Victor Hugo', isbn='9786053322896',
                         category='Felsefe'),
                    Book(title='Simyacı', author='Paulo Coelho', isbn='9789750726438', category='Kişisel Gelişim'),
                    Book(title='Satranç', author='Stefan Zweig', isbn='9786053608099', category='Psikoloji'),
                    Book(title='İnce Mehmed', author='Yaşar Kemal', isbn='9789750807106', category='Epik Roman'),
                    Book(title='Denemeler', author='Montaigne', isbn='9789752630122', category='Deneme'),
                    Book(title='Böyle Buyurdu Zerdüşt', author='Friedrich Nietzsche', isbn='9786052951424',
                         category='Felsefe'),
                    Book(title='Uçurtma Avcısı', author='Khaled Hosseini', isbn='9789752894203', category='Roman')
                ]
                db.session.add_all(books)

            db.session.commit()

    app.run(debug=True)
