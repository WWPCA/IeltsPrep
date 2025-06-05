"""
Payment services for IELTS GenAI Prep
This module handles Stripe payment integration for assessment purchases.
"""

import os
import stripe
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set Stripe API key
stripe_api_key = os.environ.get('STRIPE_SECRET_KEY', '')
if stripe_api_key:
    stripe.api_key = stripe_api_key
    logger.info("Stripe API key configured successfully")
else:
    logger.warning("STRIPE_SECRET_KEY not found in environment variables")

def create_stripe_checkout_session(product_name, description, price, success_url, cancel_url, country_code=None, customer_email=None):
    """
    Create a Stripe checkout session for IELTS assessment purchases.
    
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
    """
    try:
        # Convert price to cents for Stripe
        price_cents = int(price * 100)
        
        # Create checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': product_name,
                        'description': description,
                    },
                    'unit_amount': price_cents,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=customer_email,
            payment_intent_data={
                'description': f'IELTS Assessment: {product_name}',
            },
            metadata={
                'product_type': 'ielts_assessment',
                'product_name': product_name
            }
        )
        
        return {
            'session_id': session.id,
            'checkout_url': session.url
        }
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating checkout session: {e}")
        raise Exception(f"Payment system error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error creating checkout session: {e}")
        raise Exception(f"Payment processing error: {e}")

def create_stripe_checkout_speaking(product_name, description, price, success_url, cancel_url, customer_email=None):
    """Create Stripe checkout session specifically for speaking assessments"""
    return create_stripe_checkout_session(
        product_name=product_name,
        description=description,
        price=price,
        success_url=success_url,
        cancel_url=cancel_url,
        customer_email=customer_email
    )

def verify_stripe_payment(session_id):
    """
    Verify a Stripe payment session and return payment details.
    
    Args:
        session_id (str): Stripe checkout session ID
        
    Returns:
        dict: Payment verification details
    """
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session.payment_status == 'paid':
            return {
                'verified': True,
                'amount': session.amount_total / 100,  # Convert from cents
                'currency': session.currency,
                'customer_email': session.customer_details.email if session.customer_details else None,
                'payment_intent_id': session.payment_intent,
                'metadata': session.metadata
            }
        else:
            return {
                'verified': False,
                'status': session.payment_status
            }
            
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error verifying payment: {e}")
        return {'verified': False, 'error': str(e)}
    except Exception as e:
        logger.error(f"Unexpected error verifying payment: {e}")
        return {'verified': False, 'error': str(e)}

def create_payment_record(user_id, amount, currency, stripe_session_id, product_name, metadata=None):
    """
    Create a payment record in the database.
    
    Args:
        user_id (int): User ID
        amount (float): Payment amount
        currency (str): Payment currency
        stripe_session_id (str): Stripe session ID
        product_name (str): Name of the purchased product
        metadata (dict, optional): Additional metadata
        
    Returns:
        bool: True if record created successfully
    """
    try:
        from app import db
        from models import PaymentRecord
        
        payment_record = PaymentRecord(
            user_id=user_id,
            amount=amount,
            currency=currency,
            stripe_session_id=stripe_session_id,
            product_name=product_name,
            status='completed',
            created_at=datetime.utcnow(),
            metadata=json.dumps(metadata) if metadata else None
        )
        
        db.session.add(payment_record)
        db.session.commit()
        
        logger.info(f"Payment record created for user {user_id}: {product_name}")
        return True
        
    except Exception as e:
        logger.error(f"Error creating payment record: {e}")
        if 'db' in locals():
            db.session.rollback()
        return False

def get_product_price(product_id):
    """Get the price for a specific product"""
    prices = {
        'academic_speaking': 15.00,
        'general_speaking': 15.00,
        'academic_writing': 12.00,
        'general_writing': 12.00
    }
    return prices.get(product_id, 15.00)

def get_product_details(product_id):
    """Get detailed information about a product"""
    products = {
        'academic_speaking': {
            'name': 'Academic Speaking Assessment',
            'description': 'IELTS Academic Speaking practice with AI examiner Maya',
            'price': 15.00
        },
        'general_speaking': {
            'name': 'General Training Speaking Assessment',
            'description': 'IELTS General Training Speaking practice with AI examiner Maya',
            'price': 15.00
        },
        'academic_writing': {
            'name': 'Academic Writing Assessment',
            'description': 'IELTS Academic Writing evaluation with detailed feedback',
            'price': 12.00
        },
        'general_writing': {
            'name': 'General Training Writing Assessment',
            'description': 'IELTS General Training Writing evaluation with detailed feedback',
            'price': 12.00
        }
    }
    return products.get(product_id, products['academic_speaking'])