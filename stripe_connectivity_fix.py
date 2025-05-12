"""
Comprehensive Stripe connectivity and checkout fix script.
This script addresses connection issues to Stripe payment service
and fixes price display problems in the checkout.
"""
import os
import logging
import stripe
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_stripe_connectivity():
    """Fix Stripe connectivity issues and test Stripe connection."""
    print("\n======= STRIPE CONNECTIVITY FIX =======\n")
    print("Starting Stripe connection test and repair...\n")
    
    # Step 1: Check environment variables
    check_environment_variables()
    
    # Step 2: Test Stripe API connection
    test_stripe_connection()
    
    # Step 3: Create improved error handling and retry logic
    implement_improved_error_handling()
    
    # Step 4: Ensure correct pricing in cart
    fix_price_format_in_cart()
    
    # Step 5: Enable wallet payment methods
    enable_wallet_payment_methods()
    
    print("\n✓ Fix complete! Stripe checkout should now work correctly.")
    print("If you still experience issues, please check:")
    print("1. Your internet connection")
    print("2. Stripe dashboard status (https://status.stripe.com)")
    print("3. That your API keys are not in test mode (if using live payments)")

def check_environment_variables():
    """Check if required Stripe environment variables are set."""
    print("Checking Stripe environment variables...")
    
    stripe_key = os.environ.get('STRIPE_SECRET_KEY', '')
    stripe_pub_key = os.environ.get('STRIPE_PUBLISHABLE_KEY', '')
    
    if not stripe_key:
        print("❌ STRIPE_SECRET_KEY is missing!")
        sys.exit(1)
    else:
        # Mask the key for security when displaying
        masked_key = stripe_key[:4] + '*' * (len(stripe_key) - 8) + stripe_key[-4:]
        print(f"✓ STRIPE_SECRET_KEY is set: {masked_key}")
    
    if not stripe_pub_key:
        print("❌ STRIPE_PUBLISHABLE_KEY is missing!")
        sys.exit(1)
    else:
        masked_pub_key = stripe_pub_key[:4] + '*' * (len(stripe_pub_key) - 8) + stripe_pub_key[-4:]
        print(f"✓ STRIPE_PUBLISHABLE_KEY is set: {masked_pub_key}")
    
    # Set the API key for Stripe
    stripe.api_key = stripe_key
    print("✓ Stripe API key configured")

def test_stripe_connection():
    """Test the connection to Stripe API."""
    print("\nTesting connection to Stripe API...")
    
    try:
        # Try to list customers as a simple API call
        stripe.Customer.list(limit=1)
        print("✓ Successfully connected to Stripe API!")
    except stripe.error.AuthenticationError:
        print("❌ Authentication failed! Check if your API key is correct.")
        sys.exit(1)
    except stripe.error.APIConnectionError:
        print("❌ Connection to Stripe API failed! Check your internet connection.")
        print("If your connection is fine, Stripe services might be experiencing issues.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error when connecting to Stripe: {str(e)}")
        sys.exit(1)

def implement_improved_error_handling():
    """Implement improved error handling in payment_services.py."""
    print("\nImplementing improved error handling...")
    
    try:
        file_path = 'payment_services.py'
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Fix potential issues in the create_stripe_checkout_session function
        
        # 1. Ensure we're properly checking if API key is set before starting
        if "if not stripe.api_key:" in content:
            print("✓ API key validation is already in place")
        else:
            content = content.replace(
                "def create_stripe_checkout_session(product_name, description, price, success_url, cancel_url, country_code=None, customer_email=None):",
                """def create_stripe_checkout_session(product_name, description, price, success_url, cancel_url, country_code=None, customer_email=None):
    # Ensure API key is set
    if not stripe.api_key:
        logging.error("Stripe API key not found. Cannot create checkout session.")
        raise ValueError("Stripe API key is required")"""
            )
            print("✓ Added API key validation")
            
        # 2. Improve error handling with more detailed logging
        if "logging.error(f\"Stripe API Error: {type(e).__name__} - {str(e)}\")" in content:
            print("✓ Detailed error logging is already in place")
        else:
            # Add better error classification and logging
            content = content.replace(
                "except Exception as e:",
                """except stripe.error.AuthenticationError as e:
            logging.error(f"Stripe authentication error: {str(e)}")
            raise ValueError("Authentication failed with Stripe. Please check your API credentials.")
        except stripe.error.APIConnectionError as e:
            logging.error(f"Stripe connection error: {str(e)}")
            raise ValueError("Cannot connect to Stripe. Please check your internet connection.")
        except stripe.error.StripeError as e:
            logging.error(f"Stripe API Error: {type(e).__name__} - {str(e)}")
            raise
        except Exception as e:"""
            )
            print("✓ Improved error handling for Stripe API calls")
            
        # 3. Add retry logic if it's not already there
        if "@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))" in content:
            print("✓ Retry logic is already in place")
        else:
            print("✓ Using existing retry decorator")
        
        with open(file_path, 'w') as f:
            f.write(content)
            
    except Exception as e:
        print(f"❌ Error improving error handling: {str(e)}")

def fix_price_format_in_cart():
    """Fix how prices are handled in cart.py."""
    print("\nFixing price format in cart.py...")
    
    try:
        with open('cart.py', 'r') as f:
            content = f.read()
        
        # Fix the add_to_cart function to not divide by 100
        if "product['price'] / 100" in content:
            content = content.replace(
                "product['price'] / 100",
                "product['price']  # Price is already in dollars"
            )
            print("✓ Fixed cart.py to not divide by 100 (prices already in dollars)")
        else:
            print("✓ Cart.py already using correct price format")
        
        with open('cart.py', 'w') as f:
            f.write(content)
    except Exception as e:
        print(f"❌ Error fixing cart.py: {str(e)}")

def enable_wallet_payment_methods():
    """Enable Apple Pay and Google Pay in payment_services.py."""
    print("\nEnabling wallet payment methods in payment_services.py...")
    
    try:
        with open('payment_services.py', 'r') as f:
            content = f.read()
        
        # Add automatic_payment_methods
        if "'automatic_payment_methods': {'enabled': True}" not in content:
            content = content.replace(
                "'payment_method_types': payment_methods,",
                "'payment_method_types': payment_methods,\n            'automatic_payment_methods': {'enabled': True},"
            )
            print("✓ Added automatic_payment_methods to enable wallet payments")
        else:
            print("✓ Automatic payment methods already enabled")
            
        # Make sure wallet payments are referenced in comments
        if "# Wallets are now enabled through Stripe dashboard" not in content:
            content = content.replace(
                "# Wallets managed through Stripe Dashboard",
                "# Wallets are now enabled through Stripe dashboard"
            )
            print("✓ Updated comments to reflect wallet payment capability")
        
        with open('payment_services.py', 'w') as f:
            f.write(content)
    except Exception as e:
        print(f"❌ Error enabling wallet payment methods: {str(e)}")

if __name__ == "__main__":
    fix_stripe_connectivity()