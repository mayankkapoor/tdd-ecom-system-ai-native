from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config, TestingConfig
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)

    # Load configuration from config class
    if os.environ.get('FLASK_ENV') == 'testing':
         app.config.from_object(TestingConfig)
    else:
         app.config.from_object(config_class)


    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass # Already exists

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register Blueprints
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Register CLI commands if any (e.g., flask seed)
    # app.cli.add_command(...)

    # Add models here to ensure they are known to Flask-Migrate
    from .models import User

    return app