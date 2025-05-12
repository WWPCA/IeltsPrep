"""
Stripe Buy Button Integration Module

This module provides configuration and utility functions for integrating
Stripe Buy Buttons into the IELTS AI Prep platform.

Buy Buttons are a no-code solution provided by Stripe that simplify the checkout process
and reduce maintenance overhead compared to custom checkout implementations.
"""

# Buy Button IDs for Academic Products
ACADEMIC_BUTTONS = {
    'single': 'buy_btn_1ABCxyzExampleID123',  # Replace with your actual button ID
    'double': 'buy_btn_2ABCxyzExampleID456',  # Replace with your actual button ID
    'pack': 'buy_btn_3ABCxyzExampleID789',    # Replace with your actual button ID
    'writing': 'buy_btn_4ABCxyzExampleID012', # Replace with your actual button ID
    'speaking': 'buy_btn_5ABCxyzExampleID345' # Replace with your actual button ID
}

# Buy Button IDs for General Training Products
GENERAL_BUTTONS = {
    'single': 'buy_btn_6ABCxyzExampleID678',  # Replace with your actual button ID
    'double': 'buy_btn_7ABCxyzExampleID901',  # Replace with your actual button ID
    'pack': 'buy_btn_8ABCxyzExampleID234',    # Replace with your actual button ID
    'writing': 'buy_btn_9ABCxyzExampleID567', # Replace with your actual button ID
    'speaking': 'buy_btn_0ABCxyzExampleID890' # Replace with your actual button ID
}

# Get Stripe Publishable Key from environment
import os

# Stripe Publishable Key
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY', '')  # Get from environment

def get_button_id(test_type, product_type):
    """
    Get the Buy Button ID for a specific test type and product type.
    
    Args:
        test_type (str): 'academic' or 'general'
        product_type (str): 'single', 'double', 'pack', 'writing', or 'speaking'
        
    Returns:
        str: Button ID for the specified product
    """
    if test_type.lower() == 'academic':
        return ACADEMIC_BUTTONS.get(product_type.lower(), '')
    elif test_type.lower() == 'general':
        return GENERAL_BUTTONS.get(product_type.lower(), '')
    else:
        return ''

def is_buy_button_configured():
    """
    Check if at least one buy button is configured with a valid ID.
    
    Returns:
        bool: True if at least one button is configured, False otherwise
    """
    # Check if any button has a non-default ID
    for button_id in list(ACADEMIC_BUTTONS.values()) + list(GENERAL_BUTTONS.values()):
        if not button_id.startswith('buy_btn_'):
            return True
    
    return False

def get_setup_instructions():
    """
    Get comprehensive instructions for setting up Stripe Buy Buttons.
    
    Returns:
        str: Setup instructions including address collection
    """
    return """
    To complete the Stripe Buy Button integration, follow these steps:
    
    1. Create Payment Links in Stripe Dashboard:
       a. Go to Stripe Dashboard → Products → Create Product for each package
       b. For each product, create a Payment Link
       c. In the Payment Link settings, under "Customer information":
          - Enable "Collect shipping address"
          - Enable "Collect billing address" 
          - These settings ensure tax calculation and compliance
          
    2. Create Buy Buttons for each Payment Link:
       a. In the Payment Link page, click "Share" and select "Buy button"
       b. Customize the button appearance if needed
       c. Copy the Button ID and update the IDs in this file
       
    3. Set up webhooks to process successful payments:
       a. Go to Stripe Dashboard → Developers → Webhooks
       b. Add an endpoint for your domain: https://your-domain.com/webhooks/stripe
       c. Select these events: checkout.session.completed, payment_intent.succeeded
       d. Copy the signing secret and add it to your environment variables as STRIPE_WEBHOOK_SECRET
    
    This ensures your application will properly collect customer addresses and receive 
    notifications when payments are successful.
    """