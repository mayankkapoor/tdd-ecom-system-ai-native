import os
import click
from app.models import User # Make sure User is imported
from app import db         # Make sure db is imported
from dotenv import load_dotenv

# Load .env file from the project root
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    print("Warning: .env file not found.")


# Set FLASK_ENV based on FLASK_DEBUG, default to 'production' if not set
FLASK_DEBUG = os.environ.get('FLASK_DEBUG', '0')
if FLASK_DEBUG == '1':
    os.environ['FLASK_ENV'] = 'development'
# Check for explicit 'testing' environment
elif os.environ.get('FLASK_ENV') != 'testing':
     os.environ['FLASK_ENV'] = 'production'


from app import create_app, db # Import db if needed for cli commands later

# Create app using factory, config determined by FLASK_ENV inside create_app
app = create_app()

# Example of adding a shell context processor (optional)
@app.shell_context_processor
def make_shell_context():
  from app import models # Import models here if you want them in `flask shell`
  return {'db': db, 'User': models.User} # Add your models here later

@app.cli.command("create-admin")
@click.argument("username")
@click.argument("password")
@click.option('--email', default=None, help='Optional email address for the admin user.')
def create_admin(username, password, email):
    """Creates a new admin user."""
    # Check if user already exists
    if User.query.filter_by(username=username).first() is not None:
        click.echo(f"Error: Username '{username}' already exists.")
        return
    if email and User.query.filter_by(email=email).first() is not None:
         click.echo(f"Error: Email '{email}' already exists.")
         return

    user = User(username=username, email=email, role='admin') # Explicitly setting role=admin
    user.set_password(password)
    db.session.add(user)
    try:
        db.session.commit()
        click.echo(f"Admin user '{username}' created successfully.")
    except Exception as e:
        db.session.rollback()
        click.echo(f"Error creating user: {e}")
        
# The following is useful if you run `python run.py` directly,
# but `flask run` is generally preferred as it uses the app factory.
if __name__ == '__main__':
    print(f"Running in {os.environ.get('FLASK_ENV', 'production')} mode.")
    app.run(debug=(os.environ.get('FLASK_ENV') == 'development'))