from app import create_app

# Create the Flask application
app = create_app()

# This allows Azure Web App to find your application
if __name__ == "__main__":
    app.run()
