#!/usr/bin/env python3
"""
Test reCAPTCHA v2 validation directly with Google's API
This script tests the exact same verification process our app uses
"""

import os
import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_recaptcha_keys():
    """Test if reCAPTCHA keys are properly configured"""
    site_key = os.environ.get('RECAPTCHA_V2_SITE_KEY')
    secret_key = os.environ.get('RECAPTCHA_V2_SECRET_KEY')
    
    logger.info(f"Site key present: {bool(site_key)}")
    logger.info(f"Secret key present: {bool(secret_key)}")
    
    if site_key:
        logger.info(f"Site key: {site_key[:10]}...{site_key[-4:]}")
    if secret_key:
        logger.info(f"Secret key: {secret_key[:10]}...{secret_key[-4:]}")
    
    return site_key, secret_key

def test_google_api_connectivity():
    """Test connectivity to Google's reCAPTCHA API"""
    verify_url = "https://www.google.com/recaptcha/api/siteverify"
    
    try:
        # Test with invalid data to ensure we get a response
        test_data = {
            'secret': 'test',
            'response': 'test'
        }
        
        response = requests.post(verify_url, data=test_data, timeout=10)
        logger.info(f"Google API connectivity test - HTTP status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Google API response: {result}")
            return True
        else:
            logger.error(f"Google API returned HTTP {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to connect to Google API: {e}")
        return False

def test_recaptcha_verification(secret_key, test_token="invalid_test_token"):
    """Test actual reCAPTCHA verification"""
    verify_url = "https://www.google.com/recaptcha/api/siteverify"
    
    data = {
        'secret': secret_key,
        'response': test_token
    }
    
    try:
        response = requests.post(verify_url, data=data, timeout=10)
        logger.info(f"Verification test - HTTP status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Verification result: {result}")
            
            success = result.get('success', False)
            errors = result.get('error-codes', [])
            
            logger.info(f"Success: {success}")
            logger.info(f"Errors: {errors}")
            
            return success, errors
        else:
            logger.error(f"HTTP error: {response.status_code}")
            return False, [f"HTTP {response.status_code}"]
            
    except Exception as e:
        logger.error(f"Verification exception: {e}")
        return False, [str(e)]

if __name__ == "__main__":
    logger.info("Starting reCAPTCHA validation tests...")
    
    # Test 1: Check keys
    logger.info("\n=== Test 1: Checking reCAPTCHA keys ===")
    site_key, secret_key = test_recaptcha_keys()
    
    # Test 2: API connectivity
    logger.info("\n=== Test 2: Testing Google API connectivity ===")
    api_ok = test_google_api_connectivity()
    
    # Test 3: Verification with our keys
    if secret_key and api_ok:
        logger.info("\n=== Test 3: Testing verification with our keys ===")
        success, errors = test_recaptcha_verification(secret_key)
        
        if not success and 'invalid-input-response' in errors:
            logger.info("✓ Keys are working correctly (expected invalid-input-response for test token)")
        elif not success and 'invalid-input-secret' in errors:
            logger.error("✗ Secret key is invalid")
        else:
            logger.info(f"Verification result: success={success}, errors={errors}")
    
    logger.info("\nreCAPTCHA validation tests completed.")