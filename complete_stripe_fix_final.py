"""
Complete fix for Stripe checkout issues.
This script fixes price display issues ($5,000 instead of $50)
and enables wallet payment methods (Apple Pay and Google Pay) in the checkout.
"""
import os
import re

def complete_stripe_fix():
    """Fix all Stripe checkout issues."""
    print("Starting comprehensive Stripe checkout fix...")
    
    # 1. Ensure prices are handled consistently - stored in dollars, converted to cents for Stripe
    fix_price_format_in_cart()
    
    # 2. Enable Apple Pay and Google Pay through automatic payment methods
    enable_wallet_payment_methods()
    
    # 3. Fix debug logging for better troubleshooting
    fix_debug_logging()
    
    print("\nFix complete! Stripe checkout should now:")
    print("1. Show the correct price ($50.00 for 2 products)")
    print("2. Enable Apple Pay and Google Pay options when available")
    print("3. Provide clearer debug logging for troubleshooting")
    print("\nNOTE: Apple Pay and Google Pay will only show on supported browsers/devices.")
    print("They won't appear in Replit's preview window but will work on real devices.")
    
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
        print(f"Error fixing cart.py: {str(e)}")
    
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
        
        with open('payment_services.py', 'w') as f:
            f.write(content)
    except Exception as e:
        print(f"Error enabling wallet payment methods: {str(e)}")
    
def fix_debug_logging():
    """Fix debug logging in cart_routes.py."""
    print("\nFixing debug logging in cart_routes.py...")
    
    try:
        with open('cart_routes.py', 'r') as f:
            content = f.read()
        
        # Remove any hardcoded price forcing
        if "total_price = 5000" in content:
            content = re.sub(
                r"\s+# Force the amount to be \$50 for testing.*\n\s+total_price = 5000.*\n",
                "\n",
                content
            )
            print("✓ Removed hardcoded price forcing")
        
        # Update debug log message
        if "print(f\"Cart total: ${cart_total} -> Stripe amount: {total_price} cents" in content:
            content = re.sub(
                r"print\(f\"Cart total: \${cart_total} -> Stripe amount: {total_price} cents.*\"\)",
                "print(f\"Cart total: ${cart_total} -> Stripe amount: {total_price} cents (${cart_total:.2f})\")",
                content
            )
            print("✓ Fixed debug log message for better clarity")
        
        with open('cart_routes.py', 'w') as f:
            f.write(content)
    except Exception as e:
        print(f"Error fixing debug logging: {str(e)}")

if __name__ == "__main__":
    complete_stripe_fix()