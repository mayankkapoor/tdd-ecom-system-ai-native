from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db # Import db instance from app package __init__

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