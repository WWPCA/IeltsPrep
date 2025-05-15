"""
Integrate assessment routes directly into the main application.
This script directly adds assessment routes to the Flask app.
"""

from main import app
from flask import render_template, request, redirect, url_for, flash, session
from flask_login import current_user
from models import db, User, Assessment
from datetime import datetime
import json
from payment_services import create_stripe_checkout_session
from geoip_services import get_country_from_ip
from routes import get_pricing_for_country
from country_restrictions import country_access_required, is_country_restricted

# Define the assessment products with pricing
assessment_products = {
    'academic_writing': {
        'name': 'Academic Writing Assessment',
        'description': 'Complete Academic Writing assessment with Task 1 and Task 2',
        'price': 25,
    },
    'academic_speaking': {
        'name': 'Academic Speaking Assessment',
        'description': 'Complete Academic Speaking assessment with all three parts',
        'price': 25,
    },
    'general_writing': {
        'name': 'General Training Writing Assessment',
        'description': 'Complete General Training Writing assessment with Task 1 and Task 2',
        'price': 25,
    },
    'general_speaking': {
        'name': 'General Training Speaking Assessment',
        'description': 'Complete General Training Speaking assessment with all three parts',
        'price': 25,
    }
}

# Add assessment routes directly to the app
@app.route('/assessment-products')
@country_access_required
def assessment_products_page():
    """Display available assessment products."""
    # Detect country for pricing
    if current_user.is_authenticated and hasattr(current_user, 'region') and current_user.region:
        country_code = current_user.region[:2].upper()  # Use the first two characters of region
    else:
        # Get country from IP address
        client_ip = request.remote_addr
        country_code, country_name = get_country_from_ip(client_ip)
    
    # Get pricing based on country
    pricing = get_pricing_for_country(country_code)
    
    # Get user's test preference for product selection
    test_preference = "academic"  # Default
    if current_user.is_authenticated and hasattr(current_user, 'test_preference'):
        test_preference = current_user.test_preference
    
    # Get Stripe Buy Button IDs for each product
    from stripe_buy_buttons import get_button_id
    import os
    
    academic_writing_button_id = get_button_id('academic', 'writing')
    academic_speaking_button_id = get_button_id('academic', 'speaking')
    general_writing_button_id = get_button_id('general', 'writing')
    general_speaking_button_id = get_button_id('general', 'speaking')
    
    # Get Stripe publishable key
    stripe_publishable_key = os.environ.get('STRIPE_PUBLISHABLE_KEY', '')
    
    return render_template('assessment_products.html', 
                          title='IELTS Assessment Products', 
                          pricing=pricing,
                          test_preference=test_preference,
                          country_code=country_code,
                          academic_writing_button_id=academic_writing_button_id,
                          academic_speaking_button_id=academic_speaking_button_id,
                          general_writing_button_id=general_writing_button_id,
                          general_speaking_button_id=general_speaking_button_id,
                          stripe_publishable_key=stripe_publishable_key)

@app.route('/product-checkout')
@country_access_required
def product_checkout():
    """Handle checkout for assessment products."""
    # Get product ID from URL parameters
    product_id = request.args.get('product')
    
    if not product_id or product_id not in assessment_products:
        flash('Invalid product selected.', 'danger')
        return redirect(url_for('assessment_products_page'))
    
    # Get product details
    product = assessment_products[product_id]
    
    # Create success and cancel URLs
    success_url = url_for('payment_success', _external=True)
    cancel_url = url_for('assessment_products_page', _external=True)
    
    try:
        # Create Stripe checkout session
        checkout_session = create_stripe_checkout_session(
            product_name=product['name'],
            description=product['description'],
            price=product['price'],
            success_url=success_url,
            cancel_url=cancel_url
        )
        
        # Store product details in session for use in payment_success
        session['checkout'] = {
            'product_id': product_id,
            'session_id': checkout_session['session_id'],
            'processed': False
        }
        
        # Redirect to Stripe checkout
        return redirect(checkout_session['checkout_url'])
        
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('assessment_products_page'))

# Add a link on the navbar to the assessment products page
@app.context_processor
def inject_assessment_link():
    return {
        'has_assessment_products': True
    }

def assign_assessment_sets(user, product_id):
    """Assign assessment sets to the user for the given product."""
    # Get all available sets for this product type
    sets = Assessment.query.filter_by(
        assessment_product_id=product_id,
        status='active'
    ).all()
    
    if not sets or len(sets) == 0:
        print(f"No assessment sets found for product {product_id}")
        return
    
    print(f"Found {len(sets)} assessment sets for product {product_id}")
    
    # Get user's test history
    test_history = user.test_history if user.test_history else []
    
    # Find the most recent purchase
    purchase = None
    for item in reversed(test_history):
        if item.get('product_id') == product_id and not item.get('sets_assigned', False):
            purchase = item
            break
    
    if not purchase:
        print(f"No unassigned purchase found for product {product_id}")
        return
    
    # Assign up to 4 sets
    set_ids = []
    for i, test_set in enumerate(sets[:4]):
        set_ids.append(test_set.id)
    
    # Update purchase with assigned sets
    purchase['assigned_sets'] = set_ids
    purchase['sets_assigned'] = True
    
    # Update user's test history
    for i, item in enumerate(test_history):
        if item.get('date') == purchase.get('date') and item.get('product_id') == product_id:
            test_history[i] = purchase
            break
    
    user.test_history = test_history
    
    # Commit changes
    db.session.commit()
    
    print(f"Assigned {len(set_ids)} assessment sets to user {user.id} for product {product_id}")

def handle_assessment_product_payment(user, product_id):
    """Handle the payment success for an assessment product."""
    # Get product details
    if product_id not in assessment_products:
        print(f"Invalid product ID: {product_id}")
        return False
    
    product = assessment_products[product_id]
    
    # Add the product to user's test history
    test_history = user.test_history if user.test_history else []
    
    # Add the product to user's test history
    purchase = {
        'date': datetime.utcnow().isoformat(),
        'product_id': product_id,
        'product': product['name'],
        'amount': product['price'],
        'sets_assigned': False
    }
    
    test_history.append(purchase)
    user.test_history = test_history
    
    # Commit changes
    db.session.commit()
    
    # Assign assessment sets
    assign_assessment_sets(user, product_id)
    
    print(f"Added {product['name']} to user {user.id}'s account")
    return True

# We'll call this when handling payment success
def is_assessment_product(product_id):
    """Check if the given product ID is an assessment product."""
    return product_id in assessment_products

# Update the payment_success route to handle assessment products
def modify_payment_success_route():
    """Add assessment product handling to the payment_success route."""
    from routes import payment_success
    
    original_payment_success = payment_success
    
    @app.route('/payment-success')
    def new_payment_success():
        """Handle payment success, including assessment products."""
        # Check if this is an assessment product payment
        if 'checkout' in session and session['checkout'].get('product_id'):
            product_id = session['checkout'].get('product_id')
            
            if is_assessment_product(product_id):
                print(f"Processing assessment product payment: {product_id}")
                
                # Mark payment as processed
                session['checkout']['processed'] = True
                
                # Process assessment product
                result = handle_assessment_product_payment(current_user, product_id)
                
                if result:
                    flash(f'Thank you for your purchase! Your {assessment_products[product_id]["name"]} is now active.', 'success')
                    
                    # Redirect based on product type
                    if product_id.endswith('_writing'):
                        return redirect(url_for('practice_test_list', test_type='writing'))
                    elif product_id.endswith('_speaking'):
                        return redirect(url_for('practice_test_list', test_type='speaking'))
                    else:
                        return redirect(url_for('dashboard'))
        
        # If not an assessment product, use the original function
        return original_payment_success()
    
    # Replace the route with our new function
    app.view_functions['payment_success'] = new_payment_success

print("Integrating assessment routes...")
# Run the payment success route modification
try:
    modify_payment_success_route()
    print("Payment success route updated to handle assessment products.")
except Exception as e:
    print(f"Error updating payment success route: {str(e)}")
    print("Assessment products may still be available but payment handling won't work correctly.")

print("Assessment routes integrated directly into the application.")