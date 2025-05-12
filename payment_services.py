"""
Payment services for IELTS GenAI Prep
This module handles Stripe payment integration for test purchases.
"""

import os
import stripe
import logging
import json
from datetime import datetime
from country_restrictions import is_country_restricted, get_allowed_countries

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set Stripe API key - ensure it's loaded for all Stripe operations
stripe_api_key = os.environ.get('STRIPE_SECRET_KEY', '')
if stripe_api_key:
    stripe.api_key = stripe_api_key
    logger.info("Stripe API key configured successfully")
else:
    logger.warning("STRIPE_SECRET_KEY not found in environment variables")

def get_stripe_api_key():
    """Get the Stripe API key from environment variables and set it globally."""
    api_key = os.environ.get('STRIPE_SECRET_KEY', '')
    if api_key:
        # Set the API key globally for all stripe calls
        stripe.api_key = api_key
    return api_key

def create_stripe_checkout_session(product_name, description, price, success_url, cancel_url, country_code=None, customer_email=None):
    """
    Create a Stripe checkout session for IELTS test purchases.
    
    Args:
        product_name (str): Name of the product
        description (str): Description of the product
        price (float): Price in USD (will be converted to cents for Stripe)
        success_url (str): URL to redirect to on successful payment
        cancel_url (str): URL to redirect to if payment is canceled
        country_code (str, optional): Two-letter country code for regional payment methods
        customer_email (str, optional): Pre-fill customer email if available
        
    Returns:
        dict: Contains session_id and checkout_url
        
    Raises:
        ValueError: If the country is restricted by our policy or other error
    """
    try:
        # Check country restrictions
        if country_code and is_country_restricted(country_code):
            logger.error(f"Payment attempt from restricted country: {country_code}")
            raise ValueError("Due to regulatory requirements, we cannot process payments from your country at this time.")
        
        # Ensure Stripe API key is set
        if not get_stripe_api_key():
            logger.error("Stripe API key not found or invalid")
            raise ValueError("Could not connect to our payment service. Please try again later.")
        
        # Convert price to cents for Stripe
        # Handle both formats: 50.00 (dollars) or 5000 (cents)
        if price > 1000 and price % 100 == 0:
            # Already in cents (e.g., 5000)
            price_in_cents = price
            logger.info(f"Using price as cents: {price_in_cents} (${price/100:.2f})")
        else:
            # Convert from dollars to cents
            price_in_cents = int(price * 100)
            logger.info(f"Converting dollars to cents: ${price:.2f} → {price_in_cents} cents")
        
        # Ensure price is in a reasonable range
        if price_in_cents < 100 or price_in_cents > 50000:
            logger.error(f"Price out of reasonable range: {price_in_cents} cents")
            raise ValueError(f"Price out of reasonable range: ${price_in_cents/100:.2f}")
        
        # Set metadata for tracking
        metadata = {
            'product_name': product_name,
            'price': str(price),
            'description': description,
            'source': 'ielts_genai_prep',
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Ensure success_url includes session ID
        if '{CHECKOUT_SESSION_ID}' not in success_url:
            success_url += ('&' if '?' in success_url else '?') + 'session_id={CHECKOUT_SESSION_ID}'
        
        # Create Stripe checkout session
        session_params = {
            'payment_method_types': ['card'],
            'line_items': [
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': product_name,
                            'description': description,
                        },
                        'unit_amount': price_in_cents,
                        'tax_behavior': 'exclusive',
                    },
                    'quantity': 1,
                },
            ],
            'mode': 'payment',
            'success_url': success_url,
            'cancel_url': cancel_url,
            'metadata': metadata,
            'automatic_tax': {'enabled': False},
            'customer_creation': 'always',
            'billing_address_collection': 'required',
            'payment_intent_data': {
                'setup_future_usage': 'off_session',
                'capture_method': 'automatic',
            },
        }
        
        # Add customer email if provided
        if customer_email:
            session_params['customer_email'] = customer_email
        
        # Log session parameters (redacting sensitive info)
        debug_params = session_params.copy()
        if 'customer_email' in debug_params:
            debug_params['customer_email'] = '***@***.com'
        logger.debug(f"Stripe checkout params: {json.dumps(debug_params, indent=2)}")
        
        # Create checkout session
        checkout_session = stripe.checkout.Session.create(**session_params)
        logger.info(f"Stripe session created successfully: {checkout_session.id}")
        
        return {
            'session_id': checkout_session.id,
            'checkout_url': checkout_session.url
        }
    
    except Exception as e:
        logger.error(f"Stripe API Error: {type(e).__name__} - {str(e)}")
        if isinstance(e, ValueError):
            raise  # Re-raise ValueError exceptions (like country restrictions)
        raise ValueError("Could not connect to our payment service. Please try again later.")

def create_payment_record(user_id, amount, package_name, session_id=None):
    """
    Create a payment record in the database.
    
    Args:
        user_id (int): User ID
        amount (float): Payment amount in dollars
        package_name (str): Name of the purchased package
        session_id (str, optional): Stripe session ID
        
    Returns:
        PaymentRecord: The created payment record
    """
    from models import PaymentRecord, db
    
    try:
        # Convert amount to cents if needed
        if amount < 100:  # Likely in dollars (e.g., 50.00 instead of 5000)
            amount_in_cents = int(amount * 100)
        else:
            amount_in_cents = int(amount)  # Already in cents
            
        logger.info(f"Creating payment record: ${amount_in_cents/100:.2f} for {package_name}")
        
        # Create the payment record
        payment = PaymentRecord()
        payment.user_id = user_id
        payment.amount = amount_in_cents  # Store in cents for consistency
        payment.payment_date = datetime.utcnow()
        payment.package_name = package_name
        payment.is_successful = False  # Will be updated when payment is verified
        
        if session_id:
            payment.stripe_session_id = session_id
            
        # Add to database
        db.session.add(payment)
        db.session.commit()
        return payment
        
    except Exception as e:
        logger.error(f"Error creating payment record: {str(e)}")
        db.session.rollback()
        return None

def create_stripe_checkout_speaking(package_type, country_code=None, customer_email=None):
    """
    DEPRECATED: This function is no longer actively used as we've moved to cart-based checkout.
    Kept for backward compatibility with existing code.
    
    Create a Stripe checkout session for speaking assessments.
    
    Args:
        package_type (str): Package type ('basic' or 'pro')
        country_code (str, optional): Two-letter country code
        customer_email (str, optional): Customer email
    
    Returns:
        dict: Contains session_id and checkout_url
    """
    # Map package types to product details
    package_details = {
        'basic': {
            'name': 'Academic Speaking Assessment',
            'description': '4 academic speaking assessments (one-time use)',
            'price': 25.00  # $25.00
        },
        'pro': {
            'name': 'General Training Speaking Assessment',
            'description': '4 general training speaking assessments (one-time use)',
            'price': 25.00  # $25.00
        }
    }
    
    # Get package details or use default
    details = package_details.get(package_type, package_details['basic'])
    
    # Create success and cancel URLs
    from flask import url_for
    success_url = url_for('payment_success', _external=True)
    cancel_url = url_for('cart.view_cart', _external=True)
    
    # Create checkout session
    return create_stripe_checkout_session(
        product_name=details['name'],
        description=details['description'],
        price=details['price'],
        success_url=success_url,
        cancel_url=cancel_url,
        country_code=country_code,
        customer_email=customer_email
    )

def verify_stripe_payment(session_id):
    """
    Verify a Stripe payment session.
    
    Args:
        session_id (str): Stripe session ID
        
    Returns:
        dict: Payment details if verified, None otherwise
    """
    try:
        if not session_id:
            logger.error("No session_id provided for payment verification")
            return None
            
        # Ensure Stripe API key is set
        if not get_stripe_api_key():
            logger.error("Stripe API key not configured")
            return None
            
        # Retrieve the session from Stripe
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        
        # Check if the payment was successful
        if checkout_session.payment_status == 'paid':
            # Update payment record in the database
            from models import PaymentRecord, db
            
            payment = PaymentRecord.query.filter_by(stripe_session_id=session_id).first()
            if payment:
                payment.is_successful = True
                payment.transaction_details = f"Stripe payment: {session_id}"
                db.session.commit()
                
            # Return payment details
            return {
                'session_id': checkout_session.id,
                'amount': checkout_session.amount_total,
                'currency': checkout_session.currency,
                'payment_status': checkout_session.payment_status,
                'customer_email': checkout_session.customer_details.email if hasattr(checkout_session, 'customer_details') else None,
                'customer_name': checkout_session.customer_details.name if hasattr(checkout_session, 'customer_details') else None,
                'metadata': checkout_session.metadata
            }
        else:
            logger.warning(f"Payment not completed: {checkout_session.payment_status}")
            return None
            
    except Exception as e:
        logger.error(f"Error verifying Stripe payment: {str(e)}")
        return None