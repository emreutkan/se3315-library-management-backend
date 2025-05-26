from app import create_app

# Create Flask application
app = create_app()

# This is needed for Azure App Service
application = app

if __name__ == "__main__":
    app.run()
