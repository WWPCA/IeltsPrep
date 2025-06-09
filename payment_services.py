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

# Set Stripe API key - prefer test keys for development
stripe_test_key = os.environ.get('STRIPE_TEST_SECRET_KEY', '')
stripe_live_key = os.environ.get('STRIPE_SECRET_KEY', '')

if stripe_test_key:
    stripe.api_key = stripe_test_key
    logger.info("Stripe TEST API key configured successfully")
elif stripe_live_key:
    stripe.api_key = stripe_live_key
    logger.info("Stripe LIVE API key configured successfully")
else:
    logger.warning("No Stripe API keys found in environment variables")

def create_stripe_checkout_session(product_name, description, price, success_url, cancel_url, country_code=None, customer_email=None):
    """
    Create a Stripe checkout session for IELTS assessment purchases.
    Following Stripe API best practices from https://docs.stripe.com/api
    
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
        # Convert price to cents for Stripe (API requirement)
        price_cents = int(price * 100)
        
        # Generate idempotency key for payment safety
        import uuid
        idempotency_key = str(uuid.uuid4())
        
        # Map assessment types to Stripe product IDs
        # TEST ENVIRONMENT PRODUCTS:
        test_products = {
            'academic_writing': 'prod_SRyPROj1OcR9c4',
            'general_writing': 'prod_SRyO0g7X6gCQXn', 
            'academic_speaking': 'prod_SRyObveHwhj61F',
            'general_speaking': 'prod_SRyNGeTny9yhob'
        }
        
        # PRODUCTION ENVIRONMENT PRODUCTS (for future deployment):
        # 'academic_writing': 'prod_SRFpXW9UbuxpIK',
        # 'general_writing': 'prod_SRFqAHrX1gAjOO', 
        # 'academic_speaking': 'prod_SRFsfHFnzTki3N',
        # 'general_speaking': 'prod_SRFt035asxEgTK'
        
        # Get the appropriate product ID for current environment
        product_id = None
        for key, pid in test_products.items():
            if key in product_name.lower().replace(' ', '_').replace('-', '_'):
                product_id = pid
                break
        
        if not product_id:
            # Security: Only allow payments for pre-configured, authorized products
            logger.error(f"Unauthorized product payment attempt: {product_name}")
            raise Exception("Product not authorized for purchase. Please contact support.")
        
        # Use only pre-configured authorized products
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product': product_id,
                    'unit_amount': 2500,  # $25.00
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=customer_email if customer_email else None,
            # Collect billing address for tax compliance
            billing_address_collection='required',
            # Enable automatic tax calculation
            automatic_tax={'enabled': True},
            payment_intent_data={
                'description': f'IELTS Assessment: {product_name}',
                'metadata': {
                    'integration_type': 'checkout',
                    'platform': 'ielts_genai_prep'
                }
            },
            metadata={
                'product_type': 'ielts_assessment',
                'product_name': product_name,
                'platform': 'ielts_genai_prep',
                'created_at': datetime.utcnow().isoformat()
            },
            expires_at=int((datetime.utcnow().timestamp() + 1800))  # 30 minutes expiry
        )
        
        return {
            'session_id': session.id,
            'checkout_url': session.url
        }
        
    except stripe.error.CardError as e:
        # Card was declined
        logger.error(f"Card declined: {e}")
        raise Exception(f"Card declined: {e.user_message}")
    except stripe.error.RateLimitError as e:
        # Too many requests made to the API too quickly
        logger.error(f"Rate limit error: {e}")
        raise Exception("Too many payment requests. Please try again in a moment.")
    except stripe.error.InvalidRequestError as e:
        # Invalid parameters were supplied to Stripe's API
        logger.error(f"Invalid request: {e}")
        raise Exception("Invalid payment request. Please contact support.")
    except stripe.error.AuthenticationError as e:
        # Authentication with Stripe's API failed
        logger.error(f"Authentication failed: {e}")
        raise Exception("Payment system authentication error. Please contact support.")
    except stripe.error.APIConnectionError as e:
        # Network communication with Stripe failed
        logger.error(f"Network error: {e}")
        raise Exception("Payment system temporarily unavailable. Please try again.")
    except stripe.error.StripeError as e:
        # Generic Stripe error
        logger.error(f"Stripe error: {e}")
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