"""
A script to fix the Stripe connection issues in the IELTS GenAI Prep application.
This script checks the Stripe configuration and verifies the connection.
"""

import os
import stripe
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def check_and_fix_stripe_connection():
    """
    Check the Stripe API connection and apply fixes if needed.
    """
    logger.info("Starting Stripe connection check...")
    
    # 1. Check if Stripe API key is available in environment
    stripe_key = os.environ.get('STRIPE_SECRET_KEY')
    
    if not stripe_key:
        logger.error("Stripe API key not found in environment variables!")
        return False
    
    logger.info(f"Found Stripe API key (starts with: {stripe_key[:4]}..., length: {len(stripe_key)})")
    
    # 2. Test the Stripe API connection
    try:
        stripe.api_key = stripe_key
        
        # Simple API call to check connection
        balance = stripe.Balance.retrieve()
        
        logger.info("✅ Stripe API connection successful!")
        logger.info(f"Account balance contains {len(balance.available)} available balance entries")
        
        # Apply fixes to the payment_services.py module
        update_payment_services()
        
        return True
    except Exception as e:
        logger.error(f"❌ Stripe API connection failed: {type(e).__name__}: {str(e)}")
        return False

def update_payment_services():
    """
    Apply fixes to payment_services.py
    """
    logger.info("Applying fixes to payment_services.py...")
    
    # Fix 1: Update the get_stripe_api_key function to ensure it also sets the key
    try:
        with open('payment_services.py', 'r') as f:
            content = f.read()
        
        # Find the get_stripe_api_key function
        old_function = '''def get_stripe_api_key():
    """Get the Stripe API key from environment variables."""
    return os.environ.get('STRIPE_SECRET_KEY', '')'''
        
        new_function = '''def get_stripe_api_key():
    """Get the Stripe API key from environment variables and set it globally."""
    api_key = os.environ.get('STRIPE_SECRET_KEY', '')
    if api_key:
        # Set the API key globally for all stripe calls
        stripe.api_key = api_key
    return api_key'''
        
        # Replace the function if found
        if old_function in content:
            content = content.replace(old_function, new_function)
            logger.info("✅ Updated get_stripe_api_key function to set global API key")
        else:
            logger.warning("Could not locate get_stripe_api_key function exactly as expected")
            
        # Fix 2: Ensure stripe.api_key is set on module import
        old_init = '''# Set Stripe API key
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', '')'''
        
        new_init = '''# Set Stripe API key - ensure it's loaded for all Stripe operations
stripe_api_key = os.environ.get('STRIPE_SECRET_KEY', '')
if stripe_api_key:
    stripe.api_key = stripe_api_key
else:
    logging.warning("STRIPE_SECRET_KEY not found in environment variables")'''
        
        # Replace the initialization if found
        if old_init in content:
            content = content.replace(old_init, new_init)
            logger.info("✅ Updated Stripe API key initialization with better error handling")
        else:
            logger.warning("Could not locate Stripe API key initialization exactly as expected")

        # Fix 3: Add explicit error message for payment service connection failures
        old_catch = '''    except Exception as e:
        logging.error(f"Error creating Stripe checkout: {str(e)}")
        raise'''
        
        new_catch = '''    except Exception as e:
        logging.error(f"Error creating Stripe checkout: {str(e)}")
        
        # Check if it's a connection error
        if "connection" in str(e).lower() or "network" in str(e).lower() or "timeout" in str(e).lower():
            logging.error("Stripe connection error detected - service may be temporarily unavailable")
            raise ValueError("Could not connect to payment service. Please try again later.")
        
        # Re-raise the original exception
        raise'''
        
        # Replace the exception handling if found
        if old_catch in content:
            content = content.replace(old_catch, new_catch)
            logger.info("✅ Improved exception handling for Stripe connection errors")
        else:
            logger.warning("Could not locate exception handling code exactly as expected")
            
        # Write the updated content back to the file
        with open('payment_services.py', 'w') as f:
            f.write(content)
        
        logger.info("✅ Successfully updated payment_services.py")
        
    except Exception as e:
        logger.error(f"Failed to update payment_services.py: {str(e)}")

if __name__ == "__main__":
    if check_and_fix_stripe_connection():
        print("\n✅ Stripe connection is working correctly and fixes have been applied.")
        print("Please restart the application for changes to take effect.")
    else:
        print("\n❌ Stripe connection check failed.")
        print("Please verify your Stripe API key and try again.")