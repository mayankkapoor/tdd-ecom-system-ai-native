import pytest
from sqlalchemy.exc import IntegrityError
from app import db
from app.models import User, Product
from decimal import Decimal

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

def test_product_creation(test_app):
    """Test creating a product with valid data."""
    with test_app.app_context():
        p = Product(sku='TEST001', name='Test Product', price=Decimal('99.99'), stock_quantity=10)
        db.session.add(p)
        db.session.commit()

        product_from_db = Product.query.filter_by(sku='TEST001').first()
        assert product_from_db is not None
        assert product_from_db.name == 'Test Product'
        assert product_from_db.price == Decimal('99.99')
        assert product_from_db.stock_quantity == 10
        assert product_from_db.is_active is True # Default value
        assert product_from_db.description is None # Default nullable

def test_product_price_constraint(test_app):
    """Test that price cannot be negative."""
    with test_app.app_context():
        p = Product(sku='NEGPRICE01', name='Negative Price', price=Decimal('-1.00'))
        db.session.add(p)
        with pytest.raises(IntegrityError): # Or specific DB error if known
             db.session.commit()
        db.session.rollback() # Clean up session

def test_product_stock_constraint(test_app):
    """Test that stock quantity cannot be negative."""
    with test_app.app_context():
        # Test direct creation with negative stock
        p = Product(sku='NEGSTOCK01', name='Negative Stock', price=Decimal('10.00'), stock_quantity=-5)
        db.session.add(p)
        with pytest.raises(IntegrityError): # Or specific DB error
             db.session.commit()
        db.session.rollback()

        # Test updating stock to negative (if using a helper method later)
        # p_existing = Product(sku='UPDTEST01', name='Update Test', price=Decimal('5.00'), stock_quantity=2)
        # db.session.add(p_existing)
        # db.session.commit()
        # with pytest.raises(ValueError): # Assuming helper raises ValueError
        #     p_existing.adjust_stock(-3)
        # db.session.rollback()


def test_product_unique_sku(test_app):
    """Test that product SKU must be unique."""
    with test_app.app_context():
        p1 = Product(sku='UNIQUE01', name='First Product', price=Decimal('1.00'))
        db.session.add(p1)
        db.session.commit()

        p2 = Product(sku='UNIQUE01', name='Second Product', price=Decimal('2.00'))
        db.session.add(p2)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()
