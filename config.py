import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'super-secret-key')

    # Use a writable location on Azure (home/site/wwwroot/data)
    # but keep the default location for local development
    if 'WEBSITE_HOSTNAME' in os.environ:  # Check if running on Azure
        # Make sure the data directory exists
        data_dir = os.path.join(os.environ.get('HOME', ''), 'site', 'wwwroot', 'data')
        os.makedirs(data_dir, exist_ok=True)
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(data_dir, "library.db")}'
    else:
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///library.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-string')
    # Swagger config
    SWAGGER = {
        'title': 'Library Management API',
        'uiversion': 3
    }
