import os
import stripe
import logging
from tenacity import retry, stop_after_attempt, wait_fixed
from datetime import datetime, timedelta

# Set Stripe API key
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', '')

# Prices for the subscription plans
PLAN_PRICES = {
    'monthly': 999,  # $9.99 in cents
    'annual': 8999   # $89.99 in cents
}

# Product names
PLAN_NAMES = {
    'monthly': 'IELTS AI Prep Monthly Subscription',
    'annual': 'IELTS AI Prep Annual Subscription'
}

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def create_stripe_checkout(plan='monthly'):
    """
    Create a Stripe checkout session for subscription.
    
    Args:
        plan (str): Subscription plan ('monthly' or 'annual')
    
    Returns:
        str: Checkout URL
    """
    try:
        if not stripe.api_key:
            logging.error("Stripe API key not found. Cannot create checkout session.")
            raise ValueError("Stripe API key is required")
        
        if plan not in PLAN_PRICES:
            plan = 'monthly'  # Default to monthly if invalid plan
        
        # Get domain for success and cancel URLs
        domain = os.environ.get('REPLIT_DEV_DOMAIN') 
        if not domain and os.environ.get('REPLIT_DEPLOYMENT'):
            domain = os.environ.get('REPLIT_DOMAINS', '').split(',')[0]
        if not domain:
            domain = 'localhost:5000'
        
        # Create a Product if it doesn't exist
        product = create_or_get_product(plan)
        
        # Create a Price if it doesn't exist
        price = create_or_get_price(product.id, plan)
        
        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price': price.id,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=f'https://{domain}/payment-success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'https://{domain}/payment-cancel',
            metadata={
                'plan': plan
            }
        )
        
        return checkout_session.url
        
    except Exception as e:
        logging.error(f"Error creating Stripe checkout: {str(e)}")
        raise

def create_or_get_product(plan):
    """
    Create a Stripe product if it doesn't exist, or get the existing one.
    
    Args:
        plan (str): Subscription plan ('monthly' or 'annual')
        
    Returns:
        stripe.Product: The Stripe product
    """
    try:
        # List products with the given name
        products = stripe.Product.list(
            active=True,
            limit=1
        )
        
        for product in products.data:
            if product.name == PLAN_NAMES[plan]:
                return product
        
        # If no product found, create one
        return stripe.Product.create(
            name=PLAN_NAMES[plan],
            description=f"IELTS test preparation subscription - {plan} plan"
        )
    except Exception as e:
        logging.error(f"Error creating/getting Stripe product: {str(e)}")
        raise

def create_or_get_price(product_id, plan):
    """
    Create a Stripe price if it doesn't exist, or get the existing one.
    
    Args:
        product_id (str): The Stripe product ID
        plan (str): Subscription plan ('monthly' or 'annual')
        
    Returns:
        stripe.Price: The Stripe price
    """
    try:
        # List prices for the given product
        prices = stripe.Price.list(
            product=product_id,
            active=True,
            limit=100
        )
        
        # Find a price with the correct amount
        amount = PLAN_PRICES[plan]
        recurring_interval = 'month' if plan == 'monthly' else 'year'
        
        for price in prices.data:
            if (price.unit_amount == amount and 
                price.recurring.interval == recurring_interval):
                return price
        
        # If no price found, create one
        return stripe.Price.create(
            product=product_id,
            unit_amount=amount,
            currency='usd',
            recurring={
                'interval': recurring_interval,
            },
            metadata={
                'plan': plan
            }
        )
    except Exception as e:
        logging.error(f"Error creating/getting Stripe price: {str(e)}")
        raise

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def verify_payment(session_id):
    """
    Verify a completed payment session.
    
    Args:
        session_id (str): Stripe checkout session ID
    
    Returns:
        dict: Payment information or None if verification fails
    """
    try:
        if not stripe.api_key:
            logging.error("Stripe API key not found. Cannot verify payment.")
            raise ValueError("Stripe API key is required")
        
        # Retrieve the session
        session = stripe.checkout.Session.retrieve(session_id)
        
        # Check payment status
        if session.payment_status == 'paid':
            return {
                'paid': True,
                'plan': session.metadata.get('plan', 'monthly'),
                'customer': session.customer
            }
        else:
            return None
            
    except Exception as e:
        logging.error(f"Error verifying payment: {str(e)}")
        return None

# Additional payment methods could be implemented here for regional options
