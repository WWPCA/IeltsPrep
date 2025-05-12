"""
Debug script for Stripe checkout functionality.
This script creates a test checkout session and prints debugging information.
"""

import os
import stripe
import logging

logging.basicConfig(level=logging.DEBUG)

def debug_stripe_checkout():
    """
    Create a test checkout session and print debugging information.
    """
    try:
        # Get Stripe API key
        stripe_api_key = os.environ.get('STRIPE_SECRET_KEY')
        
        if not stripe_api_key:
            print("ERROR: Stripe API key not found")
            return
            
        print(f"Stripe API key found (starts with: {stripe_api_key[:4]}..., length: {len(stripe_api_key)})")
        
        # Set API key
        stripe.api_key = stripe_api_key
        
        # Test product info
        price = 50.00  # $50.00
        product_name = "IELTS Test Package"
        description = "Complete IELTS Assessment Package"
        
        # Convert to cents for Stripe
        print(f"Original price: ${price:.2f}")
        
        # Fix for the cents conversion issue
        if price > 1000 and price % 100 == 0:
            print(f"Price appears to be already in cents: ${price/100:.2f} - using as is")
            price_in_cents = price  # Already in cents
        else:
            price_in_cents = int(price * 100)
            print(f"Converted price: ${price:.2f} → {price_in_cents} cents")
        
        # Print key parameters
        print(f"Price in cents: {price_in_cents}")
        print(f"Product name: {product_name}")
        print(f"Description: {description}")
            
        # Create checkout session
        print("Creating checkout session...")
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': product_name,
                        'description': description,
                    },
                    'unit_amount': price_in_cents,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='https://example.com/success',
            cancel_url='https://example.com/cancel',
        )
            
        # Print session info
        print(f"Session created successfully!")
        print(f"Session ID: {session.id}")
        print(f"Checkout URL: {session.url}")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    debug_stripe_checkout()