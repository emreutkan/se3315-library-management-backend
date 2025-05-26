from app import create_app
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Create the Flask application
app = create_app()

# Register error handlers to log exceptions
@app.errorhandler(500)
def handle_500_error(e):
    app.logger.error(f"500 error: {str(e)}")
    return "Internal Server Error", 500

@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    return "Internal Server Error", 500

# This allows Azure Web App to find your application
if __name__ == "__main__":
    app.run()
