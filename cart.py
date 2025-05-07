"""
Shopping cart functionality for IELTS GenAI Prep.
This module provides a shopping cart to allow users to add multiple assessment products
before proceeding to checkout.
"""

from flask import session, redirect, url_for, render_template, flash, request
from decimal import Decimal

# Import assessment products data
from add_assessment_routes import assessment_products


def initialize_cart():
    """Initialize an empty cart if it doesn't exist."""
    if 'cart' not in session:
        session['cart'] = []


def add_to_cart(product_id):
    """
    Add a product to the cart.
    
    Args:
        product_id (str): The ID of the product to add.
        
    Returns:
        bool: True if added successfully, False otherwise.
    """
    initialize_cart()
    
    # Check if product exists
    if product_id not in assessment_products:
        flash('Invalid product selected.', 'danger')
        return False
    
    # Get product details
    product = assessment_products[product_id]
    
    # Check if product is already in cart
    for item in session['cart']:
        if item['id'] == product_id:
            flash(f"{product['name']} is already in your cart.", 'info')
            return True
    
    # Add product to cart
    cart_item = {
        'id': product_id,
        'name': product['name'],
        'description': product['description'],
        'price': product['price'] / 100  # Convert from cents to dollars for display
    }
    
    session['cart'].append(cart_item)
    session.modified = True
    
    flash(f"{product['name']} added to your cart.", 'success')
    return True


def remove_from_cart(product_id):
    """
    Remove a product from the cart.
    
    Args:
        product_id (str): The ID of the product to remove.
        
    Returns:
        bool: True if removed successfully, False otherwise.
    """
    initialize_cart()
    
    # Find and remove the product
    for i, item in enumerate(session['cart']):
        if item['id'] == product_id:
            product_name = item['name']
            del session['cart'][i]
            session.modified = True
            flash(f"{product_name} removed from your cart.", 'success')
            return True
    
    flash('Product not found in your cart.', 'warning')
    return False


def get_cart_items():
    """
    Get all items in the cart.
    
    Returns:
        list: List of cart items.
    """
    initialize_cart()
    return session['cart']


def get_cart_total():
    """
    Calculate the total price of all items in the cart.
    
    Returns:
        float: Total price in dollars (not cents).
    """
    initialize_cart()
    total = sum(item['price'] for item in session['cart'])
    return total


def clear_cart():
    """Clear all items from the cart."""
    session['cart'] = []
    session.modified = True


def get_product_ids():
    """
    Get all product IDs in the cart.
    
    Returns:
        list: List of product IDs.
    """
    initialize_cart()
    return [item['id'] for item in session['cart']]


def get_cart_count():
    """
    Get the number of items in the cart.
    
    Returns:
        int: Number of items.
    """
    initialize_cart()
    return len(session['cart'])