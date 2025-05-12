"""
Stripe Webhook Handler
This module provides webhook handling for Stripe payment events.

Webhooks ensure that payment processing continues reliably even if the user
closes their browser after completing the checkout process.
"""

import os
import stripe
import stripe.error  # Import Stripe error classes explicitly
import logging
import json
import time
import threading
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from tenacity import retry, stop_after_attempt, wait_fixed, wait_exponential

from api_issues import log_api_error
from app import db
from models import User, PaymentRecord
from payment_services import verify_stripe_payment
from account_activation import send_verification_email_to_user

# Account activation helper function
def activate_user_account(user):
    """
    Activate a user account after successful payment and send verification email.
    
    Args:
        user (User): The user to activate
    """
    user_updated = False
    
    if not user.is_active:
        user.is_active = True
        user_updated = True
        logger.info(f"Account activated for user {user.id}")
    
    # Send verification email if email is not verified
    if not user.is_email_verified():
        # Save activation change first if needed
        if user_updated:
            db.session.commit()
            
        # Send verification email
        result = send_verification_email_to_user(user.id)
        if result:
            logger.info(f"Verification email sent to user {user.id}")
        else:
            logger.warning(f"Failed to send verification email to user {user.id}")
    elif user_updated:
        # Only commit if we updated the user but didn't send an email
        db.session.commit()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the blueprint
stripe_webhook_bp = Blueprint('stripe_webhook', __name__)

# Get Stripe API key
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', '')

# Webhook signing secret - this needs to be set in the environment
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', '')


@stripe_webhook_bp.route('/webhooks/stripe', methods=['POST'])
def handle_stripe_webhook():
    """
    Handle Stripe webhook events.
    
    This endpoint receives webhook events from Stripe and processes them accordingly.
    It verifies the webhook signature to ensure it's coming from Stripe.
    """
    # Validate request method
    if request.method != 'POST':
        return jsonify(success=False, error="Invalid request method"), 405
    
    # Get the payload and signature header
    payload = request.data
    if not payload:
        logger.error("Empty webhook payload received")
        return jsonify(success=False, error="Empty payload"), 400
        
    sig_header = request.headers.get('Stripe-Signature')
    event_id = request.headers.get('Stripe-Event-Id')
    
    logger.info(f"Received webhook from Stripe: {event_id or 'unknown event ID'}")
    
    try:
        # Validate Stripe API key is set
        if not stripe.api_key:
            logger.error("Stripe API key not set")
            return jsonify(success=False, error="Stripe API key not configured"), 500
        
        # Construct the event with proper signature verification
        if not STRIPE_WEBHOOK_SECRET:
            # For development without webhook signature verification
            # This should never happen in production
            logger.critical(
                "STRIPE_WEBHOOK_SECRET not set. Processing webhook without signature verification. "
                "This is a serious security risk in production environments."
            )
            # Parse the payload as JSON
            try:
                event = json.loads(payload)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON payload: {str(e)}")
                return jsonify(success=False, error="Invalid JSON payload"), 400
        else:
            # For production with webhook signature verification
            if not sig_header:
                logger.error("Missing Stripe-Signature header")
                return jsonify(success=False, error="Missing Stripe-Signature header"), 400
                
            try:
                event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
            except Exception as e:
                logger.error(f"Invalid signature: {str(e)}")
                return jsonify(success=False, error="Invalid signature"), 401
            
        # Validate the event structure
        if not isinstance(event, dict) or 'type' not in event or 'data' not in event:
            logger.error("Invalid event structure")
            return jsonify(success=False, error="Invalid event structure"), 400
            
        # Handle the event based on type
        event_type = event.get('type')
        event_object = event.get('data', {}).get('object')
        
        if not event_object:
            logger.error("Event data object is missing")
            return jsonify(success=False, error="Event data object is missing"), 400
        
        # Process different event types
        if event_type == 'checkout.session.completed':
            handle_checkout_session_completed(event_object)
        elif event_type == 'payment_intent.succeeded':
            handle_payment_intent_succeeded(event_object)
        elif event_type == 'charge.succeeded':
            handle_charge_succeeded(event_object)
        elif event_type == 'invoice.payment_succeeded':
            # Handle subscription renewal payments
            handle_invoice_payment_succeeded(event_object)
        else:
            logger.info(f"Unhandled event type: {event_type}")
        
        # Return success response
        return jsonify(success=True, event_type=event_type)
    
    except Exception as e:
        logger.error(f"Error processing Stripe webhook: {str(e)}")
        log_api_error('stripe', '/webhooks/stripe', e, request_obj=request)
        return jsonify(success=False, error=str(e)), 500


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def handle_checkout_session_completed(session):
    """
    Handle a successful checkout session completion.
    
    Args:
        session (object): The Stripe session object
    """
    try:
        # Validate the session object
        if session is None:
            logger.error("Session object is None")
            return
            
        # Get session ID with validation
        session_id = None
        if hasattr(session, 'id'):
            session_id = session.id
        elif isinstance(session, dict) and 'id' in session:
            session_id = session['id']
            
        if not session_id or not isinstance(session_id, str):
            logger.error("Invalid session ID: not a string or not found")
            return
            
        logger.info(f"Processing checkout session completion: {session_id}")
        
        # Get the metadata from the session using safe access
        metadata = {}
        if hasattr(session, 'metadata') and session.metadata:
            # Stripe session metadata can be accessed via dictionary-like or attribute access
            if isinstance(session.metadata, dict):
                metadata = session.metadata
            else:
                # Build metadata dictionary from attributes
                for key in dir(session.metadata):
                    if not key.startswith('_') and not callable(getattr(session.metadata, key)):
                        metadata[key] = getattr(session.metadata, key)
        elif isinstance(session, dict) and 'metadata' in session and session['metadata']:
            metadata = session['metadata']
        
        # Validate required metadata
        required_fields = ['plan']
        for field in required_fields:
            if field not in metadata:
                logger.warning(f"Missing required metadata field: {field} in session {session_id}")
                # Continue processing even if metadata is incomplete
        
        # Get customer email using safe access for different object types
        customer_email = None
        if hasattr(session, 'customer_email'):
            customer_email = session.customer_email
        elif hasattr(session, 'customer_details') and hasattr(session.customer_details, 'email'):
            customer_email = session.customer_details.email
        elif isinstance(session, dict):
            if 'customer_email' in session:
                customer_email = session['customer_email']
            elif 'customer_details' in session and 'email' in session['customer_details']:
                customer_email = session['customer_details']['email']
            
        if not customer_email or not isinstance(customer_email, str):
            logger.error(f"No valid customer email found in session {session_id}")
            return
        
        # Verify the payment with Stripe
        payment_verified = verify_stripe_payment(session_id)
        
        if not payment_verified:
            logger.error(f"Payment verification failed for session {session_id}")
            return
        
        # Find the user by customer email
        user = User.query.filter_by(email=customer_email).first()
        
        if not user:
            logger.warning(f"User not found for email {customer_email} from session {session_id}")
            return
        
        # Create a payment record
        payment_amount = 0
        if hasattr(session, 'amount_total') and session.amount_total is not None:
            payment_amount = session.amount_total / 100  # Convert from cents to dollars
        elif isinstance(session, dict) and 'amount_total' in session and session['amount_total'] is not None:
            payment_amount = session['amount_total'] / 100
            
        plan_name = metadata.get('plan', 'Unknown Plan')
        
        # Extract customer address information
        address_data = {}
        
        # Try to get shipping address first
        shipping_address = None
        if hasattr(session, 'shipping') and hasattr(session.shipping, 'address'):
            shipping_address = session.shipping.address
        elif isinstance(session, dict) and 'shipping' in session and 'address' in session['shipping']:
            shipping_address = session['shipping']['address']
            
        # If no shipping address, try customer details
        if shipping_address is None:
            if hasattr(session, 'customer_details') and hasattr(session.customer_details, 'address'):
                shipping_address = session.customer_details.address
            elif isinstance(session, dict) and 'customer_details' in session and 'address' in session['customer_details']:
                shipping_address = session['customer_details']['address']
                
        # Extract address fields
        if shipping_address:
            if hasattr(shipping_address, 'line1'):
                address_data['line1'] = shipping_address.line1
            elif isinstance(shipping_address, dict) and 'line1' in shipping_address:
                address_data['line1'] = shipping_address['line1']
                
            if hasattr(shipping_address, 'line2'):
                address_data['line2'] = shipping_address.line2
            elif isinstance(shipping_address, dict) and 'line2' in shipping_address:
                address_data['line2'] = shipping_address['line2']
                
            if hasattr(shipping_address, 'city'):
                address_data['city'] = shipping_address.city
            elif isinstance(shipping_address, dict) and 'city' in shipping_address:
                address_data['city'] = shipping_address['city']
                
            if hasattr(shipping_address, 'state'):
                address_data['state'] = shipping_address.state
            elif isinstance(shipping_address, dict) and 'state' in shipping_address:
                address_data['state'] = shipping_address['state']
                
            if hasattr(shipping_address, 'postal_code'):
                address_data['postal_code'] = shipping_address.postal_code
            elif isinstance(shipping_address, dict) and 'postal_code' in shipping_address:
                address_data['postal_code'] = shipping_address['postal_code']
                
            if hasattr(shipping_address, 'country'):
                address_data['country'] = shipping_address.country
            elif isinstance(shipping_address, dict) and 'country' in shipping_address:
                address_data['country'] = shipping_address['country']
        
        logger.info(f"Customer address collected for user {user.id} - country: {address_data.get('country', 'Unknown')}")
        
        # Create payment record with address data
        create_payment_record(user.id, payment_amount, plan_name, session_id, address_data)
        
        # Activate the user account if needed - this will send verification email
        # We're using a slight delay to ensure database transactions are complete
        # before sending emails
        def delayed_activation():
            time.sleep(2)  # 2-second delay
            activate_user_account(user)
            logger.info(f"Delayed account activation completed for user {user.id}")
            
        # Start a thread for delayed activation
        activation_thread = threading.Thread(target=delayed_activation)
        activation_thread.daemon = True
        activation_thread.start()
        
        # Handle specific plan types
        plan_type = metadata.get('type')
        
        if plan_type == 'speaking_only':
            # Handle speaking assessment purchases
            handle_speaking_payment(user, metadata)
        elif plan_type == 'subscription':
            # Handle subscription purchases
            handle_subscription_payment(user, metadata)
        else:
            # Handle individual test purchases
            handle_test_purchase(user, metadata)
        
        logger.info(f"Successfully processed payment for user {user.id} with session {session_id}")
        
    except Exception as e:
        logger.error(f"Error handling checkout session completion: {str(e)}")
        log_api_error('stripe', 'handle_checkout_session_completed', e)
        raise


def handle_payment_intent_succeeded(payment_intent):
    """
    Handle a successful payment intent.
    
    Args:
        payment_intent (dict): The Stripe payment intent object
    """
    logger.info(f"Processing payment intent: {payment_intent.id}")
    # This is a redundant check, as checkout.session.completed is the primary handler
    # But we implement it as a backup for certain payment flows


def handle_charge_succeeded(charge):
    """
    Handle a successful charge.
    
    Args:
        charge (dict): The Stripe charge object
    """
    logger.info(f"Processing charge: {charge.id}")
    # This is a redundant check, as checkout.session.completed is the primary handler
    # But we implement it as a backup for certain payment flows
    
    # Get customer email from charge (if available)
    customer_email = None
    
    # For direct charges, the receipt_email field contains the customer's email
    if hasattr(charge, 'receipt_email'):
        customer_email = charge.receipt_email
    
    # If we have a customer ID but no email, try to get the email from the customer object
    elif hasattr(charge, 'customer') and charge.customer:
        try:
            customer = stripe.Customer.retrieve(charge.customer)
            if hasattr(customer, 'email'):
                customer_email = customer.email
        except Exception as e:
            logger.error(f"Error retrieving customer for charge {charge.id}: {str(e)}")
    
    if not customer_email:
        logger.warning(f"No customer email found for charge {charge.id}")
        return
        
    # Find the user by email and process payment if found
    user = User.query.filter_by(email=customer_email).first()
    if user:
        logger.info(f"Found user {user.id} for charge {charge.id}")
        # Activate account if needed
        activate_user_account(user)
    else:
        logger.warning(f"No user found for email {customer_email} from charge {charge.id}")
        
def handle_invoice_payment_succeeded(invoice):
    """
    Handle a successful invoice payment (for subscription renewals).
    
    Args:
        invoice (dict): The Stripe invoice object
    """
    logger.info(f"Processing invoice payment: {invoice.id}")
    
    # Get customer information
    customer_id = getattr(invoice, 'customer', None)
    if not customer_id:
        logger.error(f"No customer found in invoice {invoice.id}")
        return
        
    try:
        # Retrieve customer to get email
        customer = stripe.Customer.retrieve(customer_id)
        customer_email = getattr(customer, 'email', None)
        
        if not customer_email:
            logger.error(f"No email found for customer {customer_id}")
            return
            
        # Find the user by email
        user = User.query.filter_by(email=customer_email).first()
        
        if not user:
            logger.warning(f"No user found for email {customer_email} from invoice {invoice.id}")
            return
            
        # Get subscription info from invoice
        subscription_id = getattr(invoice, 'subscription', None)
        if subscription_id:
            try:
                subscription = stripe.Subscription.retrieve(subscription_id)
                # Check if this is a recurring payment for an existing subscription
                if hasattr(subscription, 'metadata') and subscription.metadata:
                    metadata = subscription.metadata
                    # Process the subscription renewal using the same logic as initial subscriptions
                    handle_subscription_payment(user, metadata)
                    logger.info(f"Processed subscription renewal for user {user.id}")
            except Exception as e:
                logger.error(f"Error retrieving subscription for invoice {invoice.id}: {str(e)}")
                
        # Ensure account is active
        activate_user_account(user)
        
    except Exception as e:
        logger.error(f"Error processing invoice payment: {str(e)}")
        log_api_error('stripe', 'handle_invoice_payment_succeeded', e)


def create_payment_record(user_id, amount, package_name, session_id=None, address_data=None):
    """
    Create a payment record in the database.
    
    Args:
        user_id (int): User ID
        amount (float): Payment amount
        package_name (str): Name of the purchased package
        session_id (str, optional): Stripe session ID
        address_data (dict, optional): Customer address information
        
    Returns:
        PaymentRecord: The created payment record
    """
    try:
        # Create a new payment record
        payment_record = PaymentRecord()
        payment_record.user_id = user_id
        payment_record.amount = amount
        payment_record.package_name = package_name
        payment_record.payment_date = datetime.utcnow()
        payment_record.stripe_session_id = session_id
        
        # Add address information if provided
        if address_data:
            payment_record.address_line1 = address_data.get('line1')
            payment_record.address_line2 = address_data.get('line2')
            payment_record.address_city = address_data.get('city')
            payment_record.address_state = address_data.get('state')
            payment_record.address_postal_code = address_data.get('postal_code')
            payment_record.address_country = address_data.get('country')
        payment_record.is_successful = True
        payment_record.transaction_details = f"Stripe payment: {session_id}"
        
        # Add to database and commit
        db.session.add(payment_record)
        db.session.commit()
        
        logger.info(f"Created payment record for user {user_id}: {payment_record.id}")
        
        return payment_record
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating payment record: {str(e)}")
        log_api_error('database', 'create_payment_record', e)
        raise


def handle_speaking_payment(user, metadata):
    """
    Handle speaking assessment payment activation.
    
    Args:
        user (User): The user object
        metadata (dict): Stripe session metadata
    """
    logger.info(f"Processing speaking payment for user {user.id}")
    
    # Get the speaking package type from metadata
    package_type = metadata.get('package')
    if not package_type:
        logger.error(f"No package type found in metadata for user {user.id}")
        return
    
    try:
        # Import assessment functions
        from add_assessment_routes import handle_assessment_product_payment, assessment_products
        
        # Map speaking_only package types to assessment product IDs
        product_map = {
            'basic': 'speaking_only_basic',
            'pro': 'speaking_only_pro'
        }
        
        product_id = product_map.get(package_type)
        if not product_id:
            logger.error(f"Invalid speaking package type: {package_type}")
            return
            
        # Handle the payment using the existing function
        success = handle_assessment_product_payment(user, product_id)
        
        if success:
            # Assign assessment sets
            from add_assessment_routes import assign_assessment_sets
            assign_assessment_sets(user, product_id)
            logger.info(f"Successfully processed speaking payment for user {user.id}")
        else:
            logger.error(f"Failed to process speaking payment for user {user.id}")
            
    except Exception as e:
        logger.error(f"Error handling speaking payment: {str(e)}")
        log_api_error('stripe', 'handle_speaking_payment', e)
    
    
def handle_subscription_payment(user, metadata):
    """
    Handle subscription payment activation.
    
    Args:
        user (User): The user object
        metadata (dict): Stripe session metadata
    """
    logger.info(f"Processing subscription payment for user {user.id}")
    
    plan_code = metadata.get('plan')
    if not plan_code:
        logger.error(f"No plan code found in metadata for user {user.id}")
        return
        
    try:
        # Add subscription to user's record
        if not user.subscriptions:
            user.subscriptions = []
            
        # Create a new subscription record
        new_subscription = {
            'plan': plan_code,
            'start_date': datetime.utcnow().isoformat(),
            'days': int(metadata.get('days', 30)),
            'active': True
        }
        
        user.subscriptions.append(new_subscription)
        db.session.commit()
        
        logger.info(f"Added subscription {plan_code} for user {user.id}")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error handling subscription payment: {str(e)}")
        log_api_error('stripe', 'handle_subscription_payment', e)


def handle_test_purchase(user, metadata):
    """
    Handle individual test purchase activation.
    
    Args:
        user (User): The user object
        metadata (dict): Stripe session metadata
    """
    logger.info(f"Processing test purchase for user {user.id}")
    
    # Get product details from metadata
    product_type = metadata.get('type')
    product_id = None
    
    # Determine the product ID based on metadata
    if product_type in ['academic', 'general']:
        test_package = metadata.get('package')
        if test_package:
            # For academic/general writing and speaking products
            product_id = f"{product_type}_{metadata.get('package', '')}"
    else:
        # For other assessment products that already have a complete product ID
        product_id = metadata.get('product_id')
    
    if not product_id:
        logger.error(f"No product ID determined from metadata for user {user.id}")
        return
        
    try:
        # Import assessment functions
        from add_assessment_routes import handle_assessment_product_payment, assign_assessment_sets
        
        # Handle the payment using the existing function
        success = handle_assessment_product_payment(user, product_id)
        
        if success:
            # Assign assessment sets
            assign_assessment_sets(user, product_id)
            logger.info(f"Successfully processed test purchase for user {user.id}, product {product_id}")
        else:
            logger.error(f"Failed to process test purchase for user {user.id}, product {product_id}")
            
    except Exception as e:
        logger.error(f"Error handling test purchase: {str(e)}")
        log_api_error('stripe', 'handle_test_purchase', e)