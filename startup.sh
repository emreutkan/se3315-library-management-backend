# startup.sh - Azure App Service startup command
# This file instructs Azure how to start your Flask application

# First, import the configuration to set environment variables
python azure_config.py

# Start the Flask app using Gunicorn
gunicorn --config gunicorn.conf.py wsgi:app
