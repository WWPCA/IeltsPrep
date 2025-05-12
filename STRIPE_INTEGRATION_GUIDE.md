# Stripe Integration Guide

## Overview

This guide explains the Stripe integration in the IELTS AI Prep application, including payment processing, automatic tax calculation, and webhooks.

## Key Components

1. **Stripe Checkout Sessions** - Primary payment method for product purchases
2. **Stripe Buy Buttons** - Simplified payment flow for assessment products
3. **Stripe Setup Intents** - Testing functionality for payment method setup
4. **Stripe Webhooks** - Asynchronous payment success/failure handling

## Automatic Tax Calculation

Stripe's automatic tax calculation is enabled for all payments to ensure proper tax compliance in different jurisdictions where our customers are located.

### Implementation Details

1. **Customer Address Collection**:
   - Billing address is collected during payment
   - Address is stored in PaymentRecord model
   - Used for tax calculation and compliance

2. **Tax Configuration**:
   - Automatic tax calculation enabled in all payment intents
   - Tax calculation works in both production and test modes
   - Tax rates are determined based on customer location

3. **Test Environment**:
   - Test environment supports automatic tax calculation
   - Testing tool includes address fields for proper tax simulation
   - Simulates real tax rates for testing purposes

### Code Implementation

```python
# Enable automatic tax calculation in payment intents
payment_intent_params = {
    'amount': amount,
    'currency': currency,
    'customer': customer_id,
    'payment_method': payment_method_id,
    'automatic_tax': {'enabled': True},
    # Additional parameters...
}

# Update customer with tax information
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
```

## Payment Testing Area

The application includes a payment testing area for administrators to verify payment functionality:

1. **Setup Intent Flow**:
   - Create a payment method
   - Store it for future use
   - Process test payments
   - Verify tax calculation

2. **Test Payment Processing**:
   - Full simulation of payment flow
   - Automatic tax calculation
   - Payment record creation
   - Success/failure handling

## Security Considerations

1. **Webhooks**:
   - Secure webhook handling with signature verification
   - Idempotency to prevent duplicate processing
   - Error logging and monitoring

2. **API Keys**:
   - Stripe secret key protected as environment variable
   - Publishable key used only for client-side integration
   - Test mode indicated clearly to users

## Country Restrictions

Stripe integration includes country-based restrictions to enforce application access controls:

1. **Allowed Countries**:
   - USA
   - Canada
   - India
   - Nepal
   - Kuwait
   - Qatar
 
2. **Implementation**:
   - Stripe billing address verification
   - GeoIP-based access control
   - Server-side validation

3. **EU/UK Special Cases**:
   - Blocked due to regulatory considerations
   - Access mechanism for future expansion

## Troubleshooting

Common issues and solutions:

1. **Payment Failures**:
   - Check Stripe Dashboard for detailed error information
   - Verify test cards are properly formatted
   - Ensure correct API keys are being used

2. **Webhook Issues**:
   - Confirm correct endpoint registration in Stripe Dashboard
   - Verify webhook signatures are correctly validated
   - Check server logs for webhook processing errors

3. **Tax Calculation Problems**:
   - Ensure customer address is complete
   - Verify tax calculation is enabled in params
   - Check Stripe Dashboard for tax settings