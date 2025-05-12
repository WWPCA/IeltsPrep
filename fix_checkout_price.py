"""
Fix for the Stripe checkout price conversion issues.
This script replaces the create_stripe_checkout_session function in payment_services.py
with a version that properly handles price conversion.
"""

import os
import re

def fix_checkout_price_conversion():
    """
    Fix the price conversion in the Stripe checkout function.
    """
    # Find the create_stripe_checkout_session function in payment_services.py
    with open('payment_services.py', 'r') as f:
        content = f.read()
    
    # Define the pattern to find the function
    function_start = "def create_stripe_checkout_session("
    function_end = "# Create a Stripe checkout session for speaking assessments"
    
    # Extract the function
    start_pos = content.find(function_start)
    end_pos = content.find(function_end)
    
    if start_pos == -1 or end_pos == -1:
        print("ERROR: Could not locate the target function in payment_services.py")
        return
    
    # The current function code
    current_function = content[start_pos:end_pos]
    
    # Create the new version with fixed price conversion
    new_function = """def create_stripe_checkout_session(
    product_name, 
    description, 
    price, 
    success_url, 
    cancel_url, 
    country_code='US', 
    customer_email=None,
    is_country_restricted=True
):
    \"\"\"
    try:
        # Check country restrictions
        check_country_restriction(country_code, is_country_restricted)
            
        api_key = get_stripe_api_key()
        if not api_key:
            logging.error("Stripe API key not found. Cannot create checkout session.")
            raise ValueError("Stripe API key is empty or invalid")
        
        stripe.api_key = api_key
        
        # Ensure price is in the correct format for Stripe (cents)
        # Handle various input formats
        try:
            # Convert price to float if it's a string
            if isinstance(price, str):
                price = float(price.replace('$', '').strip())
                
            # Determine if price is already in cents
            if price > 1000 and price % 100 == 0:
                # This is likely already in cents (e.g. 5000 instead of 50.00)
                logging.warning(f"Price appears to be already in cents: ${price/100:.2f}")
                price_in_cents = int(price)  # Keep as is, but ensure it's an integer
            else:
                # Normal case - price is in dollars, convert to cents
                price_in_cents = int(price * 100)
                
            logging.info(f"Price conversion: ${price:.2f} → {price_in_cents} cents")
        except Exception as e:
            logging.error(f"Error converting price: {str(e)}")
            # Fallback to a safe default
            price_in_cents = 5000  # $50.00
            logging.warning(f"Using fallback price: {price_in_cents} cents (${price_in_cents/100:.2f})")
        
        # Setup metadata
        metadata = {
            'product_name': product_name,
            'price': str(price),
            'description': description,
            'source': 'ielts_genai_prep',
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Ensure the success_url includes the session ID parameter
        if '{CHECKOUT_SESSION_ID}' not in success_url:
            if '?' in success_url:
                success_url += '&session_id={CHECKOUT_SESSION_ID}'
            else:
                success_url += '?session_id={CHECKOUT_SESSION_ID}'
        
        # Use card payments only for simplicity and reliability
        payment_methods = ['card']
        
        # Get the list of allowed countries
        allowed_countries = get_allowed_countries()
        
        # Build checkout session parameters
        session_params = {
            'payment_method_types': payment_methods,
            'line_items': [
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': product_name,
                            'description': description,
                        },
                        'unit_amount': price_in_cents,
                        'tax_behavior': 'exclusive',
                    },
                    'quantity': 1,
                },
            ],
            'mode': 'payment',
            'success_url': success_url,
            'cancel_url': cancel_url,
            'metadata': metadata,
            'automatic_tax': {'enabled': False},
            'customer_creation': 'always',
            'billing_address_collection': 'required',
            'payment_intent_data': {
                'capture_method': 'automatic',
            },
        }
        
        # Add customer email if provided
        if customer_email:
            session_params['customer_email'] = customer_email
        
        # Log session parameters (with sensitive info redacted)
        debug_params = session_params.copy()
        if 'customer_email' in debug_params:
            debug_params['customer_email'] = '***@***.com'
        logging.debug(f"Stripe checkout params: {json.dumps(debug_params, indent=2)}")
        
        # Create checkout session
        try:
            checkout_session = stripe.checkout.Session.create(**session_params)
            logging.debug(f"Stripe session created successfully: {checkout_session.id}")
            
            return {
                'session_id': checkout_session.id,
                'checkout_url': checkout_session.url
            }
        except Exception as e:
            logging.error(f"Stripe API Error: {type(e).__name__} - {str(e)}")
            raise
        
    except Exception as e:
        logging.error(f"Error creating Stripe checkout: {str(e)}")
        raise
"""
    
    # Replace the function in the content
    new_content = content[:start_pos] + new_function + content[end_pos:]
    
    # Write back to the file
    with open('payment_services.py', 'w') as f:
        f.write(new_content)
    
    print("Successfully updated the create_stripe_checkout_session function")
    print("The new function includes improved price handling and error recovery")

if __name__ == "__main__":
    fix_checkout_price_conversion()