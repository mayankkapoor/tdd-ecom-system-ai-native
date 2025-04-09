import os
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


# The following is useful if you run `python run.py` directly,
# but `flask run` is generally preferred as it uses the app factory.
if __name__ == '__main__':
    print(f"Running in {os.environ.get('FLASK_ENV', 'production')} mode.")
    app.run(debug=(os.environ.get('FLASK_ENV') == 'development'))