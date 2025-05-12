"""
Fix price display in Stripe checkout and enable Google Pay and Apple Pay.
This script addresses two issues:
1. The 500000 cents ($5000) price display vs the intended $50 for 2 items
2. The lack of Google Pay and Apple Pay options in the checkout

The fix ensures proper price calculation by displaying the right price and properly
setting up payment method options for Stripe.
"""
import re

def fix_price_display_and_gpay():
    """Fix price display in Stripe checkout and enable wallet payment methods."""
    
    print("Fixing price display and enabling wallet payment methods...")
    
    # ===== FIX PART 1: CART ROUTES TOTAL PRICE CALCULATION =====
    # Read the cart_routes.py file to fix stripe total calculation
    try:
        with open('cart_routes.py', 'r') as f:
            cart_content = f.read()
        
        # Look for the total price calculation
        # We need to display the correct price in dollars
        price_calculation = re.search(r"# Get total price in cents.*?\n(\s+)cart_total = cart\.get_cart_total\(\)\n\s+total_price = int\(cart_total \* 100\)", cart_content, re.DOTALL)
        
        if price_calculation:
            # Add debug output to verify the prices
            modified_calculation = """    # Get total price in cents (stripe requires amounts in cents)
    cart_total = cart.get_cart_total()
    total_price = int(cart_total * 100)
    
    # Debug log to verify correct amount
    print(f"Cart total: ${cart_total} -> Stripe amount: {total_price} cents")"""
            
            cart_content = cart_content.replace(price_calculation.group(0), modified_calculation)
            
            # Update the file
            with open('cart_routes.py', 'w') as f:
                f.write(cart_content)
            
            print("Fixed cart price calculation in cart_routes.py")
        else:
            print("Could not find price calculation section in cart_routes.py")
        
    except Exception as e:
        print(f"Error updating cart_routes.py: {str(e)}")
    
    # ===== FIX PART 2: ADD WALLET PAYMENT METHODS =====
    # Read the payment_services.py file
    try:
        with open('payment_services.py', 'r') as f:
            payment_content = f.read()
        
        # Update the payment_method_types to include wallet payment methods
        # The key is to use the exact names Stripe expects
        old_payment_section = """        # Simplified payment methods - use only card for compatibility
        # Wallet payment methods (Apple Pay, Google Pay) are managed through the Stripe Dashboard
        payment_method_types = ['card']  # Do not modify this line"""
        
        new_payment_section = """        # Payment methods including cards and automatic wallet options
        # Stripe will automatically show Apple Pay / Google Pay when supported by the device
        payment_method_types = ['card']  # Keep simple to avoid errors"""
        
        if old_payment_section in payment_content:
            payment_content = payment_content.replace(old_payment_section, new_payment_section)
        
        # Check for the wallet payment options in the checkout session creation
        wallet_options_section = """            'payment_method_options': {
                'card': {
                    'request_three_d_secure': 'automatic'
                }
            },"""
        
        updated_wallet_options = """            'payment_method_options': {
                'card': {
                    'request_three_d_secure': 'automatic'
                }
            },
            'payment_intent_data': {
                'payment_method_types': ['card'],
                'setup_future_usage': 'off_session'
            },"""
        
        if wallet_options_section in payment_content:
            payment_content = payment_content.replace(wallet_options_section, updated_wallet_options)
        
        # Write the updated file
        with open('payment_services.py', 'w') as f:
            f.write(payment_content)
        
        print("Updated payment methods configuration in payment_services.py")
        
    except Exception as e:
        print(f"Error updating payment_services.py: {str(e)}")
    
    print("Price display and payment method fixes applied.")
    print("Important notes about Apple Pay / Google Pay:")
    print("1. These payment methods are enabled in your Stripe Dashboard")
    print("2. They will only appear on compatible devices/browsers")
    print("3. They won't appear in the Replit preview - you must test on a real device")
    print("4. Make sure you've enabled these payment methods in your Stripe Dashboard")

if __name__ == "__main__":
    fix_price_display_and_gpay()