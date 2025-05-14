"""
DEPRECATED: Update subscription routes to handle our new product types.

This file should no longer be actively used as we've moved to cart-based checkout.
The implementation was functional but has been superceded by cart_routes.py.
Kept for historical reference.

NOTE: This file has been replaced by update_assessment_package_routes.py for terminology consistency.
DO NOT USE THIS FILE FOR NEW DEVELOPMENT.
"""

from main import app
from models import db, User, CompletePracticeTest
from routes import subscribe
from payment_services import create_stripe_checkout_session
from datetime import datetime, timedelta
from flask import flash, redirect, url_for, render_template, request, jsonify, session
from flask_login import current_user
import os
import json

def update_subscription_routes():
    """Update the routes to handle our new product types."""
    
    # Define the new product types
    products = {
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
    
    # Update the checkout route for the new product types
    def updated_checkout():
        """Handle checkout for the new product types."""
        # Get product ID from URL parameters
        product_id = request.args.get('plan')
        
        if not product_id or product_id not in products:
            flash('Invalid product selected.', 'danger')
            return redirect(url_for('subscribe'))
        
        # Get product details
        product = products[product_id]
        
        # Create success and cancel URLs
        success_url = url_for('payment_success', _external=True)
        cancel_url = url_for('subscribe', _external=True)
        
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
            return redirect(url_for('subscribe'))
    
    # Update the payment success route for the new product types
    def updated_payment_success():
        """Handle successful payment for the new product types."""
        # Get session ID from URL param
        session_id = request.args.get('session_id')
        
        # Check if we have checkout data
        if not session_id or 'checkout' not in session:
            flash('No payment information found.', 'warning')
            return redirect(url_for('subscribe'))
        
        # Get checkout data
        checkout_data = session['checkout']
        product_id = checkout_data.get('product_id')
        
        # Check if payment has already been processed
        if checkout_data.get('processed', False):
            flash('Your payment has already been processed.', 'info')
            return redirect(url_for('dashboard'))
        
        # Verify payment with Stripe
        try:
            from payment_services import verify_stripe_payment
            payment_verified = verify_stripe_payment(session_id)
            
            if not payment_verified:
                flash('Payment verification failed. Please contact support.', 'danger')
                return redirect(url_for('subscribe'))
            
            # Add product to user's account
            if current_user.is_authenticated:
                # Get user's test history
                test_history = current_user.test_history if current_user.test_history else []
                
                # Add the product to user's test history
                purchase = {
                    'date': datetime.utcnow().isoformat(),
                    'product_id': product_id,
                    'product': products[product_id]['name'],
                    'amount': products[product_id]['price'],
                    'sets_assigned': False
                }
                
                test_history.append(purchase)
                current_user.test_history = test_history
                
                # Set the user's new product type
                current_user.subscription_status = 'active'
                current_user.product_type = product_id
                
                # No expiry date for permanent access
                current_user.subscription_expiry = None
                
                # Commit changes
                db.session.commit()
                
                # Assign assessment sets
                assign_assessment_sets(current_user, product_id)
                
                flash(f'Thank you for your purchase! Your {products[product_id]["name"]} is now active.', 'success')
                
                # Mark payment as processed
                checkout_data['processed'] = True
                session['checkout'] = checkout_data
                
                # Redirect based on product type
                if product_id.endswith('_writing'):
                    return redirect(url_for('practice_test_list', test_type='writing'))
                elif product_id.endswith('_speaking'):
                    return redirect(url_for('practice_test_list', test_type='speaking'))
                else:
                    return redirect(url_for('dashboard'))
                
            else:
                # User not logged in - should not happen
                flash('You must be logged in to complete your purchase.', 'warning')
                return redirect(url_for('login'))
                
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
            return redirect(url_for('subscribe'))
    
    # Add the updated routes
    app.add_url_rule('/checkout', 'checkout', updated_checkout, methods=['GET'])
    app.add_url_rule('/payment-success', 'payment_success', updated_payment_success, methods=['GET'])
    
    print("Subscription routes updated for new product types")

def assign_assessment_sets(user, product_id):
    """Assign assessment sets to the user for the given product."""
    # Get all available sets for this product type
    with app.app_context():
        sets = CompletePracticeTest.query.filter_by(
            test_type=product_id,
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

if __name__ == "__main__":
    update_subscription_routes()