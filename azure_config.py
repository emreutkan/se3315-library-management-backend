# Azure deployment configuration for Library Management System - School Project Version
# This configuration uses in-memory databases for simplicity and hardcoded secrets

import os

# Set hardcoded values for school project (not recommended for real applications)
SECRET_KEY = "library-management-super-secret-key-for-school-project-2025"
JWT_SECRET_KEY = "jwt-secret-key-for-school-library-project-not-for-production"

# Use SQLite database (can be in-memory for simplicity)
# For a real app, you'd use a persistent database service like Azure PostgreSQL
DATABASE_URI = "sqlite:///library.db"

# Set environment variables for Azure deployment
os.environ["SECRET_KEY"] = SECRET_KEY
os.environ["JWT_SECRET_KEY"] = JWT_SECRET_KEY
os.environ["DATABASE_URI"] = DATABASE_URI
os.environ["FLASK_ENV"] = "production"
