import os
import stripe
import logging
import json
from flask import session
from tenacity import retry, stop_after_attempt, wait_fixed
from datetime import datetime, timedelta
from country_restrictions import is_country_restricted, get_allowed_countries, validate_billing_country
from payment_country_check import get_effective_country_code, check_country_restriction

# Set Stripe API key
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', '')

# Comprehensive region payment mapping for Stripe
# NOTE: Only include payment methods actually supported by Stripe
REGION_PAYMENT_MAPPING = {
    # East Asia
    'CN': ['alipay', 'wechat_pay'],
    'HK': ['alipay', 'fps', 'octopus'],
    'JP': ['konbini', 'jcb', 'payeasy'],
    'KR': ['kakaopay'],
    'TW': ['line_pay'],
    
    # Southeast Asia
    'MY': ['grabpay', 'fpx', 'boost'],
    'TH': ['promptpay'],
    'ID': ['gopay', 'ovo'],
    'PH': ['gcash', 'paymaya'],
    'SG': ['grabpay', 'paynow'],
    'VN': ['momo'],
    
    # South Asia
    'IN': ['upi', 'netbanking'],
    'PK': ['bacs_debit'],
    'BD': ['bacs_debit'],
    'NP': ['bacs_debit'],
    
    # Latin America
    'BR': ['boleto', 'pix'],
    'MX': ['oxxo', 'spei'],
    'AR': ['rapipago'],
    'CL': ['webpay'],
    'CO': ['pse'],
    
    # Middle East
    'AE': ['benefit'],
    'SA': ['mada'],
    'IL': ['eps'],
    'TR': ['sofort'],
    
    # Africa
    'ZA': ['eftsecure'],
    'NG': ['paystack'],
    'EG': ['fawry'],
    'KE': ['bacs_debit'],
    
    # Oceania
    'AU': ['afterpay_clearpay', 'au_becs_debit'],
    'NZ': ['afterpay_clearpay'],
    
    # North America
    'CA': ['acss_debit', 'interac'],
    'US': ['affirm', 'us_bank_account', 'cashapp', 'link', 'apple_pay', 'google_pay'],
    
    # Europe
    'GB': ['bacs_debit', 'ideal'],
    'FR': ['sepa_debit', 'bancontact'],
    'DE': ['giropay', 'sepa_debit', 'sofort'],
    'IT': ['p24', 'sepa_debit'],
    'ES': ['sepa_debit', 'multibanco'],
    'NL': ['ideal', 'sepa_debit'],
    'BE': ['bancontact', 'sepa_debit'],
    'AT': ['eps', 'sepa_debit'],
    'PL': ['blik', 'p24'],
    'PT': ['multibanco', 'sepa_debit'],
    'CH': ['sofort', 'twint', 'sepa_debit'],
    'SE': ['klarna', 'swish'],
    'NO': ['vipps'],
    'FI': ['mobile_pay'],
    'DK': ['mobile_pay'],
    'IE': ['sepa_debit'],
    'CZ': ['eps'],
    'RO': ['sepa_debit'],
    'HU': ['eps']
}

def get_country_payment_methods(country_code):
    """
    Get the list of supported payment methods for a given country.
    
    Args:
        country_code (str): Two-letter country code
        
    Returns:
        list: Supported payment methods for the country
    """
    if not country_code:
        return []
        
    # Standardize the country code
    country_code = country_code.upper()
    
    # Get payment methods for the country
    return REGION_PAYMENT_MAPPING.get(country_code, [])

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
def create_stripe_checkout_session(product_name, description, price, success_url, cancel_url, country_code=None, customer_email=None):
    """
    Create a Stripe checkout session with enhanced features based on the latest Stripe guidelines.
    
    Args:
        product_name (str): Name of the product
        description (str): Description of the product
        price (float): Price in USD
        success_url (str): URL to redirect to on successful payment
        cancel_url (str): URL to redirect to if payment is canceled
        country_code (str, optional): Two-letter country code for regional payment methods
        customer_email (str, optional): Pre-fill customer email if available
        
    Returns:
        dict: Contains session_id and checkout_url
        
    Raises:
        ValueError: If the country is restricted by our policy
    """
    try:
        # Check country restrictions
        check_country_restriction(country_code, is_country_restricted)
            
        if not stripe.api_key:
            logging.error("Stripe API key not found. Cannot create checkout session.")
            raise ValueError("Stripe API key is required")
        
        # Create a simple price-based checkout
        price_in_cents = int(price * 100)
        
        metadata = {
            'product_name': product_name,
            'price': str(price),
            'description': description,
            'source': 'ielts_genai_prep',
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Ensure the success_url includes the session ID parameter
        if '{CHECKOUT_SESSION_ID}' not in success_url:
            if '?' in success_url:
                success_url += '&session_id={CHECKOUT_SESSION_ID}'
            else:
                success_url += '?session_id={CHECKOUT_SESSION_ID}'
        
        # Determine payment method types based on country
        payment_methods = ['card']
        if country_code:
            additional_methods = get_country_payment_methods(country_code)
            if additional_methods:
                payment_methods.extend(additional_methods)
        
        # Build checkout session parameters
        # Get the list of allowed countries (countries that are not restricted)
        allowed_countries = get_allowed_countries()
        
        session_params = {
            'payment_method_types': payment_methods,
            'line_items': [
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': product_name,
                            'description': description,
                        },
                        'unit_amount': price_in_cents,
                        'tax_behavior': 'exclusive',  # Tax is calculated on top of this price
                    },
                    'quantity': 1,
                },
            ],
            'mode': 'payment',
            'success_url': success_url,
            'cancel_url': cancel_url,
            'metadata': metadata,
            'automatic_tax': {'enabled': True},         # Enable automatic tax calculation
            'customer_creation': 'always',              # Always create a customer
            'billing_address_collection': 'required',   # Always collect billing address for tax
            'payment_intent_data': {
                'setup_future_usage': 'off_session',    # Allow future payments without authentication
                'capture_method': 'automatic',          # Capture funds automatically
            },
            # Country restrictions will be handled post-checkout via webhook validation
            # Stripe doesn't support allowed_countries parameter directly
        }
        
        # Add customer email if provided
        if customer_email:
            session_params['customer_email'] = customer_email
        
        # Create checkout session with enhanced options
        checkout_session = stripe.checkout.Session.create(**session_params)
        
        # Format the return value to match what add_assessment_routes.py expects
        return {
            'session_id': checkout_session.id,
            'checkout_url': checkout_session.url
        }
        
    except Exception as e:
        logging.error(f"Error creating Stripe checkout: {str(e)}")
        raise

# Create a Stripe checkout session for speaking assessments
def create_stripe_checkout_speaking(package_type, country_code=None, customer_email=None):
    """
    Create a Stripe checkout session for speaking assessments purchase.
    
    Args:
        package_type (str): 'basic' (4 assessments) or 'pro' (10 assessments)
        country_code (str, optional): Two-letter country code for regional payment methods
        customer_email (str, optional): Pre-fill customer email if available
        
    Returns:
        dict: Contains session_id and checkout_url
        
    Raises:
        ValueError: If the country is restricted by our policy
    """
    try:
        # Check country restrictions
        check_country_restriction(country_code, is_country_restricted)
            
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
        
        # Get the list of allowed countries (countries that are not restricted)
        allowed_countries = get_allowed_countries()
        
        # Create checkout session with direct price_data for better compatibility
        session_params = {
            'payment_method_types': payment_method_types,
            'line_items': [
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': purchase_details['name'],
                            'description': purchase_details['description'],
                        },
                        'unit_amount': purchase_details['price'],
                        'tax_behavior': 'exclusive',  # Tax is calculated on top of this price
                    },
                    'quantity': 1,
                },
            ],
            'mode': 'payment',
            'success_url': f'https://{domain}/speaking-payment-success?session_id={{CHECKOUT_SESSION_ID}}',
            'cancel_url': f'https://{domain}/payment-cancel',
            'metadata': metadata,
            'automatic_tax': {'enabled': True},  # Enable automatic tax calculation
            'billing_address_collection': 'required',  # Collect billing address for tax purposes
            # Restrict billing to allowed countries only
            # Country restrictions will be handled post-checkout via webhook validation
            # Stripe doesn't support allowed_countries parameter directly
            'payment_intent_data': {
                'setup_future_usage': 'off_session',  # Allow future payments without authentication
                'capture_method': 'automatic',  # Capture funds automatically
            },
            'customer_creation': 'always',  # Always create a customer in Stripe
        }
        
        # Add customer email if provided
        if customer_email:
            session_params['customer_email'] = customer_email
            
        checkout_session = stripe.checkout.Session.create(**session_params)
        
        return {
            'session_id': checkout_session.id,
            'checkout_url': checkout_session.url
        }
        
    except Exception as e:
        logging.error(f"Error creating Stripe checkout for speaking: {str(e)}")
        raise

# For backward compatibility
def create_stripe_checkout(plan_info, country_code=None, test_type=None, test_package=None, customer_email=None):
    """
    Create a Stripe checkout session for test purchase.
    
    Args:
        plan_info (str): Either a legacy plan ('base', 'intermediate', 'pro') 
                        or 'purchase' for the new test purchase flow
        country_code (str, optional): Two-letter country code for regional payment methods
        test_type (str, optional): 'academic' or 'general' - required if plan_info is 'purchase'
        test_package (str, optional): 'single', 'double', or 'pack' - required if plan_info is 'purchase'
        customer_email (str, optional): Pre-fill customer email if available
    
    Returns:
        dict: Contains session_id and checkout_url
        
    Raises:
        ValueError: If the country is restricted by our policy
    """
    # Check country restrictions
    check_country_restriction(country_code, is_country_restricted)
    try:
        if not stripe.api_key:
            logging.error("Stripe API key not found. Cannot create checkout session.")
            raise ValueError("Stripe API key is required")
        
        # Check if we're using the new purchase system or legacy subscription
        using_new_purchase = plan_info == 'purchase' and test_type and test_package
        
        # Special case for speaking-only purchases
        if test_type == 'speaking_only' and test_package and 'speaking_only' in TEST_PURCHASE_OPTIONS:
            if test_package in TEST_PURCHASE_OPTIONS.get('speaking_only', {}):
                return create_stripe_checkout_speaking(test_package, country_code, customer_email)
            else:
                logging.error(f"Invalid speaking package: {test_package}")
                raise ValueError(f"Invalid speaking package: {test_package}")
        
        # Validate parameters for new purchase system
        if using_new_purchase:
            if not test_type or test_type not in TEST_PURCHASE_OPTIONS:
                logging.error(f"Invalid test type: {test_type}")
                raise ValueError(f"Invalid test type: {test_type}. Must be 'academic' or 'general'")
                
            test_options = TEST_PURCHASE_OPTIONS.get(test_type, {})
            if not test_package or test_package not in test_options:
                logging.error(f"Invalid package: {test_package}")
                raise ValueError(f"Invalid package: {test_package}. Must be 'single', 'double', or 'pack'")
            
            # Get the purchase details
            purchase_details = test_options.get(test_package)
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
        
        # Get the list of allowed countries (countries that are not restricted)
        allowed_countries = get_allowed_countries()
        
        # Create checkout session with direct price_data for better compatibility
        session_params = {
            'payment_method_types': payment_method_types,
            'line_items': [
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': purchase_details['name'],
                            'description': purchase_details['description'],
                        },
                        'unit_amount': purchase_details['price'],
                        'tax_behavior': 'exclusive',  # Tax is calculated on top of this price
                    },
                    'quantity': 1,
                },
            ],
            'mode': 'payment',  # Using one-time payment
            'success_url': f'https://{domain}/payment-success?session_id={{CHECKOUT_SESSION_ID}}',
            'cancel_url': f'https://{domain}/payment-cancel',
            'metadata': metadata,
            'automatic_tax': {'enabled': True},  # Enable automatic tax calculation
            'billing_address_collection': 'required',  # Collect billing address for tax purposes
            # Restrict billing to allowed countries only
            # Country restrictions will be handled post-checkout via webhook validation
            # Stripe doesn't support allowed_countries parameter directly
            'payment_intent_data': {
                'setup_future_usage': 'off_session',  # Allow future payments without authentication
                'capture_method': 'automatic',  # Capture funds automatically
            },
            'customer_creation': 'always',  # Always create a customer in Stripe
        }
        
        # Add customer email if provided
        if customer_email:
            session_params['customer_email'] = customer_email
            
        checkout_session = stripe.checkout.Session.create(**session_params)
        
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
        payment = PaymentRecord()
        payment.user_id = user_id
        payment.amount = amount
        payment.package_name = package_name
        payment.payment_date = datetime.utcnow()
        payment.stripe_session_id = session_id
        payment.is_successful = True
        payment.transaction_details = f"Stripe payment: {session_id}"
        
        # Add to database with proper error handling
        try:
            db.session.add(payment)
            db.session.commit()
            return payment
        except Exception as db_error:
            # If there's an error during commit, rollback and try again
            db.session.rollback()
            logging.warning(f"Initial payment record commit failed, rolling back: {str(db_error)}")
            
            # Try again with a new session context
            try:
                # Create a new payment record since the old one may be in an inconsistent state
                new_payment = PaymentRecord()
                new_payment.user_id = user_id
                new_payment.amount = amount
                new_payment.package_name = package_name
                new_payment.payment_date = datetime.utcnow()
                new_payment.stripe_session_id = session_id
                new_payment.is_successful = True
                new_payment.transaction_details = "Retry attempt after database error"
                db.session.add(new_payment)
                db.session.commit()
                return new_payment
            except Exception as retry_error:
                db.session.rollback()
                logging.error(f"Retry payment record creation failed: {str(retry_error)}")
                return None
        
    except Exception as e:
        logging.error(f"Error creating payment record: {str(e)}")
        # Don't raise the exception to avoid blocking the payment flow
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
        if not stripe.api_key:
            logging.error("Stripe API key not found. Cannot verify payment.")
            return None
            
        session = stripe.checkout.Session.retrieve(session_id)
        
        # Check if payment was successful
        if not session or not hasattr(session, 'payment_status') or session.payment_status != 'paid':
            logging.warning(f"Payment not completed for session {session_id}")
            return None
        
        # Get detailed payment info
        payment_details = {}
        
        # Add standard fields - the Stripe API returns objects with attributes, not dictionaries
        if hasattr(session, 'amount_total') and session.amount_total is not None:
            payment_details['amount'] = session.amount_total / 100  # Convert from cents to dollars
        else:
            payment_details['amount'] = 0
            
        payment_details['currency'] = getattr(session, 'currency', 'usd')
        
        # Add metadata if available
        metadata = getattr(session, 'metadata', None)
        if metadata:
            # Some Stripe objects return dictionaries, others return objects with attributes
            if isinstance(metadata, dict):
                for key, value in metadata.items():
                    payment_details[key] = value
            else:
                for key in dir(metadata):
                    if not key.startswith('_') and not callable(getattr(metadata, key)):
                        payment_details[key] = getattr(metadata, key)
            
        return payment_details
        
    except Exception as e:
        logging.error(f"Error verifying Stripe payment: {str(e)}")
        return None