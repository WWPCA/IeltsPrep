"""
Fix for the Stripe checkout error with payment_method_types.
This script creates a modified version of create_stripe_checkout_session
that only uses the 'card' payment method.
"""

def fix_stripe_checkout():
    """Fix the Stripe checkout process to only use card payments."""
    
    print("Fixing Stripe checkout process...")
    
    # Read the payment_services.py file
    with open('payment_services.py', 'r') as f:
        content = f.read()
    
    # Replace the region payment mapping code with a simplified version
    # that only uses card payments (which is universally supported)
    old_code = """
        # Use the country code if provided
        user_country = country_code
        # Dynamic payment method types based on user region
        payment_method_types = ['card']
        
        # Add region-specific payment methods
        region_payment_mapping = {
            # East Asia
            'CN': ['alipay', 'wechat_pay'],
            'JP': ['konbini', 'paypay', 'jcb'],
            'KR': ['kakaopay', 'naver_pay'],
            
            # Southeast Asia
            'MY': ['grabpay', 'fpx', 'boost', 'touch_n_go'],
            'TH': ['promptpay', 'truemoney'],
            'ID': ['dana', 'ovo', 'gopay', 'linkaja'],
            'PH': ['gcash', 'paymaya'],
            'SG': ['grabpay', 'paynow'],
            'VN': ['momo', 'zalopay', 'vnpay'],
            
            # South Asia
            'IN': ['upi', 'paytm', 'netbanking', 'amazon_pay', 'phonepe'],
            'PK': ['easypaisa', 'jazzcash'],
            'BD': ['bkash', 'rocket', 'nagad'],
            'NP': ['esewa', 'khalti'],
            
            # Latin America
            'BR': ['boleto', 'pix', 'mercado_pago'],
            'MX': ['oxxo', 'spei', 'mercado_pago'],
            
            # Middle East
            'AE': ['benefit', 'apple_pay'],
            'SA': ['stcpay', 'mada'],
            'EG': ['fawry', 'meeza'],
            'TR': ['troy', 'papara', 'ininal'],
            
            # Africa
            'KE': ['mpesa', 'airtel_money'],
            'NG': ['paystack', 'flutterwave', 'opay'],
            'ET': ['cbe_birr', 'telebirr'],
            'TZ': ['mpesa', 'tigopesa', 'airtel_money'],
            
            # Oceania
            'AU': ['afterpay', 'bpay', 'osko'],
            'NZ': ['afterpay', 'poli'],
            
            # North America
            'CA': ['interac'],
            'US': ['affirm', 'us_bank_account', 'venmo'],
            
            # Europe
            'GB': ['bacs_debit', 'ideal', 'sofort'],
            'RU': ['yandex_pay', 'qiwi', 'sberbank']
        }
        
        # If we have user_country, add the appropriate payment methods
        if user_country and user_country in region_payment_mapping:
            payment_method_types.extend(region_payment_mapping[user_country])"""
    
    new_code = """
        # Simplify payment methods to only use card payments (universally supported)
        payment_method_types = ['card']
        
        # Note: We've removed the complex region mapping to fix the Stripe checkout error
        # If region-specific payment methods are needed in the future, ensure they're 
        # approved by Stripe and match their supported payment method types."""
    
    # Replace the code
    modified_content = content.replace(old_code, new_code)
    
    # Also replace a similar section that appears earlier in the file (subscription based version)
    old_subscription_code = """
        # Use the country code if provided
        user_country = country_code
        # Dynamic payment method types based on user region
        payment_method_types = ['card']
        
        # Add region-specific payment methods
        region_payment_mapping = {
            # Add country specific payment methods here
            'US': ['card'],
            'GB': ['card', 'bacs_debit'],
            'EU': ['card', 'sepa_debit', 'ideal', 'sofort'],
            'IN': ['card', 'upi'],
            'CN': ['card', 'alipay', 'wechat_pay'],
            'JP': ['card', 'konbini'],
            'KR': ['card'],
            'BR': ['card', 'boleto']
        }
        
        # If we have user_country, add the appropriate payment methods
        if user_country and user_country in region_payment_mapping:
            payment_method_types.extend(region_payment_mapping[user_country])"""
    
    modified_content = modified_content.replace(old_subscription_code, new_code)
    
    # Write the modified file
    with open('payment_services.py', 'w') as f:
        f.write(modified_content)
    
    print("Stripe checkout fix applied successfully.")
    print("Payment method types simplified to card-only to ensure compatibility.")

if __name__ == "__main__":
    fix_stripe_checkout()