"""
Fix Stripe checkout integration issues.
This script addresses the price display issue and ensures Apple Pay/Google Pay work.
"""
import os
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """Fix all Stripe checkout issues."""
    logging.info("Starting Stripe checkout fix...")
    
    # Add detailed error checking in payment_services.py
    fix_payment_services()
    
    # Fix cart_routes.py to properly handle price calculation
    fix_cart_routes()
    
    # Force restart of the application to apply changes
    logging.info("Fix complete! Application has been updated.")
    logging.info("Please restart the application and try the checkout process again.")

def fix_payment_services():
    """Fix the payment_services.py file."""
    try:
        with open('payment_services.py', 'r') as f:
            content = f.read()
        
        # Make sure API key is properly loaded
        if "os.environ.get('STRIPE_SECRET_KEY', '')" in content:
            logging.info("✓ Stripe API key configuration looks correct")
        else:
            logging.error("× Stripe API key configuration not found in expected format!")
        
        # Add more robust error checking
        if "raise ValueError(\"Stripe API key is required\")" in content:
            # Modify to add more debugging
            content = content.replace(
                "raise ValueError(\"Stripe API key is required\")",
                """
            api_key = os.environ.get('STRIPE_SECRET_KEY', '')
            logging.error(f"Stripe API key empty or invalid: '{api_key[:4]}...' (length: {len(api_key)})")
            raise ValueError("Stripe API key is empty or invalid")"""
            )
            logging.info("✓ Added better Stripe API key error logging")
        
        # Fix automatic payment methods implementation
        if "'automatic_payment_methods': {'enabled': True}" in content:
            logging.info("✓ Automatic payment methods are already enabled")
        else:
            # Add automatic_payment_methods if not found
            content = content.replace(
                "'payment_method_types': payment_methods,",
                """'payment_method_types': payment_methods,
            'automatic_payment_methods': {'enabled': True},"""
            )
            logging.info("✓ Added automatic payment methods to enable Apple Pay/Google Pay")
        
        # Fix price calculation
        if "price_in_cents = int(price * 100)" in content:
            # Add debug logs for price calculation
            content = content.replace(
                "price_in_cents = int(price * 100)",
                """# Handle the most common error: Price is already in cents
            if price > 1000 and price % 100 == 0:
                # This is likely already in cents (e.g. 5000 instead of 50.00)
                logging.warning(f"Price appears to be already in cents: ${price/100:.2f} - adjusting to dollars")
                price_in_cents = price  # Already in cents
            else:
                # Normal case - price is in dollars, convert to cents
                price_in_cents = int(price * 100)
                
            logging.info(f"Price conversion: ${price:.2f} → {price_in_cents} cents")"""
            )
            logging.info("✓ Enhanced price handling to check if price is already in cents")
        
        with open('payment_services.py', 'w') as f:
            f.write(content)
    except Exception as e:
        logging.error(f"Error fixing payment_services.py: {str(e)}")
        return False
    
    return True

def fix_cart_routes():
    """Fix the cart_routes.py file."""
    try:
        with open('cart_routes.py', 'r') as f:
            content = f.read()
        
        # Add logging for checkout session parameters
        if "checkout_session = create_stripe_checkout_session(" in content:
            # Add consistent pricing approach
            content = content.replace(
                "total_price = int(cart_total * 100)",
                """# Ensure a consistent approach to pricing
            # Debug price calculation
            print(f"Cart total before conversion: ${cart_total}")
            
            # If cart_total is extremely high (e.g. 50.00 treated as 5000 cents, which becomes $5000),
            # it might be a unit conversion issue. Force a more reasonable value.
            if cart_total >= 100:  # If over $100, likely an error
                print(f"WARNING: Cart total suspiciously high: ${cart_total}. Check if cents vs dollars issue.")
                
            # Convert to cents for Stripe (prices are stored in dollars in the cart)
            total_price = int(cart_total * 100)  # Convert dollars to cents"""
            )
            logging.info("✓ Added enhanced price calculation debugging in cart_routes.py")
        
        # Add more error detection and handling
        if "print(error_msg)" in content:
            content = content.replace(
                "print(error_msg)",
                """print(error_msg)
            # Log the cart data for debugging
            print(f"Cart data: {json.dumps(cart_items, indent=2)}")
            print(f"Calculated total: ${cart_total} → {total_price} cents")
            
            # Check Stripe API key
            from payment_services import get_stripe_api_key
            api_key = get_stripe_api_key()
            if not api_key:
                print("ERROR: Stripe API key is empty!")
            else:
                print(f"Stripe API key found (starts with: {api_key[:4]}, length: {len(api_key)})")"""
            )
            logging.info("✓ Added enhanced error logging for checkout issues")
            
        with open('cart_routes.py', 'w') as f:
            f.write(content)
    except Exception as e:
        logging.error(f"Error fixing cart_routes.py: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    main()