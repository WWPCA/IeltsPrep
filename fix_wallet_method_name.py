"""
Fix the wallet payment method name to use proper format for Stripe.
"""

def fix_wallet_method_name():
    """Fix the wallet payment method name to match Stripe's expected format."""
    
    print("Fixing wallet payment method name...")
    
    with open('payment_services.py', 'r') as f:
        content = f.read()
    
    # Fix the payment method type - 'wallet' is not valid for Stripe
    old_payment_type = "payment_method_types = ['card', 'wallet']"
    new_payment_type = "payment_method_types = ['card']  # We use automatic_payment_methods instead of listing wallet options"
    
    if old_payment_type in content:
        content = content.replace(old_payment_type, new_payment_type)
    
    # Make sure we're using automatic payment methods correctly
    # This is the preferred way to enable Apple Pay and Google Pay in Stripe
    if "'automatic_payment_methods': {'enabled': True}" in content:
        print("Automatic payment methods already enabled correctly")
    else:
        # Add automatic payment methods to session parameters
        session_param_pattern = "        session_params = {"
        session_param_replacement = "        session_params = {\n            'automatic_payment_methods': {'enabled': True},"
        
        if session_param_pattern in content:
            content = content.replace(session_param_pattern, session_param_replacement)
            print("Added automatic_payment_methods to session parameters")
    
    with open('payment_services.py', 'w') as f:
        f.write(content)
    
    print("Wallet payment method name fixed!")
    print("Using Stripe's recommended 'automatic_payment_methods' setting.")
    print("This will enable Apple Pay and Google Pay automatically when supported.")

if __name__ == "__main__":
    fix_wallet_method_name()