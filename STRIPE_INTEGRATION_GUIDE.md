# Stripe Integration Guide

## Overview

This guide explains the Stripe integration in the IELTS AI Prep application, including payment processing, automatic tax calculation, and webhooks.

## Key Components

1. **Stripe Checkout Sessions** - Primary payment method for product purchases
2. **Stripe Buy Buttons** - Simplified payment flow for assessment products
3. **Stripe Setup Intents** - Testing functionality for payment method setup
4. **Stripe Webhooks** - Asynchronous payment success/failure handling

## Automatic Tax Calculation

Stripe's automatic tax calculation is enabled for all payments to ensure proper tax compliance in different jurisdictions where our customers are located. This feature is particularly important as we operate in multiple countries with varied tax regulations.

### Implementation Details

1. **Customer Address Collection**:
   - Complete billing address is collected during checkout
   - Address includes country, state/province, city, postal code, and street address
   - All address components are required for accurate tax calculation
   - Address information is stored in the PaymentRecord model for compliance and reporting

2. **Tax Configuration**:
   - Automatic tax calculation is enabled for all payment intents via the `automatic_tax` parameter
   - Tax rates are determined dynamically based on customer location and current tax regulations
   - System supports both sales tax (US) and VAT (international) calculation
   - Tax calculation works in both production and test/sandbox modes

3. **Country-Specific Considerations**:
   - **United States**: Calculates state and local sales taxes based on precise location
   - **Canada**: Handles GST, HST, and PST/QST depending on province
   - **India**: Applies appropriate GST rates
   - **Nepal, Kuwait, Qatar**: Implements country-specific VAT or sales tax requirements

4. **Test Environment Support**:
   - Full tax calculation functionality is available in test/sandbox mode
   - Address validation works the same as in production
   - Test mode simulates actual tax rates without creating real charges
   - Comprehensive testing framework available in `tax_verification_script.py`

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

### Tax Calculation Testing

Tax calculation is now fully managed through Stripe's automatic tax features. We've updated our approach to tax testing:

1. **Checkout Flow Testing**: Test tax calculation directly through the checkout flow rather than separate scripts
2. **Stripe Dashboard**: Monitor and verify tax calculations in the Stripe Dashboard
3. **Visual Indicators**: Added tax notification in the cart interface for user awareness

The tax calculation is now transparent to users with notifications in:
- Desktop cart view (subtotal with tax notice)
- Mobile cart view (subtotal with tax notice)
- Checkout flow (user status check page)

Example user notification:
```
Subtotal: $25.00
Taxes will be calculated at checkout based on your location
```

This approach simplifies testing while providing better transparency to users about tax calculations.

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
   - Ensure customer address is complete and properly formatted
   - Verify tax calculation is enabled in checkout session parameters (`automatic_tax: {enabled: true}`)
   - Check Stripe Dashboard for tax settings and calculation details
   - Test the complete checkout flow rather than using separate verification tools
   - Verify tax-related notices appear correctly in cart and checkout pages