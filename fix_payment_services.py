"""
Fix Payment Services Script
This script fixes syntax errors in the payment_services.py file.
"""
import re
import os

def fix_payment_services():
    """Fix syntax errors in payment_services.py file."""
    try:
        # Read the current content
        with open('payment_services.py', 'r') as f:
            content = f.read()
        
        # Fix automatic_payment_methods in create_stripe_checkout_session
        content = re.sub(
            r"'payment_method_types': payment_methods,\s*'automatic_payment_methods': \{'enabled': True\},",
            "'payment_method_types': payment_methods,\n            # 'automatic_payment_methods': {'enabled': True},  # Removed - not supported",
            content
        )
        
        # Fix automatic_payment_methods in speaking checkout
        content = re.sub(
            r"'payment_method_types': payment_method_types,\s*'automatic_payment_methods': \{'enabled': True\},",
            "'payment_method_types': payment_method_types,\n            # 'automatic_payment_methods': {'enabled': True},  # Removed - not supported",
            content
        )
        
        # Write the corrected content back
        with open('payment_services.py', 'w') as f:
            f.write(content)
            
        print("✅ Successfully fixed payment_services.py")
        return True
    except Exception as e:
        print(f"❌ Error fixing payment_services.py: {str(e)}")
        return False

if __name__ == "__main__":
    success = fix_payment_services()
    if success:
        print("You can now restart the application.")
    else:
        print("Please check the file manually.")