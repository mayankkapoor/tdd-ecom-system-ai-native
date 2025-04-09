import pytest
from flask import url_for
from app import db
from app.models import User, Product
from decimal import Decimal
from tests.test_auth import test_user  # Import the test_user fixture

# Fixture to create a test product
@pytest.fixture(scope='function')
def test_product(test_app):
    with test_app.app_context():
        p = Product(sku='PROD001', name='Test Product One', price=Decimal('19.99'), stock_quantity=50)
        db.session.add(p)
        db.session.commit()
        yield p
        # Clean up
        db.session.delete(p)
        db.session.commit()

# Fixture to log in the test user (assuming test_user fixture exists from Phase 1 tests)
@pytest.fixture(scope='function')
def logged_in_client(test_client, test_user):
     # Log in the user created by the test_user fixture
    test_client.post(url_for('auth.login'), data={
        'username': test_user.username,
        'password': 'password' # Password used in test_user fixture
    }, follow_redirects=True)
    yield test_client
    # Logout not strictly necessary here as client is recreated, but good practice
    test_client.get(url_for('auth.logout'))


# --- Access Control Tests ---
def test_access_product_list_unauthenticated(test_client):
    response = test_client.get(url_for('products.list_products'))
    assert response.status_code == 302 # Redirect
    assert '/auth/login' in response.location  # Check for relative URL path

def test_access_add_product_unauthenticated(test_client):
    response = test_client.get(url_for('products.add_product'))
    assert response.status_code == 302
    assert '/auth/login' in response.location  # Check for relative URL path

# --- Logged-in Tests ---
def test_list_products_page_loads(logged_in_client, test_product):
    response = logged_in_client.get(url_for('products.list_products'))
    assert response.status_code == 200
    assert b'<h1>Products</h1>' in response.data
    assert test_product.sku.encode('utf-8') in response.data # Check if product is listed

def test_add_product_page_loads(logged_in_client):
    response = logged_in_client.get(url_for('products.add_product'))
    assert response.status_code == 200
    assert b'<h1>Add New Product</h1>' in response.data # Check title assuming route sets it
    assert b'SKU' in response.data # Check for form fields

def test_add_product_success(logged_in_client):
    response = logged_in_client.post(url_for('products.add_product'), data={
        'sku': 'NEWPROD01',
        'name': 'New Awesome Product',
        'price': '123.45',
        'stock_quantity': '10',
        'is_active': 'y' # Checkbox value for True
        # Add other required fields from your form
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'<h1>Products</h1>' in response.data # Should redirect to list
    assert b'Product NEWPROD01 added successfully!' in response.data # Check flash message
    # Verify in DB
    with logged_in_client.application.app_context():
        prod = Product.query.filter_by(sku='NEWPROD01').first()
        assert prod is not None
        assert prod.name == 'New Awesome Product'
        assert prod.price == Decimal('123.45')

def test_add_product_validation_error(logged_in_client):
    """Test adding product with invalid data (e.g., negative price)."""
    response = logged_in_client.post(url_for('products.add_product'), data={
        'sku': 'INVALID01',
        'name': 'Invalid Price Prod',
        'description': 'Test product with invalid price',
        'price': '-10.00', # Invalid price
        'stock_quantity': '5',
        'category': 'Test',
        'image_url': '',  # Optional field
        'is_active': 'y',
        'csrf_token': 'dummy'  # This will be replaced by actual CSRF token
    }, follow_redirects=True)

    assert response.status_code == 200 # Should re-render form
    assert b'<h1>Add New Product</h1>' in response.data # Still on Add page
    # Check for validation error message - WTForms might use different wording
    assert b'[' in response.data and b']' in response.data # Error message is wrapped in []
    assert b'0' in response.data # Error message should mention 0 as the minimum

def test_add_product_duplicate_sku(logged_in_client, test_product):
    """Test adding product with an existing SKU."""
    response = logged_in_client.post(url_for('products.add_product'), data={
        'sku': test_product.sku, # Use existing SKU
        'name': 'Duplicate SKU Product',
        'price': '5.00',
        'stock_quantity': '2'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'<h1>Add New Product</h1>' in response.data
    assert b'This SKU is already taken' in response.data # Check custom validator message


def test_edit_product_page_loads(logged_in_client, test_product):
    response = logged_in_client.get(url_for('products.edit_product', sku=test_product.sku))
    assert response.status_code == 200
    assert b'<h1>Edit Product</h1>' in response.data
    assert test_product.sku.encode('utf-8') in response.data # Check if SKU is in form
    assert test_product.name.encode('utf-8') in response.data # Check if name is in form

def test_edit_product_not_found(logged_in_client):
    response = logged_in_client.get(url_for('products.edit_product', sku='NONEXISTENT'))
    assert response.status_code == 404

def test_edit_product_success(logged_in_client, test_product):
    edit_url = url_for('products.edit_product', sku=test_product.sku)
    response = logged_in_client.post(edit_url, data={
        'sku': test_product.sku, # Keep SKU same or change if needed
        'name': 'Updated Product Name', # Change name
        'price': '25.50', # Change price
        'stock_quantity': str(test_product.stock_quantity + 5), # Update stock
        'is_active': 'y'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'<h1>Products</h1>' in response.data # Redirect to list
    assert b'Product PROD001 updated successfully!' in response.data # Flash message

    # Verify update in DB
    with logged_in_client.application.app_context():
        updated_prod = db.session.get(Product, test_product.id) # Use get for PK lookup
        assert updated_prod.name == 'Updated Product Name'
        assert updated_prod.price == Decimal('25.50')
        assert updated_prod.stock_quantity == 55

def test_delete_product_success(logged_in_client, test_product):
    delete_url = url_for('products.delete_product', sku=test_product.sku)
    product_id = test_product.id # Get ID before potential deletion

    response = logged_in_client.post(delete_url, follow_redirects=True)

    assert response.status_code == 200
    assert b'<h1>Products</h1>' in response.data # Redirect to list
    assert b'Product PROD001 deleted.' in response.data # Flash message

    # Verify deleted from DB
    with logged_in_client.application.app_context():
        deleted_prod = db.session.get(Product, product_id)
        assert deleted_prod is None

def test_delete_product_not_found(logged_in_client):
    response = logged_in_client.post(url_for('products.delete_product', sku='NONEXISTENT'))
    assert response.status_code == 404