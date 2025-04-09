from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user # Import current_user if needed for roles later
from . import db
from .models import Product
from .product_forms import ProductForm
from sqlalchemy.exc import IntegrityError

products_bp = Blueprint('products', __name__, template_folder='templates/products')

@products_bp.route('/')
@login_required
def list_products():
    page = request.args.get('page', 1, type=int)
    per_page = 10 # Example pagination
    pagination = Product.query.order_by(Product.name).paginate(page=page, per_page=per_page, error_out=False)
    products = pagination.items
    return render_template('list_products.html', products=products, pagination=pagination, title="Products")

@products_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        # Check SKU uniqueness again explicitly here in case of race conditions,
        # though form validation should handle most cases.
        existing_product = Product.query.filter(db.func.lower(Product.sku) == db.func.lower(form.sku.data)).first()
        if existing_product:
             flash('SKU already exists.', 'danger')
             # Re-rendering might clear other fields depending on setup, consider alternatives
             return render_template('product_form.html', title='Add New Product', form=form)

        new_product = Product(
            sku=form.sku.data,
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            category=form.category.data,
            image_url=form.image_url.data,
            stock_quantity=form.stock_quantity.data,
            is_active=form.is_active.data
        )
        db.session.add(new_product)
        try:
            db.session.commit()
            flash(f'Product {new_product.sku} added successfully!', 'success')
            return redirect(url_for('products.list_products'))
        except IntegrityError as e:
            db.session.rollback()
            # Log the error e
            flash(f'Database error occurred: {e}', 'danger') # More specific error might be needed
        except Exception as e:
             db.session.rollback()
             flash(f'An error occurred: {e}', 'danger')

    # For GET request or failed validation
    return render_template('product_form.html', title='Add New Product', form=form)

@products_bp.route('/<sku>')
@login_required
def view_product(sku):
    product = Product.query.filter(db.func.lower(Product.sku) == db.func.lower(sku)).first_or_404()
    return render_template('view_product.html', product=product, title=f"View {product.name}")


@products_bp.route('/<sku>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(sku):
    product = Product.query.filter(db.func.lower(Product.sku) == db.func.lower(sku)).first_or_404()
    # Pass original SKU to form for validation check
    form = ProductForm(obj=product, original_sku=product.sku)

    if form.validate_on_submit():
        # Update product fields from form data
        product.sku = form.sku.data # Be careful if SKU is allowed to change
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.category = form.category.data
        product.image_url = form.image_url.data
        product.stock_quantity = form.stock_quantity.data
        product.is_active = form.is_active.data
        try:
            db.session.commit()
            flash(f'Product {product.sku} updated successfully!', 'success')
            return redirect(url_for('products.list_products'))
        except IntegrityError as e:
             db.session.rollback()
             # This could happen if changing SKU to an existing one
             flash(f'Database error: Could not update product. SKU may already exist. {e}', 'danger')
             # Re-render form with error, might need to handle form repopulation better
             return render_template('product_form.html', title='Edit Product', form=form, product=product)
        except Exception as e:
             db.session.rollback()
             flash(f'An error occurred: {e}', 'danger')

    elif request.method == 'GET':
        # Pre-populate form with existing product data is handled by passing obj=product to form constructor
        pass

    return render_template('product_form.html', title='Edit Product', form=form, product=product) # Pass product for context maybe

@products_bp.route('/<sku>/delete', methods=['POST'])
@login_required
def delete_product(sku):
    product = Product.query.filter(db.func.lower(Product.sku) == db.func.lower(sku)).first_or_404()
    try:
        db.session.delete(product)
        db.session.commit()
        flash(f'Product {product.sku} deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting product {product.sku}: {e}', 'danger')
        # Log the error
    return redirect(url_for('products.list_products'))
