import pytest
from sqlalchemy.exc import IntegrityError
from app import db
from app.models import User

# Use test_app fixture implicitly provided by pytest-flask via conftest.py
# The app context is needed for db operations

def test_user_creation(test_app):
    """Test creating a new user."""
    with test_app.app_context():
        u = User(username='john', email='john@example.com')
        u.set_password('cat')
        db.session.add(u)
        db.session.commit()

        user_from_db = User.query.filter_by(username='john').first()
        assert user_from_db is not None
        assert user_from_db.username == 'john'
        assert user_from_db.email == 'john@example.com'
        assert user_from_db.role == 'admin' # Default role
        assert user_from_db.password_hash != 'cat' # Ensure it's hashed

def test_password_setting_and_verification(test_app):
    """Test password hashing and checking."""
    with test_app.app_context():
        u = User(username='susan')
        u.set_password('dog')
        db.session.add(u)
        db.session.commit()

        assert u.password_hash is not None
        assert u.check_password('dog') is True
        assert u.check_password('cat') is False

def test_duplicate_username(test_app):
    """Test that adding users with duplicate usernames raises IntegrityError."""
    with test_app.app_context():
        u1 = User(username='peter', email='peter1@example.com')
        u1.set_password('pass1')
        db.session.add(u1)
        db.session.commit()

        u2 = User(username='peter', email='peter2@example.com')
        u2.set_password('pass2')
        db.session.add(u2)

        # Expect an IntegrityError when trying to commit the duplicate
        with pytest.raises(IntegrityError):
            db.session.commit()

        # Rollback the session to clean up after the expected error
        db.session.rollback()

def test_duplicate_email(test_app):
    """Test that adding users with duplicate emails raises IntegrityError."""
    with test_app.app_context():
        u1 = User(username='user1', email='test@example.com')
        u1.set_password('pass1')
        db.session.add(u1)
        db.session.commit()

        u2 = User(username='user2', email='test@example.com')
        u2.set_password('pass2')
        db.session.add(u2)

        # Expect an IntegrityError
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()