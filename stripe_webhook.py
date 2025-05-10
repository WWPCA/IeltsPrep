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
# Account activation helper function
def activate_user_account(user):
    """
    Activate a user account after successful payment.
    
    Args:
        user (User): The user to activate
    """
    if not user.is_active:
        user.is_active = True
        db.session.commit()
        logger.info(f"Account activated for user {user.id}")

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
        session (dict): The Stripe session object
    """
    try:
        logger.info(f"Processing checkout session completion: {session.id}")
        
        # Get the metadata from the session
        metadata = session.get('metadata', {})
        customer_email = session.get('customer_email')
        
        # Verify the payment and get payment details
        payment_verified = verify_stripe_payment(session.id)
        
        if not payment_verified:
            logger.error(f"Payment verification failed for session {session.id}")
            return
        
        # Find the user by customer email
        user = User.query.filter_by(email=customer_email).first()
        
        if not user:
            logger.warning(f"User not found for email {customer_email} from session {session.id}")
            return
        
        # Create a payment record
        payment_amount = session.get('amount_total', 0) / 100  # Convert from cents to dollars
        plan_name = metadata.get('plan', 'Unknown Plan')
        
        create_payment_record(user.id, payment_amount, plan_name, session.id)
        
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
        
        logger.info(f"Successfully processed payment for user {user.id} with session {session.id}")
        
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
        payment_record = PaymentRecord(
            user_id=user_id,
            amount=amount,
            package_name=package_name,
            payment_date=datetime.utcnow(),
            stripe_session_id=session_id,
            status='completed'
        )
        
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
    # This should call the function that assigns speaking assessments to the user
    # Details would be based on your specific implementation
    
    
def handle_subscription_payment(user, metadata):
    """
    Handle subscription payment activation.
    
    Args:
        user (User): The user object
        metadata (dict): Stripe session metadata
    """
    logger.info(f"Processing subscription payment for user {user.id}")
    # This should call the function that activates user subscription
    # Details would be based on your specific implementation
    

def handle_test_purchase(user, metadata):
    """
    Handle individual test purchase activation.
    
    Args:
        user (User): The user object
        metadata (dict): Stripe session metadata
    """
    logger.info(f"Processing test purchase for user {user.id}")
    # This should call the function that assigns purchased tests to the user
    # Details would be based on your specific implementation