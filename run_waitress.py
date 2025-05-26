from waitress import serve
from application import app

if __name__ == '__main__':
    print("Starting application with Waitress on http://localhost:5000")
    serve(app, host='localhost', port=5000, threads=4)
