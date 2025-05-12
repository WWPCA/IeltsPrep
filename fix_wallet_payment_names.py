"""
Fix payment method names for Apple Pay and Google Pay to match Stripe's expected format.
"""

def fix_wallet_payment_names():
    """Fix payment method names to match Stripe's requirements."""
    
    print("Fixing wallet payment method names...")
    
    # Read the payment_services.py file
    with open('payment_services.py', 'r') as f:
        content = f.read()
    
    # The current implementation uses 'apple_pay' and 'google_pay' 
    # but Stripe actually expects them as specific format
    incorrect_names = """payment_method_types = ['card', 'apple_pay', 'google_pay']"""
    correct_names = """payment_method_types = ['card']  # Wallets are now enabled through Stripe dashboard"""
    
    # Replace the incorrect names with the correct ones
    modified_content = content.replace(incorrect_names, correct_names)
    
    # Update the other occurrence as well
    old_payment_methods = """        # Determine payment method types based on country
        payment_methods = ['card', 'apple_pay', 'google_pay']"""
    
    new_payment_methods = """        # Determine payment method types based on country
        payment_methods = ['card']  # Wallets are now enabled through Stripe dashboard"""
    
    modified_content = modified_content.replace(old_payment_methods, new_payment_methods)
    
    # Write the modified file
    with open('payment_services.py', 'w') as f:
        f.write(modified_content)
    
    print("Wallet payment method names fixed successfully.")
    print("Note: Apple Pay and Google Pay should be enabled in your Stripe Dashboard.")
    print("They will appear automatically on supported devices/browsers.")

if __name__ == "__main__":
    fix_wallet_payment_names()