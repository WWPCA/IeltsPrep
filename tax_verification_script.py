"""
Tax Verification Script

This script demonstrates how to verify Stripe automatic tax calculation is working,
by creating a test payment with a specific address and checking the calculated tax.

For admin use only - do not run in production environment.
"""

import os
import stripe
import json
from datetime import datetime

# Set your Stripe API key
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

def test_tax_calculation(country_code, postal_code, amount=1000):
    """
    Test automatic tax calculation for a specific country and postal code.
    
    Args:
        country_code (str): Two-letter country code (e.g., 'US', 'CA')
        postal_code (str): Postal code to test
        amount (int): Amount in cents to test (default: 1000 = $10.00)
    
    Returns:
        dict: Details of the tax calculation
    """
    print(f"Testing tax calculation for {country_code} {postal_code}...")
    
    # Create a test customer
    customer = stripe.Customer.create(
        email=f"test_{country_code.lower()}_{postal_code}@example.com",
        name=f"Test Customer {country_code}",
        address={
            'line1': '123 Test Street',
            'city': 'Test City',
            'state': 'Test State',
            'postal_code': postal_code,
            'country': country_code,
        },
        tax_exempt='none'  # Ensure customer is not tax-exempt
    )
    
    # Create a payment method (doesn't actually charge)
    payment_method = stripe.PaymentMethod.create(
        type='card',
        card={
            'number': '4242424242424242',
            'exp_month': 12,
            'exp_year': datetime.now().year + 1,
            'cvc': '123',
        },
    )
    
    # Attach payment method to customer
    stripe.PaymentMethod.attach(
        payment_method.id,
        customer=customer.id,
    )
    
    # Create a payment intent with automatic tax calculation
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='usd',
            customer=customer.id,
            payment_method=payment_method.id,
            off_session=True,
            confirm=True,
            automatic_tax={'enabled': True},
            metadata={
                'tax_test': 'true',
                'country': country_code,
                'postal_code': postal_code
            }
        )
        
        # Get tax details
        tax_details = {
            'country': country_code,
            'postal_code': postal_code,
            'amount': f"${amount/100:.2f}",
            'tax_enabled': payment_intent.automatic_tax.enabled,
            'tax_status': payment_intent.automatic_tax.status,
        }
        
        # Add calculated tax amount if available
        if hasattr(payment_intent, 'tax'):
            tax_amount = payment_intent.tax.amount if hasattr(payment_intent, 'tax') else 0
            tax_details['tax_amount'] = f"${tax_amount/100:.2f}"
            tax_details['tax_percentage'] = f"{(tax_amount / amount) * 100:.2f}%"
        
        print(f"Tax calculation successful for {country_code} {postal_code}")
        print(json.dumps(tax_details, indent=2))
        return tax_details
    
    except Exception as e:
        print(f"Error testing tax calculation: {str(e)}")
        return {
            'country': country_code,
            'postal_code': postal_code, 
            'error': str(e)
        }
    finally:
        # Clean up - delete the test customer
        try:
            stripe.Customer.delete(customer.id)
        except Exception as e:
            print(f"Warning: Failed to delete test customer: {str(e)}")


def run_tax_tests():
    """Run tax calculation tests for various locations.
    
    Returns:
        list: List of dictionaries with test results for each country.
    """
    test_countries = [
        {'country_code': 'US', 'postal_code': '94103', 'country_name': 'United States (California)'},
        {'country_code': 'US', 'postal_code': '10001', 'country_name': 'United States (New York)'},
        {'country_code': 'US', 'postal_code': '33139', 'country_name': 'United States (Florida)'},
        {'country_code': 'CA', 'postal_code': 'M5V 2N4', 'country_name': 'Canada (Toronto)'},
        {'country_code': 'IN', 'postal_code': '400001', 'country_name': 'India (Mumbai)'},
        {'country_code': 'NP', 'postal_code': '44600', 'country_name': 'Nepal (Kathmandu)'},
        {'country_code': 'KW', 'postal_code': '13001', 'country_name': 'Kuwait (Kuwait City)'},
        {'country_code': 'QA', 'postal_code': '00974', 'country_name': 'Qatar (Doha)'}
    ]
    
    # Standard price amount for IELTS assessment test
    price_amount = 2500  # $25.00 USD
    
    results = []
    
    for country in test_countries:
        try:
            # Create a test customer
            customer = stripe.Customer.create(
                email=f"test_{country['country_code'].lower()}_{country['postal_code']}@example.com",
                name=f"Test Customer {country['country_code']}",
                address={
                    'line1': '123 Test Street',
                    'city': 'Test City',
                    'state': 'Test State',
                    'postal_code': country['postal_code'],
                    'country': country['country_code'],
                },
                tax_exempt='none'  # Ensure customer is not tax-exempt
            )
            
            # Create a test price calculation
            calculation = stripe.tax.Calculation.create(
                currency="usd",
                customer=customer.id,
                line_items=[
                    {
                        "amount": price_amount, 
                        "reference": "ielts_assessment",
                        "tax_behavior": "exclusive",
                    }
                ],
                expand=["line_items"]
            )
            
            # Extract useful tax information
            tax_amount = calculation.tax_breakdown[0]['tax_amount'] if calculation.tax_breakdown else 0
            tax_rate = (tax_amount / price_amount) * 100 if price_amount > 0 else 0
            
            # Format the result
            result = {
                'country_code': country['country_code'],
                'country_name': country['country_name'],
                'postal_code': country['postal_code'],
                'price_amount': price_amount,
                'tax_amount': tax_amount,
                'tax_rate': tax_rate,
                'total_amount': price_amount + tax_amount,
                'success': True,
                'error': None
            }
            
            # Clean up the test customer
            stripe.Customer.delete(customer.id)
                        
        except Exception as e:
            result = {
                'country_code': country['country_code'],
                'country_name': country['country_name'],
                'postal_code': country['postal_code'],
                'price_amount': price_amount,
                'tax_amount': 0,
                'tax_rate': 0,
                'total_amount': price_amount,
                'success': False,
                'error': str(e)
            }
        
        results.append(result)
        print(f"Tested {country['country_name']}: {'Success' if result['success'] else 'Failed - ' + result['error']}")
    
    return results


if __name__ == "__main__":
    # Only run if executed directly
    if not stripe.api_key:
        print("Error: STRIPE_SECRET_KEY environment variable is not set")
    else:
        run_tax_tests()