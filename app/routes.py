from flask import Blueprint, jsonify

main = Blueprint('main', __name__)

@main.route('/ping')
def ping():
    """Health check endpoint."""
    return 'pong'

# Add other main routes here later (e.g., home page)