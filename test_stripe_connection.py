"""
Test Stripe Connection and API Keys
This script tests the Stripe connection and API keys to troubleshoot checkout issues.
"""
import os
import stripe
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')

def test_stripe_connection():
    """Test Stripe API connection and key validity."""
    print("======================================")
    print("STRIPE CONNECTION TEST")
    print("======================================")
    
    # Check if API keys are set in environment
    stripe_secret_key = os.environ.get('STRIPE_SECRET_KEY', '')
    stripe_public_key = os.environ.get('STRIPE_PUBLISHABLE_KEY', '')
    
    if not stripe_secret_key:
        print("❌ ERROR: STRIPE_SECRET_KEY is not set in environment variables")
        return False
    
    if not stripe_public_key:
        print("❌ ERROR: STRIPE_PUBLISHABLE_KEY is not set in environment variables")
        return False
    
    print("✓ Stripe API keys are set in environment variables")
    
    # Mask the keys for security when printing
    masked_secret = f"{stripe_secret_key[:4]}...{stripe_secret_key[-4:]}" if len(stripe_secret_key) > 8 else "****"
    masked_public = f"{stripe_public_key[:4]}...{stripe_public_key[-4:]}" if len(stripe_public_key) > 8 else "****"
    
    print(f"Secret Key: {masked_secret}")
    print(f"Public Key: {masked_public}")
    
    # Test if we can connect to Stripe API
    try:
        # Set the API key
        stripe.api_key = stripe_secret_key
        
        # Try to make a simple API call (list customers with a limit of 1)
        response = stripe.Customer.list(limit=1)
        
        print("✓ Successfully connected to Stripe API")
        print(f"✓ Retrieved {len(response.data)} customers")
        
        # Test creating a dummy product
        test_product_name = f"TEST_PRODUCT_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        try:
            product = stripe.Product.create(
                name=test_product_name,
                description="Test product for connection verification",
                type='service'
            )
            
            print(f"✓ Successfully created test product: {product.id}")
            
            # Clean up by archiving the test product
            stripe.Product.modify(
                product.id,
                active=False
            )
            print(f"✓ Successfully archived test product")
            
        except Exception as e:
            print(f"❌ Error creating test product: {str(e)}")
            return False
        
        # Test creating a checkout session object (without actually using it)
        try:
            # Get domain for success and cancel URLs
            domain = os.environ.get('REPLIT_DEV_DOMAIN') 
            if not domain and os.environ.get('REPLIT_DEPLOYMENT'):
                domain = os.environ.get('REPLIT_DOMAINS', '').split(',')[0]
            if not domain:
                domain = 'localhost:5000'
            
            # Build the success and cancel URLs
            success_url = f"https://{domain}/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
            cancel_url = f"https://{domain}/cart"
            
            # Create the checkout session parameters
            session_params = {
                'payment_method_types': ['card'],
                # 'automatic_payment_methods' parameter removed - not supported by current Stripe version
                'line_items': [
                    {
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': 'Test Product',
                                'description': 'Test checkout session',
                            },
                            'unit_amount': 1000,  # $10.00
                        },
                        'quantity': 1,
                    },
                ],
                'mode': 'payment',
                'success_url': success_url,
                'cancel_url': cancel_url,
            }
            
            # Create the checkout session
            checkout_session = stripe.checkout.Session.create(**session_params)
            
            print(f"✓ Successfully created test checkout session: {checkout_session.id}")
            print(f"✓ Checkout URL: {checkout_session.url}")
            
            # All tests passed
            return True
        except Exception as e:
            print(f"❌ Error creating test checkout session: {str(e)}")
            return False
        
    except Exception as e:
        print(f"❌ Failed to connect to Stripe API: {str(e)}")
        # If it's an authentication error, suggest checking the key
        if "authentication" in str(e).lower() or "unauthorized" in str(e).lower():
            print("ℹ️ This may be due to an invalid API key. Check your Stripe dashboard for the correct key.")
            print("ℹ️ Make sure you're using the correct key for your environment (test vs. production).")
        return False

if __name__ == "__main__":
    result = test_stripe_connection()
    
    print("\n======================================")
    if result:
        print("✅ All Stripe connection tests PASSED")
        print("If you're still having issues with checkout, check:")
        print("1. Your cart_routes.py and payment_services.py error handling")
        print("2. Network connectivity issues in your environment")
        print("3. Browser console for JavaScript errors")
    else:
        print("❌ Stripe connection tests FAILED")
        print("Please fix the issues mentioned above before proceeding.")
    print("======================================")