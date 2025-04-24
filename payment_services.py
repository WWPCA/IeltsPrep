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
        
        # Create a product
        product = create_or_get_product_for_purchase(product_name, description)
        
        # Create a price (convert price from dollars to cents)
        price_in_cents = int(price * 100)
        price_obj = create_or_get_price_for_purchase(
            product.id,
            price_in_cents,
            product_name.lower().replace(' ', '_'),
            1,  # tests
            30  # days
        )
        
        # Use only 'card' payment method to avoid compatibility issues
        payment_method_types = ['card']
        
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
        if country_code and country_code in region_payment_mapping:
            payment_method_types.extend(region_payment_mapping[country_code])
        
        metadata = {
            'product_name': product_name,
            'price': str(price),
            'description': description
        }
        
        # Create checkout session with all payment options
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=payment_method_types,
            line_items=[
                {
                    'price': price_obj.id,
                    'quantity': 1,
                },
            ],
            mode='payment',  # Using one-time payment instead of subscription
            success_url=success_url,
            cancel_url=cancel_url,
            payment_method_options={
                'card': {
                    'wallet': {
                        'applePay': 'auto',
                        'googlePay': 'auto',
                    }
                }
            },
            metadata=metadata
        )
        
        return checkout_session
        
    except Exception as e:
        logging.error(f"Error creating Stripe checkout: {str(e)}")
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
        if using_new_purchase:
            product = create_or_get_product_for_purchase(purchase_details['name'], purchase_details['description'])
            
            # Create a Price if it doesn't exist
            price = create_or_get_price_for_purchase(
                product.id, 
                purchase_details['price'],
                plan_code,
                purchase_details['tests'],
                purchase_details['days']
            )
        else:
            # Legacy product and price handling
            product = create_or_get_product(plan_info)
            price = create_or_get_price(product.id, plan_info)
        
        # Use the country code if provided
        user_country = country_code
        # Dynamic payment method types based on user region
        # Only use 'card' to avoid compatibility issues
        payment_method_types = ['card']
        
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
        
        metadata = {}
        if using_new_purchase:
            metadata = {
                'plan': plan_code,
                'test_type': test_type,
                'test_package': test_package,
                'tests': str(purchase_details['tests']),
                'days': str(purchase_details['days'])
            }
        else:
            metadata = {
                'plan': plan_info,
                'tests': str(purchase_details['tests']),
                'days': str(purchase_details['days'])
            }
            
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
            metadata=metadata
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

def create_payment_record(user_id, amount, package, session_id):
    """
    Create a payment record for audit and tracking purposes.
    
    Args:
        user_id (int): User ID making the payment
        amount (float): Payment amount
        package (str): Package purchased ('single', 'double', 'pack')
        session_id (str): Stripe session ID for reference
        
    Returns:
        dict: Payment record data
    """
    # This is a placeholder function - in a real implementation, you would 
    # save this information to a database. For now, we just return a dict.
    payment_record = {
        'user_id': user_id,
        'amount': amount,
        'package': package,
        'session_id': session_id,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    logging.info(f"Payment record created: {payment_record}")
    return payment_record

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def verify_stripe_payment(session_id):
    """
    Verify a Stripe payment using the session ID.
    
    Args:
        session_id (str): Stripe checkout session ID
        
    Returns:
        bool: True if payment was successful, False otherwise
    """
    try:
        if not stripe.api_key:
            logging.error("Stripe API key not found. Cannot verify payment.")
            return False
        
        # Retrieve the session
        session = stripe.checkout.Session.retrieve(session_id)
        
        # Check payment status
        return session.payment_status == 'paid'
    except Exception as e:
        logging.error(f"Error verifying Stripe payment: {str(e)}")
        return False

# For backward compatibility
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
            # Get metadata from the session
            plan = session.metadata.get('plan', 'base')
            
            # Check if this is a test purchase by looking for test_type in metadata
            is_test_purchase = 'test_type' in session.metadata and 'test_package' in session.metadata
            
            if is_test_purchase:
                # Test purchase flow
                test_type = session.metadata.get('test_type')
                test_package = session.metadata.get('test_package')
                tests = int(session.metadata.get('tests', 1))
                days = int(session.metadata.get('days', 15))
                
                return {
                    'paid': True,
                    'plan': plan,
                    'test_type': test_type,
                    'test_package': test_package,
                    'tests': tests,
                    'days': days,
                    'customer': session.customer
                }
            else:
                # Legacy subscription flow
                try:
                    tests = int(session.metadata.get('tests', SUBSCRIPTION_PLANS[plan]['tests']))
                    days = int(session.metadata.get('days', SUBSCRIPTION_PLANS[plan]['days']))
                except KeyError:
                    # Fallback to defaults if plan info not found
                    tests = int(session.metadata.get('tests', 3))
                    days = int(session.metadata.get('days', 30))
                
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

def create_or_get_product_for_purchase(product_name, product_description):
    """
    Create a Stripe product for the new purchase system if it doesn't exist, or get the existing one.
    
    Args:
        product_name (str): The name of the product
        product_description (str): The description of the product
        
    Returns:
        stripe.Product: The Stripe product
    """
    try:
        # List products with the given name
        products = stripe.Product.list(
            active=True,
            limit=10
        )
        
        for product in products.data:
            if product.name == product_name:
                return product
        
        # If no product found, create one
        return stripe.Product.create(
            name=product_name,
            description=product_description
        )
    except Exception as e:
        logging.error(f"Error creating/getting Stripe product: {str(e)}")
        raise

def create_or_get_price_for_purchase(product_id, price_amount, plan_code, tests, days):
    """
    Create a Stripe price for the new purchase system if it doesn't exist, or get the existing one.
    
    Args:
        product_id (str): The Stripe product ID
        price_amount (int): The price amount in cents
        plan_code (str): The unique plan code (e.g., 'academic_single')
        tests (int): Number of tests included
        days (int): Number of days of access
        
    Returns:
        stripe.Price: The Stripe price
    """
    try:
        # List prices for the given product
        prices = stripe.Price.list(
            product=product_id,
            active=True,
            limit=10
        )
        
        # Find a price with the correct amount and matching metadata
        for price in prices.data:
            if price.unit_amount == price_amount and price.metadata.get('plan') == plan_code:
                return price
        
        # If no price found, create one
        return stripe.Price.create(
            product=product_id,
            unit_amount=price_amount,
            currency='usd',
            metadata={
                'plan': plan_code,
                'tests': str(tests),
                'days': str(days)
            }
        )
    except Exception as e:
        logging.error(f"Error creating/getting Stripe price: {str(e)}")
        raise

# Additional payment methods could be implemented here for regional options
