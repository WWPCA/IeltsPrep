"""
Add Apple Pay and Google Pay to the Stripe checkout options.
This script updates the payment_services.py file to include these popular wallet payment options.
"""

def add_wallet_payment_methods():
    """Add Apple Pay and Google Pay to the payment options."""
    
    print("Adding Apple Pay and Google Pay to Stripe checkout options...")
    
    # Read the payment_services.py file
    with open('payment_services.py', 'r') as f:
        content = f.read()
    
    # Update the payment methods in the create_stripe_checkout_session function
    old_code = """        # Simplify payment methods to only use card payments (universally supported)
        payment_method_types = ['card']
        
        # Note: We've removed the complex region mapping to fix the Stripe checkout error
        # If region-specific payment methods are needed in the future, ensure they're 
        # approved by Stripe and match their supported payment method types."""
    
    new_code = """        # Use card payments plus popular digital wallets
        payment_method_types = ['card', 'apple_pay', 'google_pay']
        
        # Note: Apple Pay and Google Pay are enabled globally where supported by the browser
        # These are presented automatically by Stripe when the browser/device supports them"""
    
    # Replace the code in both places in the file
    modified_content = content.replace(old_code, new_code)
    
    # Update the payment methods in the direct function code too
    old_payment_methods = """        # Determine payment method types based on country
        payment_methods = ['card']"""
    
    new_payment_methods = """        # Determine payment method types based on country
        payment_methods = ['card', 'apple_pay', 'google_pay']"""
    
    modified_content = modified_content.replace(old_payment_methods, new_payment_methods)
    
    # Write the modified file
    with open('payment_services.py', 'w') as f:
        f.write(modified_content)
    
    print("Wallet payment methods added successfully.")
    print("Stripe checkout now includes Apple Pay and Google Pay where supported by the device.")

if __name__ == "__main__":
    add_wallet_payment_methods()