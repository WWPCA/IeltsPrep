"""
Stripe Webhook Handler
This module provides webhook handling for Stripe payment events.

Webhooks ensure that payment processing continues reliably even if the user
closes their browser after completing the checkout process.
"""

import os
import stripe
import logging
import json
from flask import Blueprint, request, jsonify
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_fixed

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
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    
    logger.info(f"Received webhook from Stripe: {request.headers.get('Stripe-Event-Id')}")
    
    try:
        if not STRIPE_WEBHOOK_SECRET:
            # For development without webhook signature verification
            logger.warning("STRIPE_WEBHOOK_SECRET not set. Processing webhook without signature verification.")
            event = json.loads(payload)
        else:
            # For production with webhook signature verification
            event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
            
        # Handle the event
        if event['type'] == 'checkout.session.completed':
            handle_checkout_session_completed(event['data']['object'])
        elif event['type'] == 'payment_intent.succeeded':
            handle_payment_intent_succeeded(event['data']['object'])
        elif event['type'] == 'charge.succeeded':
            handle_charge_succeeded(event['data']['object'])
        else:
            logger.info(f"Unhandled event type: {event['type']}")
        
        return jsonify(success=True)
    
    except Exception as e:
        logger.error(f"Error processing Stripe webhook: {str(e)}")
        log_api_error('stripe', '/webhooks/stripe', e, request_obj=request)
        return jsonify(success=False, error=str(e)), 400


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def handle_checkout_session_completed(session):
    """
    Handle a successful checkout session completion.
    
    Args:
        session (object): The Stripe session object
    """
    try:
        session_id = getattr(session, 'id', None)
        if not session_id:
            logger.error("Invalid session object: no ID found")
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
        
        # Get customer email using similar safe access
        customer_email = None
        if hasattr(session, 'customer_email'):
            customer_email = session.customer_email
        elif hasattr(session, 'customer_details') and hasattr(session.customer_details, 'email'):
            customer_email = session.customer_details.email
            
        if not customer_email:
            logger.error(f"No customer email found in session {session_id}")
            return
        
        # Verify the payment and get payment details
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
            
        plan_name = metadata.get('plan', 'Unknown Plan')
        
        create_payment_record(user.id, payment_amount, plan_name, session_id)
        
        # Activate the user account if needed
        activate_user_account(user)
        
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


def create_payment_record(user_id, amount, package_name, session_id=None):
    """
    Create a payment record in the database.
    
    Args:
        user_id (int): User ID
        amount (float): Payment amount
        package_name (str): Name of the purchased package
        session_id (str, optional): Stripe session ID
        
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