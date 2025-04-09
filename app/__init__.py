from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager # Import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config, TestingConfig
import os

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager() # Instantiate LoginManager
csrf = CSRFProtect() # Initialize CSRF protection
login_manager.login_view = 'auth.login' # Route name (Blueprint.view_function) for login page
login_manager.login_message_category = 'info' # Optional: category for flash messages

# Define the user loader function required by Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from .models import User # Import here to avoid circular imports
    return User.query.get(int(user_id))

def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)

    # Load configuration (updated logic)
    if os.environ.get('FLASK_ENV') == 'testing':
         app.config.from_object(TestingConfig)
    else:
         app.config.from_object(config_class)
         # Ensure SECRET_KEY is set for non-testing environments if using Flask-WTF
         if not app.config.get('SECRET_KEY'):
             raise ValueError("SECRET_KEY must be set in config for production/development.")


    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app) # Initialize LoginManager
    csrf.init_app(app) # Initialize CSRF protection

    # Register Blueprints
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Import and register the Auth blueprint (add this later in step 10)
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .products import products_bp # Import products blueprint
    app.register_blueprint(products_bp, url_prefix='/products') # Register it

    from . import models

    return app