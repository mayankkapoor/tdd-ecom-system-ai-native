import os
from dotenv import load_dotenv

# Determine the absolute path of the directory containing config.py
basedir = os.path.abspath(os.path.dirname(__file__))
# Construct the path to the .env file in the project root
dotenv_path = os.path.join(basedir, '.env')

# Load the .env file from the specified path
load_dotenv(dotenv_path=dotenv_path)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-should-really-change-this' # Change this!
    # Default to SQLite if DATABASE_URL is not set
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Add other configurations here, e.g., mail server, etc.

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # Use in-memory SQLite for tests
    WTF_CSRF_ENABLED = False # Disable CSRF forms validation in tests
    SECRET_KEY = 'test-secret-key' # Use a fixed key for tests