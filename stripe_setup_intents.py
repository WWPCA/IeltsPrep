"""
Stripe Setup Intents Integration
This module provides functionality for creating and managing Stripe Setup Intents
for testing payment integration in sandbox mode.
"""

import os
import stripe
import logging
from flask import url_for
from datetime import datetime

# Set Stripe API key
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', '')

def create_setup_intent(customer_email=None, customer_name=None):
    """
    Create a Stripe Setup Intent for testing payment method setup.
    
    Args:
        customer_email (str, optional): Customer email for pre-filling
        customer_name (str, optional): Customer name for pre-filling
        
    Returns:
        dict: Contains client_secret and other setup intent details
    """
    try:
        # Create a customer if email is provided
        customer = None
        if customer_email:
            customers = stripe.Customer.list(email=customer_email, limit=1)
            if customers.data:
                customer = customers.data[0]
            else:
                customer_data = {'email': customer_email}
                if customer_name:
                    customer_data['name'] = customer_name
                customer = stripe.Customer.create(**customer_data)
        
        # Create setup intent
        setup_intent_args = {
            'payment_method_types': ['card'],
            'usage': 'off_session',  # Allow for off-session payments
            'metadata': {
                'source': 'ielts_genai_prep',
                'created_at': datetime.utcnow().isoformat()
            }
        }
        
        # Only add customer if it exists
        if customer:
            setup_intent_args['customer'] = customer.id
            
        setup_intent = stripe.SetupIntent.create(**setup_intent_args)
        
        return {
            'client_secret': setup_intent.client_secret,
            'id': setup_intent.id,
            'customer_id': customer.id if customer else None
        }
    except Exception as e:
        logging.error(f"Error creating Stripe setup intent: {str(e)}")
        raise

def get_setup_intent(setup_intent_id):
    """
    Retrieve a Stripe Setup Intent.
    
    Args:
        setup_intent_id (str): The ID of the setup intent to retrieve
        
    Returns:
        dict: Setup intent details
    """
    try:
        return stripe.SetupIntent.retrieve(setup_intent_id)
    except Exception as e:
        logging.error(f"Error retrieving Stripe setup intent: {str(e)}")
        raise

def create_test_payment(customer_id, payment_method_id, amount=1000, currency='usd', address=None):
    """
    Create a test payment using a stored payment method.
    
    Args:
        customer_id (str): Stripe customer ID
        payment_method_id (str): Stripe payment method ID
        amount (int): Amount in cents
        currency (str): Currency code
        address (dict, optional): Address information for tax calculation
        
    Returns:
        dict: Payment intent details
    """
    try:
        # Get the domain for success and cancel URLs
        domain = os.environ.get('REPLIT_DEV_DOMAIN') if os.environ.get('REPLIT_DEPLOYMENT') != '' else os.environ.get('REPLIT_DOMAINS', '').split(',')[0]
        
        # Set up the payment intent params
        payment_intent_params = {
            'amount': amount,
            'currency': currency,
            'customer': customer_id,
            'payment_method': payment_method_id,
            'off_session': True,
            'confirm': True,
            'metadata': {
                'source': 'ielts_genai_prep_test',
                'created_at': datetime.utcnow().isoformat(),
            }
        }
        
        # Enable automatic tax calculation if address is provided
        if address:
            # Update the customer with tax information
            stripe.Customer.modify(
                customer_id,
                address={
                    'line1': address.get('line1', ''),
                    'line2': address.get('line2', ''),
                    'city': address.get('city', ''),
                    'state': address.get('state', ''),
                    'postal_code': address.get('postal_code', ''),
                    'country': address.get('country', 'US'),
                },
                tax_exempt='none'  # Ensure customer is not tax-exempt
            )
            
            # Enable automatic tax calculation for this payment
            payment_intent_params['automatic_tax'] = {'enabled': True}
            payment_intent_params['metadata']['automatic_tax_enabled'] = 'true'
        
        # Create the payment intent
        payment_intent = stripe.PaymentIntent.create(**payment_intent_params)
        
        return payment_intent
    except Exception as e:
        logging.error(f"Error creating test payment: {str(e)}")
        raise