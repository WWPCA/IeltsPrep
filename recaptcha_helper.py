"""
reCAPTCHA Helper Module
Provides reCAPTCHA validation functionality for IELTS GenAI Prep
"""

import os
import requests
import logging

logger = logging.getLogger(__name__)

def get_recaptcha_keys():
    """Get appropriate reCAPTCHA v2 keys based on environment"""
    # Use production keys as fallback since dev keys aren't configured
    site_key = os.environ.get('RECAPTCHA_V2_SITE_KEY')
    secret_key = os.environ.get('RECAPTCHA_V2_SECRET_KEY')
    
    # If production keys aren't available, try development keys
    if not site_key or not secret_key:
        site_key = os.environ.get('RECAPTCHA_DEV_PUBLIC_KEY')
        secret_key = os.environ.get('RECAPTCHA_DEV_PRIVATE_KEY')
    
    return site_key, secret_key

def verify_recaptcha(recaptcha_response, user_ip=None):
    """
    Verify reCAPTCHA response with Google's API
    
    Args:
        recaptcha_response (str): The reCAPTCHA response token
        user_ip (str, optional): User's IP address for additional verification
        
    Returns:
        bool: True if verification successful, False otherwise
    """
    if not recaptcha_response:
        logger.warning("No reCAPTCHA response provided")
        return False
    
    site_key, secret_key = get_recaptcha_keys()
    
    if not secret_key:
        logger.error("reCAPTCHA secret key not configured")
        return False
    
    # Prepare verification request
    data = {
        'secret': secret_key,
        'response': recaptcha_response
    }
    
    if user_ip:
        data['remoteip'] = user_ip
    
    try:
        # Send verification request to Google
        response = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data=data,
            timeout=10
        )
        
        result = response.json()
        
        if result.get('success'):
            logger.info("reCAPTCHA verification successful")
            return True
        else:
            logger.warning(f"reCAPTCHA verification failed: {result.get('error-codes', [])}")
            return False
            
    except requests.RequestException as e:
        logger.error(f"reCAPTCHA verification request failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during reCAPTCHA verification: {e}")
        return False

def is_recaptcha_enabled():
    """Check if reCAPTCHA is properly configured and enabled"""
    site_key, secret_key = get_recaptcha_keys()
    return bool(site_key and secret_key)