from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
# Remove werkzeug import if only using model's check_password
# from werkzeug.security import check_password_hash

from . import db
from .models import User
# Import the form
from .auth_forms import LoginForm # Make sure this path is correct

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Redirect if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.ping')) # Or redirect to a dashboard later

    form = LoginForm()
    if form.validate_on_submit(): # Handles POST, validates form and CSRF
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            if not user.is_active:
                 flash('Your account is disabled. Please contact support.', 'warning')
                 return redirect(url_for('auth.login'))

            # Log user in
            login_user(user, remember=form.remember_me.data)
            flash('Logged in successfully!', 'success')

            # Redirect to 'next' page if it exists, otherwise to a default page
            next_page = request.args.get('next')
            # Basic security check for next_page (prevent open redirect)
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('auth.profile') # Default redirect after login
            return redirect(next_page)
        else:
            flash('Invalid username or password.', 'danger')
    # For GET request or failed validation, render login template
    return render_template('auth/login.html', title='Sign In', form=form)

@auth.route('/logout')
@login_required # User must be logged in to log out
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login')) # Redirect to login page after logout

@auth.route('/profile')
@login_required # Protected route example
def profile():
     # Render a simple profile page or return data
     return f"Hello, {current_user.username}! This is your protected profile."

# Helper function for validating 'next' URL (important for security)
from urllib.parse import urlparse, urljoin
from flask import request, current_app

def url_parse(url):
     return urlparse(url)

# Consider adding more routes like registration later