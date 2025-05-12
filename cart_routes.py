"""
Shopping cart routes for IELTS GenAI Prep.
This module defines routes for the shopping cart functionality.
"""

from flask import Blueprint, redirect, url_for, render_template, flash, session, request, jsonify
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

import cart
import stripe
from models import User, db
from payment_services import create_stripe_checkout_session

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/')
def view_cart():
    """Display the shopping cart page."""
    cart_items = cart.get_cart_items()
    cart_total = cart.get_cart_total()
    
    # Get any checkout error from session and remove it
    checkout_error = session.pop('checkout_error', None)
    
    return render_template(
        'cart.html', 
        title='Shopping Cart',
        cart_items=cart_items,
        cart_total=cart_total,
        checkout_error=checkout_error
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

@cart_bp.route('/debug-checkout/<session_id>')
def debug_checkout(session_id):
    """Show debug information for a checkout session."""
    try:
        # Retrieve the session from Stripe to get the latest info
        from payment_services import get_stripe_api_key
        stripe.api_key = get_stripe_api_key()
        
        stripe_session = stripe.checkout.Session.retrieve(session_id)
        
        # Render the debug template with all session details
        return render_template('stripe_debug.html',
                              checkout_url=stripe_session.url,
                              session_id=session_id,
                              created_at=datetime.fromtimestamp(stripe_session.created).strftime('%Y-%m-%d %H:%M:%S'),
                              amount=stripe_session.amount_total)
    except Exception as e:
        flash(f"Error retrieving checkout session: {str(e)}", "danger")
        return redirect(url_for('cart.view_cart'))

@cart_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    """Start the checkout process by checking user status."""
    from flask_login import current_user
    
    # Get cart items first
    cart_items = cart.get_cart_items()
    
    if not cart_items:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('cart.view_cart'))
    
    # If the user is already logged in, proceed directly to payment
    if current_user.is_authenticated:
        return create_checkout_session()
    
    # If the user is not logged in, show the user status check page
    cart_total = cart.get_cart_total()
    return render_template(
        'user_status_check.html',
        title='Complete Your Purchase',
        cart_items=cart_items,
        cart_total=cart_total
    )

@cart_bp.route('/check-email', methods=['POST'])
def check_email():
    """Check if an email exists and direct user accordingly."""
    email = request.form.get('email')
    if not email:
        flash('Please provide an email address.', 'danger')
        return redirect(url_for('cart.checkout'))
    
    try:
        # Check if the email already exists - only query the needed columns
        existing_user = db.session.query(User.id).filter_by(email=email).first()
        
        if existing_user:
            # User exists, direct to login
            flash('An account with this email already exists. Please log in to continue.', 'info')
            session['pending_checkout'] = True
            return redirect(url_for('login', next='checkout'))
        else:
            # New user, direct to registration with email pre-filled
            session['pending_checkout'] = True
            session['registration_email'] = email
            return redirect(url_for('register', next='checkout'))
    except Exception as e:
        # Log the error (in a production environment)
        print(f"Error checking email: {str(e)}")
        flash('An error occurred while processing your request. Please try again.', 'danger')
        return redirect(url_for('cart.checkout'))

def create_checkout_session():
    """Create a Stripe checkout session for the current cart."""
    from flask_login import current_user
    from flask import json
    import logging

    logger = logging.getLogger(__name__)
    
    # Get cart items
    cart_items = cart.get_cart_items()
    
    if not cart_items:
        # Check if this is an AJAX request
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({'error': 'Your cart is empty.'})
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('cart.view_cart'))
    
    # Get total price in dollars from cart
    cart_total = cart.get_cart_total()
    
    # Convert to cents for Stripe (prices are stored in dollars in the cart)
    # Ensure a consistent approach to pricing
    # Debug price calculation
    print(f"Cart total before conversion: ${cart_total}")
    
    # If cart_total is extremely high (e.g. 50.00 treated as 5000 cents, which becomes $5000),
    # it might be a unit conversion issue. Force a more reasonable value.
    if cart_total >= 100:  # If over $100, likely an error
        print(f"WARNING: Cart total suspiciously high: ${cart_total}. Check if cents vs dollars issue.")
        
    # Convert to cents for Stripe (prices are stored in dollars in the cart)
    total_price = int(cart_total * 100)  # Convert dollars to cents
    
    # Debug log to verify correct amount
    print(f"Cart total: ${cart_total} -> Stripe amount: {total_price} cents (${cart_total:.2f})")
    
    # Create product description for Stripe
    product_names = [item['name'] for item in cart_items]
    product_description = "Purchase: " + ", ".join(product_names)
    
    # Create checkout session
    try:
        # Create success and cancel URLs
        success_url = url_for('payment_success', _external=True)
        cancel_url = url_for('cart.view_cart', _external=True)
        
        # Get user details if available
        customer_email = None
        if hasattr(current_user, 'email') and current_user.email:
            customer_email = current_user.email
            
        # Always get the country code from GeoIP to enforce restrictions
        from geoip_services import get_country_from_ip
        country_code, _ = get_country_from_ip()
        
        # Create a custom checkout session for multiple products
        checkout_session = create_stripe_checkout_session(
            product_name="IELTS GenAI Prep Products",
            description=product_description,
            price=total_price,
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=customer_email,
            country_code=country_code
        )
        
        # The checkout_session could be either a dictionary with session_id and checkout_url
        # or a direct Stripe Session object depending on the implementation
        
        # Check if it's a dictionary
        if isinstance(checkout_session, dict):
            session_id = checkout_session.get('session_id', '')
            checkout_url = checkout_session.get('checkout_url', '')
        else:
            # It's a Stripe Session object
            session_id = getattr(checkout_session, 'id', '')
            checkout_url = getattr(checkout_session, 'url', '')
        
        # Store cart details in session for use in payment_success
        session['checkout'] = {
            'product_ids': cart.get_product_ids(),
            'session_id': session_id,
            'processed': False
        }
        
        # Handle different response types based on request
        is_ajax = request.headers.get('Content-Type') == 'application/json'
        
        # Make sure checkout_url is valid
        if not checkout_url:
            # Handle error - couldn't create checkout session properly
            flash('Error creating checkout session. Please try again.', 'danger')
            return redirect(url_for('cart.view_cart')) if not is_ajax else jsonify({'error': 'Failed to create checkout session'})
        
        if is_ajax:
            # For AJAX requests
            return jsonify({
                'checkout_url': checkout_url,
                'session_id': session_id
            })
        else:
            # Use our debugging template that worked previously
            return render_template('stripe_debug.html', 
                                  checkout_url=checkout_url,
                                  session_id=session_id,
                                  created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                  amount=int(cart.get_cart_total() * 100))
        
    except Exception as e:
        # Log the error 
        error_msg = f"Error creating checkout session: {str(e)}"
        print(error_msg)
        
        # Log the cart data for debugging
        print(f"Cart data: {json.dumps(cart_items, indent=2)}")
        print(f"Calculated total: ${cart_total} → {total_price} cents")
        
        # Check Stripe API key
        from payment_services import get_stripe_api_key
        api_key = get_stripe_api_key()
        if not api_key:
            print("ERROR: Stripe API key is empty!")
        else:
            print(f"Stripe API key found (starts with: {api_key[:4]}, length: {len(api_key)})")
        
        # Use more user-friendly error messages
        error_str = str(e).lower()
        if 'authentication' in error_str or 'unauthorized' in error_str or '401' in error_str:
            user_error = "Payment service authentication failed. Please try again later."
        elif 'connection' in error_str or 'timeout' in error_str:
            user_error = "Connection to payment service timed out. Please try again."
        else:
            user_error = "We couldn't connect to our payment service. Please try again or contact support."
        
        # Handle different response types
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({
                'error': 'Payment processing error',
                'message': user_error
            })
        
        # Store the error in session to display on cart page
        session['checkout_error'] = user_error
        flash(user_error, 'danger')
        return redirect(url_for('cart.view_cart'))