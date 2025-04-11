import os
import stripe
import logging
from tenacity import retry, stop_after_attempt, wait_fixed
from datetime import datetime, timedelta

# Set Stripe API key
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', '')

# Subscription plans details
SUBSCRIPTION_PLANS = {
    'base': {
        'name': 'IELTS AI Prep Base - 3 Tests',
        'price': 1000,  # $10.00 in cents
        'tests': 3,
        'days': 30,
        'description': 'Access to 3 tests for 30 days'
    },
    'intermediate': {
        'name': 'IELTS AI Prep Intermediate - 6 Tests',
        'price': 1500,  # $15.00 in cents
        'tests': 6,
        'days': 30,
        'description': 'Access to 6 tests for 30 days'
    },
    'pro': {
        'name': 'IELTS AI Prep Pro - 12 Tests',
        'price': 2000,  # $20.00 in cents
        'tests': 12,
        'days': 30,
        'description': 'Access to 12 tests for 30 days'
    }
}

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def create_stripe_checkout(plan='base', country_code=None):
    """
    Create a Stripe checkout session for subscription.
    
    Args:
        plan (str): Subscription plan ('base', 'intermediate', or 'pro')
        country_code (str, optional): Two-letter country code for regional payment methods
    
    Returns:
        dict: Contains session_id and checkout_url
    """
    try:
        if not stripe.api_key:
            logging.error("Stripe API key not found. Cannot create checkout session.")
            raise ValueError("Stripe API key is required")
        
        if plan not in SUBSCRIPTION_PLANS:
            plan = 'base'  # Default to base if invalid plan
        
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
        
        # Use the country code if provided
        user_country = country_code
        # Dynamic payment method types based on user region
        payment_method_types = ['card', 'apple_pay', 'google_pay']
        
        # Add region-specific payment methods
        # These are the payment methods supported by Stripe
        region_payment_mapping = {
            # East Asia
            'CN': ['alipay', 'wechat_pay'],
            'JP': ['konbini', 'paypay', 'jcb'],
            'KR': ['kakaopay', 'naver_pay'],
            
            # Southeast Asia
            'MY': ['grabpay', 'fpx', 'boost', 'touch_n_go'],
            'TH': ['promptpay', 'truemoney'],
            'ID': ['dana', 'ovo', 'gopay', 'linkaja'],
            'PH': ['gcash', 'paymaya'],
            'SG': ['grabpay', 'paynow'],
            'VN': ['momo', 'zalopay', 'vnpay'],
            
            # South Asia
            'IN': ['upi', 'paytm', 'netbanking', 'amazon_pay', 'phonepe'],
            'PK': ['easypaisa', 'jazzcash'],
            'BD': ['bkash', 'rocket', 'nagad'],
            'NP': ['esewa', 'khalti'],
            
            # Latin America
            'BR': ['boleto', 'pix', 'mercado_pago'],
            'MX': ['oxxo', 'spei', 'mercado_pago'],
            
            # Middle East
            'AE': ['benefit', 'apple_pay'],
            'SA': ['stcpay', 'mada'],
            'EG': ['fawry', 'meeza'],
            'TR': ['troy', 'papara', 'ininal'],
            
            # Africa
            'KE': ['mpesa', 'airtel_money'],
            'NG': ['paystack', 'flutterwave', 'opay'],
            'ET': ['cbe_birr', 'telebirr'],
            'TZ': ['mpesa', 'tigopesa', 'airtel_money'],
            
            # Oceania
            'AU': ['afterpay', 'bpay', 'osko'],
            'NZ': ['afterpay', 'poli'],
            
            # North America
            'CA': ['interac'],
            'US': ['affirm', 'us_bank_account', 'venmo'],
            
            # Europe
            'GB': ['bacs_debit', 'ideal', 'sofort'],
            'RU': ['yandex_pay', 'qiwi', 'sberbank']
        }
        
        # If we have user_country, add the appropriate payment methods
        if user_country and user_country in region_payment_mapping:
            payment_method_types.extend(region_payment_mapping[user_country])
        
        # Create checkout session with all payment options
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=payment_method_types,
            line_items=[
                {
                    'price': price.id,
                    'quantity': 1,
                },
            ],
            mode='payment',  # Using one-time payment instead of subscription
            success_url=f'https://{domain}/payment-success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'https://{domain}/payment-cancel',
            payment_method_options={
                'card': {
                    'wallet': {
                        'applePay': 'auto',
                        'googlePay': 'auto',
                    }
                }
            },
            metadata={
                'plan': plan,
                'tests': str(SUBSCRIPTION_PLANS[plan]['tests']),
                'days': str(SUBSCRIPTION_PLANS[plan]['days'])
            }
        )
        
        return {
            'session_id': checkout_session.id,
            'checkout_url': checkout_session.url
        }
        
    except Exception as e:
        logging.error(f"Error creating Stripe checkout: {str(e)}")
        raise

def create_or_get_product(plan):
    """
    Create a Stripe product if it doesn't exist, or get the existing one.
    
    Args:
        plan (str): Subscription plan ('base', 'intermediate', or 'pro')
        
    Returns:
        stripe.Product: The Stripe product
    """
    try:
        plan_details = SUBSCRIPTION_PLANS[plan]
        
        # List products with the given name
        products = stripe.Product.list(
            active=True,
            limit=10
        )
        
        for product in products.data:
            if product.name == plan_details['name']:
                return product
        
        # If no product found, create one
        return stripe.Product.create(
            name=plan_details['name'],
            description=plan_details['description']
        )
    except Exception as e:
        logging.error(f"Error creating/getting Stripe product: {str(e)}")
        raise

def create_or_get_price(product_id, plan):
    """
    Create a Stripe price if it doesn't exist, or get the existing one.
    
    Args:
        product_id (str): The Stripe product ID
        plan (str): Subscription plan ('base', 'intermediate', or 'pro')
        
    Returns:
        stripe.Price: The Stripe price
    """
    try:
        plan_details = SUBSCRIPTION_PLANS[plan]
        
        # List prices for the given product
        prices = stripe.Price.list(
            product=product_id,
            active=True,
            limit=10
        )
        
        # Find a price with the correct amount
        amount = plan_details['price']
        
        for price in prices.data:
            if price.unit_amount == amount:
                return price
        
        # If no price found, create one
        return stripe.Price.create(
            product=product_id,
            unit_amount=amount,
            currency='usd',
            metadata={
                'plan': plan,
                'tests': str(plan_details['tests']),
                'days': str(plan_details['days'])
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
            plan = session.metadata.get('plan', 'base')
            tests = int(session.metadata.get('tests', SUBSCRIPTION_PLANS[plan]['tests']))
            days = int(session.metadata.get('days', SUBSCRIPTION_PLANS[plan]['days']))
            
            return {
                'paid': True,
                'plan': plan,
                'tests': tests,
                'days': days,
                'customer': session.customer
            }
        else:
            return None
            
    except Exception as e:
        logging.error(f"Error verifying payment: {str(e)}")
        return None

# Additional payment methods could be implemented here for regional options
