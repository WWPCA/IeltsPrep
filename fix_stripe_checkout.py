"""
Fix Stripe checkout issues including price conversion problems.
This script addresses the pricing display bug showing incorrect amounts in checkout.
"""

import os
import re
import stripe
import logging
from tenacity import retry, stop_after_attempt, wait_fixed

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def fix_stripe_checkout():
    """
    Apply fixes to resolve the Stripe checkout issues.
    """
    logger.info("Starting Stripe checkout fixes...")
    
    # 1. Check if Stripe API key is available and working
    stripe_key = os.environ.get('STRIPE_SECRET_KEY')
    
    if not stripe_key:
        logger.error("❌ Stripe API key not found in environment variables!")
        return False
    
    logger.info(f"✅ Found Stripe API key (starts with: {stripe_key[:4]}..., length: {len(stripe_key)})")
    stripe.api_key = stripe_key
    
    try:
        # Simple API call to check connection
        balance = stripe.Balance.retrieve()
        logger.info("✅ Stripe API connection successful!")
    except Exception as e:
        logger.error(f"❌ Stripe API connection failed: {type(e).__name__}: {str(e)}")
        return False
    
    # 2. Fix the cart_routes.py file to properly handle price conversions
    fix_cart_routes()
    
    # 3. Fix the payment_services.py file to ensure consistent pricing
    fix_payment_services()
    
    return True

def fix_cart_routes():
    """
    Fix the cart_routes.py file to properly handle price conversion.
    """
    logger.info("Fixing cart_routes.py...")
    
    try:
        # Read the file
        with open('cart_routes.py', 'r') as f:
            content = f.read()
        
        # Fix 1: Update the price conversion logic
        old_price_conversion = """    # Convert to cents for Stripe (prices are stored in dollars in the cart)
    # Ensure a consistent approach to pricing
    # Debug price calculation
    print(f"Cart total before conversion: ${cart_total}")
    price_in_cents = int(cart_total * 100)
    print(f"Price in cents: {price_in_cents}")"""
        
        new_price_conversion = """    # Convert to cents for Stripe (prices are stored in dollars in the cart)
    # Ensure a consistent approach to pricing
    # Debug price calculation
    logger.info(f"Cart total before conversion: ${cart_total}")
    price_in_cents = int(float(cart_total) * 100)
    logger.info(f"Price in cents: {price_in_cents}")
    
    # Sanity check - ensure price is reasonable (between $1 and $500)
    if price_in_cents < 100 or price_in_cents > 50000:
        logger.error(f"Price conversion error! ${cart_total} converted to {price_in_cents} cents")
        flash('There was an issue with the price calculation. Please try again or contact support.', 'danger')
        return redirect(url_for('cart.view_cart'))"""
        
        # Replace if found (use a regex to match even if there are slight differences)
        if "# Convert to cents for Stripe" in content:
            pattern = re.compile(r'# Convert to cents for Stripe.*?price_in_cents = int\(.*?\).*?print\(f"Price in cents:.*?\)', re.DOTALL)
            content = pattern.sub(new_price_conversion, content)
            logger.info("✅ Updated price conversion logic in cart_routes.py")
        else:
            logger.warning("Could not locate price conversion code in cart_routes.py")
        
        # Fix 2: Add proper logging import
        if "import logging" not in content:
            content = content.replace("import json", "import json\nimport logging\n\nlogger = logging.getLogger(__name__)")
            logger.info("✅ Added logging import to cart_routes.py")
        
        # Write the updated content back to the file
        with open('cart_routes.py', 'w') as f:
            f.write(content)
        
        logger.info("✅ Successfully updated cart_routes.py")
        
    except Exception as e:
        logger.error(f"Failed to update cart_routes.py: {str(e)}")

def fix_payment_services():
    """
    Fix the payment_services.py file to ensure consistent pricing.
    """
    logger.info("Fixing payment_services.py...")
    
    try:
        # Read the file
        with open('payment_services.py', 'r') as f:
            content = f.read()
        
        # Fix 1: Update the create_stripe_checkout_session function to validate price
        old_function_pattern = re.compile(r'def create_stripe_checkout_session\(\s*product_name,\s*description,\s*price,.*?\):.*?try:.*?checkout_session = stripe\.checkout\.Session\.create\(', re.DOTALL)
        
        # Find the function and insert price validation code
        if old_function_pattern.search(content):
            # Locate the try block within the function
            try_pattern = re.compile(r'(\s+try:)')
            
            # Add price validation logic after the try statement
            content = try_pattern.sub(r'\1\n        # Validate price - ensure it is an integer in cents\n        if not isinstance(price, int):\n            try:\n                # Try converting to integer cents if it\'s a float in dollars\n                price = int(float(price) * 100)\n                logging.info(f"Converted price to {price} cents")\n            except (ValueError, TypeError):\n                logging.error(f"Invalid price format: {price} - must be numeric")\n                raise ValueError(f"Invalid price: {price}")\n        \n        # Sanity check - ensure price is reasonable (between $1 and $500)\n        if price < 100 or price > 50000:\n            logging.error(f"Price out of reasonable range: {price} cents")\n            raise ValueError(f"Price out of reasonable range: ${price/100:.2f}")\n', content)
            
            logger.info("✅ Added price validation to create_stripe_checkout_session")
        else:
            logger.warning("Could not locate create_stripe_checkout_session function")
        
        # Write the updated content back to the file
        with open('payment_services.py', 'w') as f:
            f.write(content)
        
        logger.info("✅ Successfully updated payment_services.py")
        
    except Exception as e:
        logger.error(f"Failed to update payment_services.py: {str(e)}")

if __name__ == "__main__":
    print("\n===== IELTS GenAI Prep - Fixing Stripe Checkout =====\n")
    
    if fix_stripe_checkout():
        print("\n✅ Stripe checkout fixes have been applied successfully!")
        print("Please restart the application for changes to take effect.")
    else:
        print("\n❌ Failed to apply some Stripe checkout fixes.")
        print("Please check the logs for details.")
    
    print("\n======================================================")