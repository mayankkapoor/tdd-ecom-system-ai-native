from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, URL, ValidationError
from .models import Product # Import Product to check SKU uniqueness
from . import db # Import db from app package

class ProductForm(FlaskForm):
    sku = StringField('SKU', validators=[DataRequired(), Length(min=3, max=80)])
    name = StringField('Product Name', validators=[DataRequired(), Length(min=3, max=120)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=5000)])
    price = DecimalField('Price', validators=[DataRequired(), NumberRange(min=0)], places=2)
    category = StringField('Category', validators=[Optional(), Length(max=80)])
    image_url = StringField('Image URL', validators=[Optional(), URL(), Length(max=255)])
    stock_quantity = IntegerField('Stock Quantity', validators=[DataRequired(), NumberRange(min=0)])
    is_active = BooleanField('Product Active', default=True)
    submit = SubmitField('Save Product')

    # Add validation for unique SKU - needs access to the original SKU during edit
    def __init__(self, original_sku=None, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.original_sku = original_sku

    def validate_sku(self, sku):
        # If the SKU hasn't changed or it's a new product, check normally
        if self.original_sku is None or sku.data.lower() != self.original_sku.lower():
            product = Product.query.filter(db.func.lower(Product.sku) == db.func.lower(sku.data)).first()
            if product:
                raise ValidationError('This SKU is already taken. Please choose a different one.')