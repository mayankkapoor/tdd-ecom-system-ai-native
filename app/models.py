from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db # Import db instance from app package __init__
from sqlalchemy import CheckConstraint
from decimal import Decimal # For price


class User(UserMixin, db.Model):
    __tablename__ = 'users' # Optional: Define table name explicitly

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True, index=True) # Optional email
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(64), nullable=False, default='admin') # Default role is admin for now
    is_active = db.Column(db.Boolean, default=True) # Useful for disabling users

    def set_password(self, password):
        """Hashes the password and stores it."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks if the provided password matches the hash."""
        return check_password_hash(self.password_hash, password)

    # Flask-Login expects these properties/methods if not using UserMixin defaults
    # UserMixin provides suitable defaults for these based on the 'id' field
    # def get_id(self): # Provided by UserMixin
    #     return str(self.id)
    #
    # def is_authenticated(self): # Provided by UserMixin (True for logged-in users)
    #     return True
    #
    # def is_active(self): # Provided by UserMixin (Checks our is_active column)
    #      return self.is_active
    #
    # def is_anonymous(self): # Provided by UserMixin (False for logged-in users)
    #      return False

    def __repr__(self):
        return f'<User {self.username}>'
    
class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    # SKU (Stock Keeping Unit) - unique identifier for the product
    sku = db.Column(db.String(80), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    # Use Numeric for precise decimal values like currency
    price = db.Column(db.Numeric(10, 2), nullable=False)
    category = db.Column(db.String(80), nullable=True, index=True)
    image_url = db.Column(db.String(255), nullable=True)
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    # Optional: Timestamps
    # date_created = db.Column(db.DateTime, default=datetime.utcnow)
    # date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Add constraints directly to the table args or within Column definitions if supported
    __table_args__ = (
        CheckConstraint('price >= 0', name='ck_product_price_non_negative'),
        CheckConstraint('stock_quantity >= 0', name='ck_product_stock_non_negative'),
    )

    def __repr__(self):
        return f'<Product {self.sku}: {self.name}>'

    # Potential helper methods can be added later, e.g.:
    # def adjust_stock(self, quantity_change):
    #     if self.stock_quantity + quantity_change < 0:
    #         raise ValueError("Stock cannot go below zero.")
    #     self.stock_quantity += quantity_change