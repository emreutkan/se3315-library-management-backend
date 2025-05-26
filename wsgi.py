from app import create_app

# Create the Flask application instance
# This needs to be named 'app' for Azure App Service to find it properly
app = create_app()

# Add this for Azure App Service to find the application object
application = app

if __name__ == "__main__":
    app.run()
