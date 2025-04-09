from flask import Blueprint, jsonify, render_template
from flask_login import login_required

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
@login_required
def index():
    """Home page."""
    return render_template('index.html')

@main.route('/ping')
def ping():
    """Health check endpoint."""
    return 'pong'

# Add other main routes here later (e.g., home page)