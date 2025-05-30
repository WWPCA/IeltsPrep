#!/usr/bin/env python3
"""
Test script to check reCAPTCHA configuration
"""
import os
import requests

def test_recaptcha_keys():
    """Test if the current reCAPTCHA keys are working"""
    
    # Check both production and development keys
    prod_site_key = os.environ.get('RECAPTCHA_PUBLIC_KEY')
    prod_secret_key = os.environ.get('RECAPTCHA_PRIVATE_KEY')
    dev_site_key = os.environ.get('RECAPTCHA_DEV_PUBLIC_KEY')
    dev_secret_key = os.environ.get('RECAPTCHA_DEV_PRIVATE_KEY')
    
    print("=== Production Keys ===")
    print(f"Site key present: {bool(prod_site_key)}")
    print(f"Secret key present: {bool(prod_secret_key)}")
    if prod_site_key:
        print(f"Site key starts with: {prod_site_key[:10]}...")
    
    print("\n=== Development Keys ===")
    print(f"Dev site key present: {bool(dev_site_key)}")
    print(f"Dev secret key present: {bool(dev_secret_key)}")
    if dev_site_key:
        print(f"Dev site key starts with: {dev_site_key[:10]}...")
    
    # Use development keys for testing
    site_key = dev_site_key
    secret_key = dev_secret_key
    
    print(f"Site key present: {bool(site_key)}")
    print(f"Secret key present: {bool(secret_key)}")
    
    if site_key:
        print(f"Site key starts with: {site_key[:10]}...")
    
    if secret_key:
        print(f"Secret key starts with: {secret_key[:10]}...")
    
    # Test a dummy verification to see what error we get
    if secret_key:
        verify_data = {
            'secret': secret_key,
            'response': 'test-token',
            'remoteip': '127.0.0.1'
        }
        
        try:
            r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=verify_data)
            result = r.json()
            print(f"Test verification result: {result}")
            
            if 'error-codes' in result:
                error_codes = result['error-codes']
                print(f"Error codes: {error_codes}")
                
                # Common error codes:
                # invalid-input-secret: The secret parameter is invalid or malformed
                # invalid-input-response: The response parameter is invalid or malformed
                # bad-request: The request is invalid or malformed
                # timeout-or-duplicate: The response is no longer valid
                
        except Exception as e:
            print(f"Request failed: {e}")

if __name__ == "__main__":
    test_recaptcha_keys()