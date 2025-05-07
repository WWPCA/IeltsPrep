"""
Shopping cart routes for IELTS GenAI Prep.
This module defines routes for the shopping cart functionality.
"""

from flask import Blueprint, redirect, url_for, render_template, flash, session, request
from datetime import datetime

import cart
from payment_services import create_stripe_checkout_session

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/')
def view_cart():
    """Display the shopping cart page."""
    cart_items = cart.get_cart_items()
    cart_total = cart.get_cart_total()
    
    return render_template(
        'cart.html', 
        title='Shopping Cart',
        cart_items=cart_items,
        cart_total=cart_total
    )

@cart_bp.route('/add/<product_id>')
def add_to_cart(product_id):
    """Add a product to the cart."""
    success = cart.add_to_cart(product_id)
    
    # Redirect back to referring page or assessment products page
    next_page = request.args.get('next') or url_for('assessment_products_page')
    return redirect(next_page)

@cart_bp.route('/remove/<product_id>')
def remove_from_cart(product_id):
    """Remove a product from the cart."""
    cart.remove_from_cart(product_id)
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/clear')
def clear_cart():
    """Clear all items from the cart."""
    cart.clear_cart()
    flash('Your cart has been cleared.', 'info')
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/checkout')
def checkout():
    """Process the checkout for all items in the cart."""
    # Get cart items
    cart_items = cart.get_cart_items()
    
    if not cart_items:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('cart.view_cart'))
    
    # Get total price in cents
    total_price = int(cart.get_cart_total() * 100)  # Convert dollars to cents
    
    # Create product description for Stripe
    product_names = [item['name'] for item in cart_items]
    product_description = "Purchase: " + ", ".join(product_names)
    
    # Create checkout session
    try:
        # Create success and cancel URLs
        success_url = url_for('payment_success', _external=True)
        cancel_url = url_for('cart.view_cart', _external=True)
        
        # Create a custom checkout session for multiple products
        checkout_session = create_stripe_checkout_session(
            product_name="IELTS GenAI Prep Products",
            description=product_description,
            price=total_price,
            success_url=success_url,
            cancel_url=cancel_url
        )
        
        # Store cart details in session for use in payment_success
        session['checkout'] = {
            'product_ids': cart.get_product_ids(),
            'session_id': checkout_session['session_id'],
            'processed': False
        }
        
        # Redirect to Stripe checkout
        return redirect(checkout_session['checkout_url'])
        
    except Exception as e:
        flash(f'An error occurred during checkout: {str(e)}', 'danger')
        return redirect(url_for('cart.view_cart'))