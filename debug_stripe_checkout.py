"""
Debug script for Stripe checkout integration.
This script verifies the checkout process works correctly.
"""

import os
import json
import stripe
import logging
from flask import url_for, session
from urllib.parse import urlparse, parse_qs

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_stripe_checkout():
    """
    Test and debug the Stripe checkout integration.
    """
    logger.info("Starting Stripe checkout debugging...")
    
    # 1. Verify Stripe API key is available and set correctly
    stripe_key = os.environ.get('STRIPE_SECRET_KEY')
    
    if not stripe_key:
        logger.error("❌ Stripe API key not found in environment variables!")
        return False
    
    logger.info(f"✅ Found Stripe API key (starts with: {stripe_key[:4]}..., length: {len(stripe_key)})")
    stripe.api_key = stripe_key
    
    # 2. Try creating a test checkout session directly with Stripe
    try:
        # Create a direct test checkout session with minimal parameters
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'IELTS GenAI Prep - Debug Test',
                    },
                    'unit_amount': 2500,  # $25.00 in cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='http://example.com/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='http://example.com/cancel',
        )
        
        logger.info(f"✅ Direct Stripe checkout created successfully! Session ID: {checkout_session.id}")
        logger.info(f"✅ Checkout URL: {checkout_session.url}")
        
        # 3. Verify important fields in the response
        checkout_url = checkout_session.url
        parsed_url = urlparse(checkout_url)
        
        logger.info(f"✅ Checkout domain: {parsed_url.netloc}")
        
        # Get checkout session to verify price data
        retrieved_session = stripe.checkout.Session.retrieve(checkout_session.id)
        
        # The amount in the line item should be in the retrieved session
        line_items = stripe.checkout.Session.list_line_items(checkout_session.id)
        
        if line_items.data:
            logger.info(f"✅ Line item count: {len(line_items.data)}")
            first_item = line_items.data[0]
            logger.info(f"✅ Line item amount: ${first_item.amount_total/100:.2f} ({first_item.amount_total} cents)")
            
            # Verify price matches what we expect
            if first_item.amount_total == 2500:
                logger.info("✅ Price matches expected value ($25.00)")
            else:
                logger.error(f"❌ Price does not match expected value! Expected: 2500 cents, Got: {first_item.amount_total} cents")
        else:
            logger.error("❌ No line items found in the checkout session")
        
        # 4. Check payment methods available
        logger.info(f"✅ Payment method types: {checkout_session.payment_method_types}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error creating test checkout: {type(e).__name__}: {str(e)}")
        return False

def verify_currency_handling():
    """
    Verify that currency handling is consistent between dollar 
    and cent representation.
    """
    logger.info("\nTesting currency conversion handling...")
    
    # Test conversion functions to ensure they're consistent
    test_cases = [
        (25, 2500),    # $25 -> 2500 cents
        (25.0, 2500),  # $25.0 -> 2500 cents
        (25.00, 2500), # $25.00 -> 2500 cents
        (25.5, 2550),  # $25.50 -> 2550 cents
        (25.99, 2599), # $25.99 -> 2599 cents
        (0.99, 99),    # $0.99 -> 99 cents
        (0.01, 1),     # $0.01 -> 1 cent
    ]
    
    for dollars, expected_cents in test_cases:
        # Calculate cents from dollars
        calculated_cents = int(float(dollars) * 100)
        
        if calculated_cents == expected_cents:
            logger.info(f"✅ ${dollars:.2f} -> {calculated_cents} cents (matched expected {expected_cents})")
        else:
            logger.error(f"❌ ${dollars:.2f} -> {calculated_cents} cents (expected {expected_cents})")
    
    # Reverse conversion tests (cents to dollars)
    for dollars, cents in test_cases:
        # Calculate dollars from cents
        calculated_dollars = cents / 100
        
        if calculated_dollars == float(dollars):
            logger.info(f"✅ {cents} cents -> ${calculated_dollars:.2f} (matched expected ${dollars:.2f})")
        else:
            logger.error(f"❌ {cents} cents -> ${calculated_dollars:.2f} (expected ${dollars:.2f})")

if __name__ == "__main__":
    print("\n===== IELTS GenAI Prep - Stripe Checkout Debug =====\n")
    
    # First check the direct Stripe API integration
    if debug_stripe_checkout():
        print("\n✅ Stripe direct checkout test passed successfully!")
    else:
        print("\n❌ Stripe direct checkout test failed.")
        
    # Also verify currency handling logic
    verify_currency_handling()
    
    print("\n====================================================")