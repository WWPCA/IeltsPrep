from flask import render_template, request, redirect, url_for, flash, session
from flask_login import current_user
from models import db, User
from datetime import datetime, timedelta
import json
import os
from geoip_services import get_country_from_ip
from stripe_buy_buttons import get_button_id
from flask import Flask, render_template, request, redirect, url_for, flash, session, current_app, jsonify

"""
Add assessment product routes to the application.
This script adds routes for the new assessment products.
"""

# Simple country code to name mapping for supported countries
country_name_map = {
    'US': 'United States',
    'CA': 'Canada',
    'IN': 'India',
    'NP': 'Nepal',
    'KW': 'Kuwait',
    'QA': 'Qatar'
}

# Define the assessment products with pricing (speaking-only packages removed)
assessment_products = {
    'academic_writing': {
        'name': 'Academic Writing',
        'description': 'Complete Academic Writing assessment with Task 1 and Task 2',
        'price': 25,  # Price in dollars
    },
    'academic_speaking': {
        'name': 'Academic Speaking',
        'description': 'Complete Academic Speaking assessment with all three parts',
        'price': 25,  # Price in dollars
    },
    'general_writing': {
        'name': 'General Writing',
        'description': 'Complete General Writing assessment with Task 1 and Task 2',
        'price': 25,  # Price in dollars
    },
    'general_speaking': {
        'name': 'General Speaking',
        'description': 'Complete General Speaking assessment with all three parts',
        'price': 25,  # Price in dollars
    }
}

def add_assessment_routes(app=None):
    """Add routes for assessment products."""
    if app is None:
        # For backward compatibility when called directly
        from flask import current_app
        app = current_app
    
    @app.route('/assessment-products')
    def assessment_products_page():
        """Display available assessment products."""
        # Detect country for region display only
        country_code = None
        country_name = None
        
        if current_user.is_authenticated and current_user.region:
            country_code = current_user.region[:2].upper()  # Use the first two characters of region
            # Get country name from code
            country_name = country_name_map.get(country_code, "United States")
        else:
            # Get country from IP address
            client_ip = request.remote_addr
            country_code, country_name = get_country_from_ip(client_ip)
        
        # Default values if detection fails
        if not country_code:
            country_code = 'US'
        if not country_name:
            country_name = 'United States'
        
        # Fixed pricing for all regions
        pricing = {
            'country_code': country_code,
            'country_name': country_name,
            'price': 25  # Fixed price of $25 for all assessment products
        }
        
        # Get user's assessment preference for product selection
        assessment_preference = "academic"  # Default
        if current_user.is_authenticated:
            assessment_preference = current_user.assessment_preference
        
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
                              assessment_preference=assessment_preference,
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
    # Get user's assessment history
    assessment_history = user.assessment_history if hasattr(user, 'assessment_history') else []
    
    # Find the most recent purchase
    purchase = None
    for item in reversed(assessment_history):
        if item.get('product_id') == product_id and not item.get('assigned', False):
            purchase = item
            break
    
    if not purchase:
        print(f"No unassigned purchase found for product {product_id}")
        return
    
    # Mark the assessment as assigned
    purchase['assigned'] = True
    
    # Set the assessment package status based on product_id
    # Now product names match package names exactly
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
    
    # Create UserPackage record for the new system
    from models import UserPackage
    try:
        # Check if package already exists
        existing_package = UserPackage.query.filter_by(
            user_id=user.id,
            package_name=assessment_type_mapping[product_id]
        ).first()
        
        if existing_package:
            # Add to existing package
            existing_package.add_more_packages(1)
            print(f"Added 1 more package to existing {assessment_type_mapping[product_id]} package")
        else:
            # Create new package
            new_package = UserPackage()
            new_package.user_id = user.id
            new_package.package_name = assessment_type_mapping[product_id]
            new_package.quantity_purchased = 1
            new_package.quantity_remaining = 1
            new_package.purchase_date = datetime.utcnow()
            new_package.expiry_date = datetime.utcnow() + timedelta(days=30)
            new_package.status = 'active'
            db.session.add(new_package)
            print(f"Created new UserPackage: {assessment_type_mapping[product_id]}")
        
        db.session.commit()
        success = True
        assigned_ids = []  # Will be assigned when user starts assessment
        
        if success:
            print(f"Successfully created UserPackage for {assessment_type_mapping[product_id]}")
            purchase['assigned_package'] = assessment_type_mapping[product_id]
        else:
            print(f"Failed to create UserPackage for {assessment_type_mapping[product_id]}")
    except Exception as e:
        print(f"Error creating UserPackage for user {user.id}: {str(e)}")
    
    # Also maintain legacy system for backward compatibility
    if product_id in assessment_type_mapping:
        user.assessment_package_status = assessment_type_mapping[product_id]
        # Set expiry date to 30 days from now
        user.assessment_package_expiry = datetime.utcnow() + timedelta(days=30)
        
    # Update user's assessment history
    for i, item in enumerate(assessment_history):
        if item.get('date') == purchase.get('date') and item.get('product_id') == product_id:
            assessment_history[i] = purchase
            break
    
    user.assessment_history = assessment_history
    
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
    
    # Add the product to user's assessment history
    assessment_history = user.assessment_history if hasattr(user, 'assessment_history') else []
    
    # Add the product to user's assessment history
    purchase = {
        'date': datetime.utcnow().isoformat(),
        'product_id': product_id,
        'product': product['name'],
        'amount': product['price'],
        'sets_assigned': False
    }
    
    assessment_history.append(purchase)
    user.assessment_history = assessment_history
    
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