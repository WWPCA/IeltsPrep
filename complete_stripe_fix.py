"""
Complete fix for Stripe checkout to use only card payments and allow Apple Pay/Google Pay
to be managed through the Stripe Dashboard instead of our code.

This script:
1. Removes all region-specific payment methods
2. Updates the payment_services.py file to only use 'card' payment method
3. Disables the get_country_payment_methods function to prevent additional method injection
"""

def complete_stripe_fix():
    """Apply a comprehensive fix to Stripe checkout configuration."""
    
    print("Applying comprehensive fix to Stripe checkout...")
    
    # Read the payment_services.py file
    with open('payment_services.py', 'r') as f:
        content = f.read()
    
    # 1. Replace the get_country_payment_methods function to always return an empty list
    old_function = """def get_country_payment_methods(country_code):
    """
    Get the list of supported payment methods for a given country.
    
    Args:
        country_code (str): Two-letter country code
        
    Returns:
        list: Supported payment methods for the country
    """
    if not country_code:
        return []
        
    country_code = country_code.upper()
    
    if country_code in REGION_PAYMENT_MAPPING:
        return REGION_PAYMENT_MAPPING[country_code]
    
    return []"""
    
    new_function = """def get_country_payment_methods(country_code):
    """
    Get the list of supported payment methods for a given country.
    
    Note: This function has been disabled to fix Stripe checkout issues.
    All payment methods are now managed through the Stripe Dashboard.
    
    Args:
        country_code (str): Two-letter country code
        
    Returns:
        list: Empty list - all payment methods are now managed in Stripe Dashboard
    """
    # Return empty list - payment methods are managed in Stripe Dashboard
    return []"""
    
    modified_content = content.replace(old_function, new_function)
    
    # 2. Update all payment_method_types references to only use 'card'
    # This is simpler than trying to replace specific sections and ensures consistency
    
    # A. Handle create_stripe_checkout_session
    create_checkout_start = "def create_stripe_checkout_session"
    create_checkout_end = "return {"
    
    create_checkout_section = content[content.find(create_checkout_start):content.find(create_checkout_end)]
    
    # Find payment methods section
    old_payment_section = """        # Determine payment method types based on country
        payment_methods = ['card']  # Wallets are now enabled through Stripe dashboard
        if country_code:
            additional_methods = get_country_payment_methods(country_code)
            if additional_methods:
                payment_methods.extend(additional_methods)"""
    
    new_payment_section = """        # Simplified payment methods - use only card for compatibility
        # Wallet payment methods (Apple Pay, Google Pay) are managed through the Stripe Dashboard
        payment_methods = ['card']  # Do not modify this line"""
    
    # Replace in the create_checkout_section first
    modified_create_checkout = create_checkout_section.replace(old_payment_section, new_payment_section)
    
    # Then replace the entire section in the full content
    modified_content = modified_content.replace(create_checkout_section, modified_create_checkout)
    
    # B. Handle create_subscription_checkout
    subscription_checkout_start = "def create_subscription_checkout"
    subscription_checkout_end = "checkout_session ="
    
    subscription_section = content[content.find(subscription_checkout_start):content.find(subscription_checkout_end)]
    
    old_payment_section_subscription = """        # Use card payments plus popular digital wallets
        payment_method_types = ['card']  # Wallets are now enabled through Stripe dashboard
        
        # Note: Apple Pay and Google Pay are enabled globally where supported by the browser
        # These are presented automatically by Stripe when the browser/device supports them"""
    
    new_payment_section_subscription = """        # Simplified payment methods - use only card for compatibility
        # Wallet payment methods (Apple Pay, Google Pay) are managed through the Stripe Dashboard
        payment_method_types = ['card']  # Do not modify this line"""
    
    # Replace in the subscription section 
    modified_subscription = subscription_section.replace(old_payment_section_subscription, new_payment_section_subscription)
    
    # Then replace the entire section in the full content
    modified_content = modified_content.replace(subscription_section, modified_subscription)
    
    # Write the modified file
    with open('payment_services.py', 'w') as f:
        f.write(modified_content)
    
    print("Stripe checkout fix applied successfully.")
    print("Payment method is now simplified to 'card' only.")
    print("Apple Pay and Google Pay should be managed through the Stripe Dashboard.")

if __name__ == "__main__":
    complete_stripe_fix()