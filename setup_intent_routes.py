"""
Setup Intent Routes for Stripe Integration
This module provides routes for handling Stripe Setup Intents for payment testing.
"""

from flask import Blueprint, render_template, redirect, url_for, request, jsonify, flash, session
from flask_login import current_user, login_required
from stripe_setup_intents import create_setup_intent, get_setup_intent, create_test_payment
import cart
import json
import logging
from datetime import datetime
from models import db, PaymentRecord, User

setup_intent_bp = Blueprint('setup_intent', __name__, url_prefix='/payment-test')

@setup_intent_bp.route('/')
@login_required
def payment_test_home():
    """Display the payment test homepage."""
    cart_items = cart.get_cart_items()
    cart_total = cart.get_cart_total()
    
    return render_template(
        'payment_test/home.html',
        title='Payment Testing',
        cart_items=cart_items,
        cart_total=cart_total
    )

@setup_intent_bp.route('/setup')
@login_required
def setup_payment():
    """Initialize payment method setup."""
    # Create a setup intent
    try:
        setup_intent_result = create_setup_intent(
            customer_email=current_user.email,
            customer_name=current_user.username
        )
        
        # Store the setup intent details in the session
        session['setup_intent'] = {
            'id': setup_intent_result['id'],
            'client_secret': setup_intent_result['client_secret'],
            'customer_id': setup_intent_result['customer_id']
        }
        
        # Get the Stripe publishable key from environment
        import os
        stripe_pk = os.environ.get('STRIPE_PUBLISHABLE_KEY', '')
        
        return render_template(
            'payment_test/setup.html',
            title='Setup Payment Method',
            client_secret=setup_intent_result['client_secret'],
            stripe_pk=stripe_pk
        )
    except Exception as e:
        flash(f'Error setting up payment method: {str(e)}', 'danger')
        return redirect(url_for('setup_intent.payment_test_home'))

@setup_intent_bp.route('/confirm', methods=['POST'])
@login_required
def confirm_setup():
    """Handle confirmation of payment method setup."""
    setup_intent_id = request.form.get('setup_intent_id')
    payment_method_id = request.form.get('payment_method_id')
    
    if not setup_intent_id or not payment_method_id:
        flash('Missing required payment information.', 'danger')
        return redirect(url_for('setup_intent.payment_test_home'))
    
    try:
        # Retrieve the setup intent to verify it succeeded
        setup_intent = get_setup_intent(setup_intent_id)
        
        if setup_intent.status != 'succeeded':
            flash(f'Payment method setup was not successful. Status: {setup_intent.status}', 'warning')
            return redirect(url_for('setup_intent.payment_test_home'))
        
        # Get customer ID from the session or the setup intent
        customer_id = session.get('setup_intent', {}).get('customer_id') or setup_intent.customer
        
        if not customer_id:
            flash('Customer information not found.', 'danger')
            return redirect(url_for('setup_intent.payment_test_home'))
        
        # Store payment method ID in session for future use
        session['payment_method'] = {
            'id': payment_method_id,
            'customer_id': customer_id
        }
        
        flash('Payment method set up successfully!', 'success')
        return redirect(url_for('setup_intent.test_payment'))
    except Exception as e:
        flash(f'Error confirming payment method: {str(e)}', 'danger')
        return redirect(url_for('setup_intent.payment_test_home'))

@setup_intent_bp.route('/test')
@login_required
def test_payment():
    """Test a payment with the stored payment method."""
    if 'payment_method' not in session:
        flash('No payment method found. Please set up a payment method first.', 'warning')
        return redirect(url_for('setup_intent.setup_payment'))
    
    cart_items = cart.get_cart_items()
    cart_total = cart.get_cart_total()
    
    return render_template(
        'payment_test/test_payment.html',
        title='Test Payment',
        cart_items=cart_items,
        cart_total=cart_total,
        payment_method=session['payment_method']
    )

@setup_intent_bp.route('/process', methods=['POST'])
@login_required
def process_test_payment():
    """Process a test payment with the stored payment method."""
    if 'payment_method' not in session:
        flash('No payment method found. Please set up a payment method first.', 'warning')
        return redirect(url_for('setup_intent.setup_payment'))
    
    try:
        # Get payment details
        customer_id = session['payment_method']['customer_id']
        payment_method_id = session['payment_method']['id']
        
        # Get cart total
        cart_total = cart.get_cart_total()
        amount_in_cents = int(cart_total * 100)
        
        # Get address information from the form
        address = {
            'line1': request.form.get('line1'),
            'line2': request.form.get('line2', ''),
            'city': request.form.get('city'),
            'state': request.form.get('state'),
            'postal_code': request.form.get('postal_code'),
            'country': request.form.get('country')
        }
        
        # Create a test payment with address for tax calculation
        payment_intent = create_test_payment(
            customer_id=customer_id,
            payment_method_id=payment_method_id,
            amount=amount_in_cents,
            address=address
        )
        
        if payment_intent.status == 'succeeded':
            # Create payment record
            payment_record = PaymentRecord()
            payment_record.user_id = current_user.id
            payment_record.amount = cart_total
            payment_record.package_name = 'Test Payment'
            payment_record.payment_date = datetime.utcnow()
            payment_record.stripe_session_id = payment_intent.id
            payment_record.is_successful = True
            
            # Store address information in payment record
            payment_record.address_line1 = address.get('line1')
            payment_record.address_line2 = address.get('line2')
            payment_record.address_city = address.get('city')
            payment_record.address_state = address.get('state')
            payment_record.address_postal_code = address.get('postal_code')
            payment_record.address_country = address.get('country')
            
            # Get tax details if available
            tax_enabled = getattr(payment_intent, 'automatic_tax', {}).get('enabled', False)
            tax_amount = getattr(payment_intent, 'tax', {}).get('amount', 0)
            
            payment_record.transaction_details = json.dumps({
                'product_ids': cart.get_product_ids(),
                'payment_intent_id': payment_intent.id,
                'payment_method': 'card',
                'currency': 'usd',
                'type': 'test_payment',
                'automatic_tax_enabled': tax_enabled,
                'tax_amount': tax_amount
            })
            db.session.add(payment_record)
            
            # Update user's payment status
            current_user.is_active = True
            db.session.commit()
            
            # Clear cart
            cart.clear_cart()
            
            # Log the success for monitoring
            logging.info(f"Test payment processed successfully with automatic tax: {tax_enabled}")
            
            flash('Test payment processed successfully!', 'success')
            return redirect(url_for('payment_success'))
        else:
            flash(f'Payment not successful. Status: {payment_intent.status}', 'warning')
            return redirect(url_for('setup_intent.test_payment'))
    except Exception as e:
        logging.error(f"Error processing test payment: {str(e)}")
        flash(f'Error processing test payment: {str(e)}', 'danger')
        return redirect(url_for('setup_intent.test_payment'))