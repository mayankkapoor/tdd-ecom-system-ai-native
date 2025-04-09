import pytest
from flask import url_for, get_flashed_messages, session
from flask_login import current_user
from app import db
from app.models import User

# Helper fixture to create a user for testing login
@pytest.fixture(scope='function') # Function scope to ensure clean user for each test
def test_user(test_app):
    with test_app.app_context():
        u = User(username='testuser', email='test@example.com')
        u.set_password('password')
        db.session.add(u)
        db.session.commit()
        yield u # Provide the user to the test
        # Clean up after test
        db.session.delete(u)
        db.session.commit()

def test_login_page_loads(test_client, app_context):
    """Test that the login page loads correctly."""
    response = test_client.get(url_for('auth.login'))
    assert response.status_code == 200
    assert b'<h1>Login</h1>' in response.data # Check for unique content

def test_correct_login(test_client, test_user, app_context):
    """Test logging in with correct credentials."""
    response = test_client.post(url_for('auth.login'), data={
        'username': test_user.username,
        'password': 'password' # The correct password set in fixture
    }, follow_redirects=True) # Follow redirects to see the final page

    assert response.status_code == 200 # Should redirect to a success page (e.g., profile)
    # Check content of the redirected page (e.g., the profile page)
    assert f'Welcome, {test_user.username}!'.encode('utf-8') in response.data
    # Check that the user is now logged in via the session context
    with test_client.session_transaction() as sess:
         assert sess['_user_id'] == str(test_user.id)

def test_login_wrong_password(test_client, test_user, app_context):
    """Test logging in with incorrect password."""
    # Make sure we're not already logged in
    with test_client.session_transaction() as sess:
        if '_user_id' in sess:
            del sess['_user_id']
    
    response = test_client.post(url_for('auth.login'), data={
        'username': test_user.username,
        'password': 'wrongpassword'
    }, follow_redirects=False)  # Don't follow redirects

    assert response.status_code == 200 # Should re-render login page
    assert b'<h1>Login</h1>' in response.data # Still on login page
    # Check for flash message (depends on implementation in route)
    assert b'Invalid username or password' in response.data # Assuming flash message is rendered

def test_login_user_not_found(test_client, app_context):
    """Test logging in with a username that doesn't exist."""
    response = test_client.post(url_for('auth.login'), data={
        'username': 'nonexistentuser',
        'password': 'password'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'<h1>Login</h1>' in response.data
    assert b'Invalid username or password' in response.data

def test_logout(test_client, test_user, app_context):
    """Test logging out."""
    # First, log in the user
    test_client.post(url_for('auth.login'), data={
        'username': test_user.username,
        'password': 'password'
    })

    # Now, log out
    response = test_client.get(url_for('auth.logout'), follow_redirects=True) # Assuming logout uses GET for simplicity here
    assert response.status_code == 200
    # Should redirect to login or home page, check for content there
    assert b'<h1>Login</h1>' in response.data # Assuming redirect to login
    # Verify user is logged out by accessing a protected route
    profile_response = test_client.get(url_for('auth.profile'))
    assert profile_response.status_code == 302 # Should redirect to login

def test_access_protected_route_unauthenticated(test_client, app_context):
    """Test accessing a protected route redirects to login."""
    response = test_client.get(url_for('auth.profile'), follow_redirects=False) # Don't follow redirect here
    assert response.status_code == 302 # Found redirect
    assert '/auth/login' in response.location # Check redirect location

def test_access_protected_route_authenticated(test_client, test_user, app_context):
    """Test accessing protected route after logging in."""
    # Log in
    test_client.post(url_for('auth.login'), data={
        'username': test_user.username,
        'password': 'password'
    })

    # Access protected route
    response = test_client.get(url_for('auth.profile'))
    assert response.status_code == 200
    assert b'<h1>Profile</h1>' in response.data
    assert test_user.username.encode('utf-8') in response.data