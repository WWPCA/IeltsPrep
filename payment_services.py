import os
import stripe
import logging
from tenacity import retry, stop_after_attempt, wait_fixed
from datetime import datetime, timedelta

# Set Stripe API key
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', '')

# New purchase options following the updated pricing structure
TEST_PURCHASE_OPTIONS = {
    # Academic Test Type
    'academic': {
        'single': {
            'name': 'IELTS Academic - 1 Test',
            'price': 2500,  # $25.00 in cents
            'tests': 1,
            'days': 15,
            'description': 'Access to 1 Academic test for 15 days'
        },
        'double': {
            'name': 'IELTS Academic - 2 Tests',
            'price': 3500,  # $35.00 in cents
            'tests': 2,
            'days': 15,
            'description': 'Access to 2 Academic tests for 15 days'
        },
        'pack': {
            'name': 'IELTS Academic - 4 Tests',
            'price': 5000,  # $50.00 in cents
            'tests': 4,
            'days': 15,
            'description': 'Access to 4 Academic tests for 15 days'
        }
    },
    # General Training Test Type
    'general': {
        'single': {
            'name': 'IELTS General Training - 1 Test',
            'price': 2500,  # $25.00 in cents
            'tests': 1,
            'days': 15,
            'description': 'Access to 1 General Training test for 15 days'
        },
        'double': {
            'name': 'IELTS General Training - 2 Tests',
            'price': 3500,  # $35.00 in cents
            'tests': 2,
            'days': 15,
            'description': 'Access to 2 General Training tests for 15 days'
        },
        'pack': {
            'name': 'IELTS General Training - 4 Tests',
            'price': 5000,  # $50.00 in cents
            'tests': 4,
            'days': 15,
            'description': 'Access to 4 General Training tests for 15 days'
        }
    },
    # Speaking Only Test Options
    'speaking_only': {
        'basic': {
            'name': 'IELTS Speaking Assessments - Basic',
            'price': 1500,  # $15.00 in cents
            'assessments': 4,
            'days': 0,  # No expiry
            'description': 'Access to 4 Speaking assessments (one-time use)'
        },
        'pro': {
            'name': 'IELTS Speaking Assessments - Pro',
            'price': 2000,  # $20.00 in cents
            'assessments': 10,
            'days': 0,  # No expiry
            'description': 'Access to 10 Speaking assessments (one-time use)'
        }
    }
}

# Legacy subscription plans (keeping for backward compatibility)
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

def create_or_get_product_for_purchase(product_name, product_description):
    """
    Create a Stripe product for the new purchase system if it doesn't exist, or get the existing one.
    
    Args:
        product_name (str): Name of the product
        product_description (str): Description of the product
        
    Returns:
        stripe.Product: The created or retrieved Stripe product
    """
    try:
        # Search for existing products with the same name
        existing_products = stripe.Product.list(limit=10)
        for product in existing_products.data:
            if product.name == product_name:
                return product
        
        # If no product found, create a new one
        return stripe.Product.create(
            name=product_name,
            description=product_description,
            type='service'
        )
    except Exception as e:
        logging.error(f"Error creating/getting Stripe product: {str(e)}")
        raise

def create_or_get_price_for_purchase(product_id, price_in_cents, plan_code, tests, days):
    """
    Create a Stripe price for the new purchase system if it doesn't exist, or get the existing one.
    
    Args:
        product_id (str): ID of the Stripe product
        price_in_cents (int): Price in cents
        plan_code (str): Internal plan code
        tests (int): Number of tests included
        days (int): Number of days for access
        
    Returns:
        stripe.Price: The created or retrieved Stripe price
    """
    try:
        # Check for existing prices for this product
        existing_prices = stripe.Price.list(
            product=product_id,
            active=True,
            limit=10
        )
        
        # Find a price with the same amount
        for price in existing_prices.data:
            if price.unit_amount == price_in_cents:
                return price
        
        # If no price found, create a new one
        metadata = {
            'plan': plan_code,
            'tests': str(tests),
            'days': str(days)
        }
        
        return stripe.Price.create(
            product=product_id,
            unit_amount=price_in_cents,
            currency='usd',
            metadata=metadata
        )
    except Exception as e:
        logging.error(f"Error creating/getting Stripe price: {str(e)}")
        raise

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def create_stripe_checkout_session(product_name, description, price, success_url, cancel_url, country_code=None):
    """
    Create a Stripe checkout session.
    
    Args:
        product_name (str): Name of the product
        description (str): Description of the product
        price (float): Price in USD
        success_url (str): URL to redirect to on successful payment
        cancel_url (str): URL to redirect to if payment is canceled
        country_code (str, optional): Two-letter country code for regional payment methods
        
    Returns:
        stripe.checkout.Session: The created Stripe checkout session
    """
    try:
        if not stripe.api_key:
            logging.error("Stripe API key not found. Cannot create checkout session.")
            raise ValueError("Stripe API key is required")
        
        # Create a simple price-based checkout
        price_in_cents = int(price * 100)
        
        metadata = {
            'product_name': product_name,
            'price': str(price),
            'description': description
        }
        
        # Create simplified checkout session with minimal options
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': product_name,
                            'description': description,
                        },
                        'unit_amount': price_in_cents,
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata
        )
        
        # Format the return value to match what add_assessment_routes.py expects
        return {
            'session_id': checkout_session.id,
            'checkout_url': checkout_session.url
        }
        
    except Exception as e:
        logging.error(f"Error creating Stripe checkout: {str(e)}")
        raise

# Create a Stripe checkout session for speaking assessments
def create_stripe_checkout_speaking(package_type, country_code=None):
    """
    Create a Stripe checkout session for speaking assessments purchase.
    
    Args:
        package_type (str): 'basic' (4 assessments) or 'pro' (10 assessments)
        country_code (str, optional): Two-letter country code for regional payment methods
        
    Returns:
        dict: Contains session_id and checkout_url
    """
    try:
        if not stripe.api_key:
            logging.error("Stripe API key not found. Cannot create checkout session.")
            raise ValueError("Stripe API key is required")
            
        # Validate parameters
        if package_type not in TEST_PURCHASE_OPTIONS['speaking_only']:
            raise ValueError(f"Invalid speaking package: {package_type}. Must be 'basic' or 'pro'")
            
        # Get the purchase details
        purchase_details = TEST_PURCHASE_OPTIONS['speaking_only'][package_type]
        plan_code = f"speaking_only_{package_type}"  # Create a unique plan code
        
        # Get domain for success and cancel URLs
        domain = os.environ.get('REPLIT_DEV_DOMAIN') 
        if not domain and os.environ.get('REPLIT_DEPLOYMENT'):
            domain = os.environ.get('REPLIT_DOMAINS', '').split(',')[0]
        if not domain:
            domain = 'localhost:5000'
            
        # Create a Product if it doesn't exist
        product = create_or_get_product_for_purchase(purchase_details['name'], purchase_details['description'])
        
        # Create a Price if it doesn't exist
        price = create_or_get_price_for_purchase(
            product.id, 
            purchase_details['price'],
            plan_code,
            purchase_details.get('assessments', 0),
            purchase_details['days']
        )
        
        # Use the country code if provided
        user_country = country_code
        # Dynamic payment method types based on user region
        payment_method_types = ['card']
        
        # Add region-specific payment methods
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
            
        metadata = {
            'plan': plan_code,
            'type': 'speaking_only',
            'package': package_type,
            'assessments': str(purchase_details['assessments']),
            'days': str(purchase_details['days'])
        }
        
        # Create checkout session with direct price_data for better compatibility
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': purchase_details['name'],
                            'description': purchase_details['description'],
                        },
                        'unit_amount': purchase_details['price'],
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=f'https://{domain}/speaking-payment-success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'https://{domain}/payment-cancel',
            metadata=metadata
        )
        
        return {
            'session_id': checkout_session.id,
            'checkout_url': checkout_session.url
        }
        
    except Exception as e:
        logging.error(f"Error creating Stripe checkout for speaking: {str(e)}")
        raise

# For backward compatibility
def create_stripe_checkout(plan_info, country_code=None, test_type=None, test_package=None):
    """
    Create a Stripe checkout session for test purchase.
    
    Args:
        plan_info (str): Either a legacy plan ('base', 'intermediate', 'pro') 
                        or 'purchase' for the new test purchase flow
        country_code (str, optional): Two-letter country code for regional payment methods
        test_type (str, optional): 'academic' or 'general' - required if plan_info is 'purchase'
        test_package (str, optional): 'single', 'double', or 'pack' - required if plan_info is 'purchase'
    
    Returns:
        dict: Contains session_id and checkout_url
    """
    try:
        if not stripe.api_key:
            logging.error("Stripe API key not found. Cannot create checkout session.")
            raise ValueError("Stripe API key is required")
        
        # Check if we're using the new purchase system or legacy subscription
        using_new_purchase = plan_info == 'purchase' and test_type and test_package
        
        # Special case for speaking-only purchases
        if test_type == 'speaking_only' and test_package in TEST_PURCHASE_OPTIONS['speaking_only']:
            return create_stripe_checkout_speaking(test_package, country_code)
        
        # Validate parameters for new purchase system
        if using_new_purchase:
            if test_type not in TEST_PURCHASE_OPTIONS:
                raise ValueError(f"Invalid test type: {test_type}. Must be 'academic' or 'general'")
            if test_package not in TEST_PURCHASE_OPTIONS[test_type]:
                raise ValueError(f"Invalid package: {test_package}. Must be 'single', 'double', or 'pack'")
            
            # Get the purchase details
            purchase_details = TEST_PURCHASE_OPTIONS[test_type][test_package]
            plan_code = f"{test_type}_{test_package}"  # Create a unique plan code
        else:
            # Legacy subscription handling
            if plan_info not in SUBSCRIPTION_PLANS:
                plan_info = 'base'  # Default to base if invalid plan
            
            # Get the subscription details
            purchase_details = SUBSCRIPTION_PLANS[plan_info]
            plan_code = plan_info
        
        # Get domain for success and cancel URLs
        domain = os.environ.get('REPLIT_DEV_DOMAIN') 
        if not domain and os.environ.get('REPLIT_DEPLOYMENT'):
            domain = os.environ.get('REPLIT_DOMAINS', '').split(',')[0]
        if not domain:
            domain = 'localhost:5000'
        
        # Create a Product if it doesn't exist
        product = create_or_get_product_for_purchase(
            purchase_details['name'], 
            purchase_details['description']
        )
        
        # Create a Price if it doesn't exist
        price = create_or_get_price_for_purchase(
            product.id, 
            purchase_details['price'],
            plan_code,
            purchase_details.get('tests', 0),
            purchase_details['days']
        )
        
        # Use the country code if provided
        user_country = country_code
        # Dynamic payment method types based on user region
        payment_method_types = ['card']
        
        # Add region-specific payment methods
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
            
        metadata = {
            'plan': plan_code,
            'type': test_type if using_new_purchase else 'subscription',
            'package': test_package if using_new_purchase else plan_info,
            'tests': str(purchase_details.get('tests', 0)),
            'days': str(purchase_details['days'])
        }
        
        # Create checkout session with direct price_data for better compatibility
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': purchase_details['name'],
                            'description': purchase_details['description'],
                        },
                        'unit_amount': purchase_details['price'],
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',  # Using one-time payment
            success_url=f'https://{domain}/payment-success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'https://{domain}/payment-cancel',
            metadata=metadata
        )
        
        return {
            'session_id': checkout_session.id,
            'checkout_url': checkout_session.url
        }
        
    except Exception as e:
        logging.error(f"Error creating Stripe checkout: {str(e)}")
        raise

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
    from models import PaymentRecord
    from app import db
    
    try:
        # Create a new payment record
        payment = PaymentRecord(
            user_id=user_id,
            amount=amount,
            package_name=package_name,
            payment_date=datetime.utcnow(),
            stripe_session_id=session_id,
            is_successful=True,
            transaction_details=None  # Can be updated later if needed
        )
        
        # Add to database in a separate transaction
        # Using a fresh session to avoid any conflicts with existing transactions
        db.session.add(payment)
        db.session.commit()
            
        return payment
        
    except Exception as e:
        logging.error(f"Error creating payment record: {str(e)}")
        # Don't raise the exception to avoid blocking the payment flow
        # Just return None instead
        return None

def verify_stripe_payment(session_id):
    """
    Verify a Stripe payment session.
    
    Args:
        session_id (str): Stripe session ID
        
    Returns:
        dict: Payment details if verified, None otherwise
    """
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        
        # Check if payment was successful
        if session.payment_status != 'paid':
            logging.warning(f"Payment not completed for session {session_id}")
            return None
        
        # Get detailed payment info
        payment_details = {}
        
        # Add standard fields
        payment_details['amount'] = session.amount_total / 100  # Convert from cents to dollars
        payment_details['currency'] = session.currency
        
        # Add metadata if available
        if session.metadata:
            for key, value in session.metadata.items():
                payment_details[key] = value
            
        return payment_details
        
    except Exception as e:
        logging.error(f"Error verifying Stripe payment: {str(e)}")
        return None