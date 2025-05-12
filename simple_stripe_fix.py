"""
Simple fix for the Stripe checkout to only use card payment method.
This script makes direct edits to the payment_services.py file.
"""
import re

def simple_stripe_fix():
    """Fix the Stripe checkout process by limiting to card payments only."""
    
    print("Applying simple fix to Stripe checkout...")
    
    # Read the payment_services.py file
    with open('payment_services.py', 'r') as f:
        content = f.read()
    
    # 1. First, update the create_stripe_checkout_session function
    # Find and replace the payment_methods section
    pattern1 = r"# Determine payment method types based on country\s+payment_methods = \['card'\].+?if additional_methods:\s+payment_methods\.extend\(additional_methods\)"
    replacement1 = "# Use only card payments for universal compatibility\n        payment_methods = ['card']  # Wallets managed through Stripe Dashboard"
    
    content = re.sub(pattern1, replacement1, content, flags=re.DOTALL)
    
    # 2. Replace all occurrences of payment_method_types that might include more than 'card'
    pattern2 = r"payment_method_types = \['card'.*?\]"
    replacement2 = "payment_method_types = ['card']  # Wallets managed through Stripe Dashboard"
    
    content = re.sub(pattern2, replacement2, content)
    
    # 3. Override the get_country_payment_methods function to always return an empty list
    pattern3 = r"def get_country_payment_methods\(country_code\):.*?return \[\]"
    replacement3 = """def get_country_payment_methods(country_code):
    \"\"\"
    This function has been disabled to fix Stripe checkout issues.
    All payment methods are now managed through the Stripe Dashboard.
    \"\"\"
    # Always return empty list to prevent additional payment methods
    return []"""
    
    content = re.sub(pattern3, replacement3, content, flags=re.DOTALL)
    
    # Write the modified file
    with open('payment_services.py', 'w') as f:
        f.write(content)
    
    print("Stripe checkout fix applied successfully.")
    print("Payment method is now simplified to 'card' only.")
    print("Apple Pay and Google Pay should be managed through the Stripe Dashboard.")

if __name__ == "__main__":
    simple_stripe_fix()