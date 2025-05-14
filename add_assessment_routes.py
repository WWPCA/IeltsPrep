"""
Add assessment product routes to the application.
This script adds routes for the new assessment products.
"""
from main import app
from flask import render_template, request, redirect, url_for, flash, session
from flask_login import current_user
from models import db, User
from datetime import datetime, timedelta
import json
import os
from geoip_services import get_country_from_ip
from routes import get_pricing_for_country
from stripe_buy_buttons import get_button_id

# Define the assessment products with pricing (speaking-only packages removed)
assessment_products = {
    'academic_writing': {
        'name': 'Academic Writing Assessment',
        'description': 'Complete Academic Writing assessment with Task 1 and Task 2',
        'price': 25,  # Price in dollars
    },
    'academic_speaking': {
        'name': 'Academic Speaking Assessment',
        'description': 'Complete Academic Speaking assessment with all three parts',
        'price': 25,  # Price in dollars
    },
    'general_writing': {
        'name': 'General Training Writing Assessment',
        'description': 'Complete General Training Writing assessment with Task 1 and Task 2',
        'price': 25,  # Price in dollars
    },
    'general_speaking': {
        'name': 'General Training Speaking Assessment',
        'description': 'Complete General Training Speaking assessment with all three parts',
        'price': 25,  # Price in dollars
    }
}

def add_assessment_routes():
    """Add routes for assessment products."""
    
    @app.route('/assessment-products')
    def assessment_products_page():
        """Display available assessment products."""
        # Detect country for pricing
        if current_user.is_authenticated and current_user.region:
            country_code = current_user.region[:2].upper()  # Use the first two characters of region
        else:
            # Get country from IP address
            client_ip = request.remote_addr
            country_code, country_name = get_country_from_ip(client_ip)
        
        # Get pricing based on country
        pricing = get_pricing_for_country(country_code)
        
        # Get user's test preference for product selection
        test_preference = "academic"  # Default
        if current_user.is_authenticated:
            test_preference = current_user.test_preference
        
        # Get Stripe Buy Button IDs for each product
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
            from payment_services import create_stripe_checkout_session
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
    
    print("Assessment routes added successfully.")

def assign_assessment_sets(user, product_id):
    """Assign assessment package to the user for the given product."""
    # Get user's test history
    test_history = user.test_history if hasattr(user, 'test_history') and user.test_history else []
    
    # Find the most recent purchase
    purchase = None
    for item in reversed(test_history):
        if item.get('product_id') == product_id and not item.get('assigned', False):
            purchase = item
            break
    
    if not purchase:
        print(f"No unassigned purchase found for product {product_id}")
        return
    
    # Mark the assessment as assigned
    purchase['assigned'] = True
    
    # Set the assessment package status based on product_id
    assessment_type_mapping = {
        'academic_writing': 'Academic Writing',
        'academic_speaking': 'Academic Speaking', 
        'general_writing': 'General Writing',
        'general_speaking': 'General Speaking'
    }
    
    # Determine base assessment type (academic or general)
    base_assessment_type = 'academic' if product_id.startswith('academic_') else 'general'
    
    # Number of assessments to assign (using standard package size of 4)
    num_assessments = 4
    
    # Use the new assessment_assignment_service to assign assessments
    try:
        import assessment_assignment_service
        assigned_ids, success = assessment_assignment_service.assign_assessments_to_user(
            user_id=user.id,
            assessment_type=base_assessment_type,
            num_assessments=num_assessments,
            access_days=30
        )
        
        if success:
            print(f"Successfully assigned {len(assigned_ids)} assessments to user {user.id}")
            purchase['assigned_assessment_ids'] = assigned_ids
        else:
            print(f"Failed to assign assessments to user {user.id}: not enough unique assessments available")
    except Exception as e:
        print(f"Error assigning assessments to user {user.id}: {str(e)}")
    
    if product_id in assessment_type_mapping:
        user.assessment_package_status = assessment_type_mapping[product_id]
        # Set expiry date to 30 days from now
        user.assessment_package_expiry = datetime.utcnow() + timedelta(days=30)
        
    # Update user's test history
    for i, item in enumerate(test_history):
        if item.get('date') == purchase.get('date') and item.get('product_id') == product_id:
            test_history[i] = purchase
            break
    
    user.test_history = test_history
    
    # Commit changes
    db.session.commit()
    
    print(f"Assigned assessment package {product_id} to user {user.id}")

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

if __name__ == '__main__':
    add_assessment_routes()