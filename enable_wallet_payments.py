"""
Enable Apple Pay and Google Pay wallet payment options in Stripe checkout.
This script updates the payment_services.py file to explicitly include support
for these popular wallet payment methods.
"""

def enable_wallet_payments():
    """Enable Apple Pay and Google Pay in Stripe checkout."""
    
    print("Enabling wallet payment methods (Apple Pay, Google Pay)...")
    
    with open('payment_services.py', 'r') as f:
        content = f.read()
    
    # 1. Update payment method types to include wallet options
    old_payment_types = "payment_method_types = ['card']  # Keep simple to avoid errors"
    new_payment_types = "payment_method_types = ['card', 'wallet']  # Include wallet payments like Apple Pay and Google Pay"
    
    if old_payment_types in content:
        content = content.replace(old_payment_types, new_payment_types)
    
    # 2. Update payment session params to include automatic_payment_methods
    payment_session_params = """        session_params = {
            'payment_method_types': payment_method_types,"""
            
    updated_session_params = """        # Enable automatic payment methods to detect and enable Apple Pay, Google Pay, etc.
        session_params = {
            'payment_method_types': payment_method_types,
            'automatic_payment_methods': {'enabled': True},"""
    
    if payment_session_params in content:
        content = content.replace(payment_session_params, updated_session_params)
    
    # 3. Add comment to clarify wallet payments
    old_comment = """# This function provides basic payment methods.
    Wallet options like Apple Pay and Google Pay are enabled through the Stripe Dashboard."""
    
    new_comment = """# This function provides payment methods including wallet options.
    Apple Pay and Google Pay will automatically appear when supported by the user's device."""
    
    if old_comment in content:
        content = content.replace(old_comment, new_comment)
    
    with open('payment_services.py', 'w') as f:
        f.write(content)
    
    print("Wallet payment methods enabled!")
    print("Important notes:")
    print("1. Apple Pay and Google Pay will only appear on compatible devices/browsers")
    print("2. These payment methods won't be visible in the Replit preview")
    print("3. You must have them enabled in your Stripe Dashboard settings")
    print("4. The customer must be using a device that supports these payment methods")

if __name__ == "__main__":
    enable_wallet_payments()