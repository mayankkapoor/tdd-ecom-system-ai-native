import pytest
from app import create_app, db

@pytest.fixture(scope='module')
def test_app():
    """Create and configure a new app instance for each test module."""
    # Set environment to testing *before* creating the app
    import os
    os.environ['FLASK_ENV'] = 'testing'
    app = create_app()

    # Establish an application context
    with app.app_context():
        # Create the database and the database table(s)
        db.create_all()

        yield app # Testing happens here

        # Drop the database tables and clean up
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='module')
def test_client(test_app):
    """Create a test client for the app."""
    return test_app.test_client()