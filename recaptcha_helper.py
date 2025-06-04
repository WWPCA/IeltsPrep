"""
reCAPTCHA Helper Module
Provides server-side reCAPTCHA verification with robust error handling
"""

import os
import requests
import logging
from flask import request, current_app
import json

logger = logging.getLogger(__name__)

def get_recaptcha_secret_key():
    """Get the appropriate reCAPTCHA v2 secret key"""
    return (os.environ.get("RECAPTCHA_V2_SECRET_KEY") or 
            os.environ.get("RECAPTCHA_PRIVATE_KEY") or 
            os.environ.get("RECAPTCHA_DEV_PRIVATE_KEY"))

def verify_recaptcha(token, action=None, min_score=0.5):
    """
    Verify reCAPTCHA token with Google's servers
    
    Args:
        token (str): The reCAPTCHA token from the client
        action (str): Expected action (login, register, etc.)
        min_score (float): Minimum score threshold (0.0 to 1.0)
    
    Returns:
        tuple: (success: bool, score: float, errors: list)
    """
    if not token:
        logger.warning("reCAPTCHA verification failed: No token provided")
        return False, 0.0, ["No reCAPTCHA token provided"]
    
    secret_key = get_recaptcha_secret_key()
    if not secret_key:
        logger.error("reCAPTCHA verification failed: No secret key configured")
        return False, 0.0, ["reCAPTCHA not configured"]
    
    # Prepare verification request
    verify_url = "https://www.google.com/recaptcha/api/siteverify"
    data = {
        'secret': secret_key,
        'response': token,
        'remoteip': get_client_ip()
    }
    
    try:
        # Make request to Google's verification endpoint
        response = requests.post(verify_url, data=data, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        logger.info(f"reCAPTCHA verification response: {result}")
        
        success = result.get('success', False)
        errors = result.get('error-codes', [])
        
        # reCAPTCHA v2 doesn't have scores or actions, so we return None for score
        score = None
        
        if success:
            logger.info(f"reCAPTCHA v2 verification successful")
        else:
            logger.warning(f"reCAPTCHA v2 verification failed: errors={errors}")
        
        return success, score, errors
        
    except requests.exceptions.Timeout:
        logger.error("reCAPTCHA verification timeout")
        return False, 0.0, ["Verification service timeout"]
        
    except requests.exceptions.ConnectionError:
        logger.error("reCAPTCHA verification connection error")
        return False, 0.0, ["Cannot connect to verification service"]
        
    except requests.exceptions.RequestException as e:
        logger.error(f"reCAPTCHA verification request error: {e}")
        return False, 0.0, ["Verification service error"]
        
    except json.JSONDecodeError:
        logger.error("reCAPTCHA verification invalid response format")
        return False, 0.0, ["Invalid verification response"]
        
    except Exception as e:
        logger.error(f"reCAPTCHA verification unexpected error: {e}")
        return False, 0.0, ["Verification failed"]

def get_client_ip():
    """Get the real client IP address, accounting for proxies"""
    # Check for forwarded IP first (common in proxy setups)
    forwarded_ips = request.headers.get('X-Forwarded-For')
    if forwarded_ips:
        # Get the first IP (original client)
        return forwarded_ips.split(',')[0].strip()
    
    # Check other common proxy headers
    real_ip = request.headers.get('X-Real-IP')
    if real_ip:
        return real_ip
    
    # Fall back to remote address
    return request.environ.get('REMOTE_ADDR', '127.0.0.1')

def require_recaptcha(action=None, min_score=0.5):
    """
    Decorator to require reCAPTCHA verification for a route
    
    Args:
        action (str): Expected reCAPTCHA action
        min_score (float): Minimum score threshold
    
    Returns:
        Flask response or None if verification passes
    """
    def decorator(f):
        def decorated_function(*args, **kwargs):
            # Get reCAPTCHA token from form data
            token = request.form.get('g-recaptcha-response')
            
            # Verify the token
            success, score, errors = verify_recaptcha(token, action, min_score)
            
            if not success:
                logger.warning(f"reCAPTCHA verification failed for route {request.endpoint}: {errors}")
                from flask import flash, redirect, url_for
                
                # Flash appropriate error message
                if "timeout" in str(errors).lower() or "connect" in str(errors).lower():
                    flash("Security verification is temporarily unavailable. Please try again in a moment.", "error")
                elif "score" in str(errors).lower():
                    flash("Security verification failed. Please try again.", "error")
                else:
                    flash("Security verification failed. Please refresh the page and try again.", "error")
                
                # Redirect back to the referring page or login
                return redirect(request.referrer or url_for('login'))
            
            # Verification successful, proceed with the original function
            logger.info(f"reCAPTCHA verification successful for route {request.endpoint}: score={score}")
            return f(*args, **kwargs)
            
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator

def is_recaptcha_configured():
    """Check if reCAPTCHA is properly configured"""
    site_key = current_app.config.get('RECAPTCHA_SITE_KEY')
    secret_key = get_recaptcha_secret_key()
    return bool(site_key and secret_key)

def get_recaptcha_status():
    """Get current reCAPTCHA configuration status"""
    return {
        'configured': is_recaptcha_configured(),
        'site_key': current_app.config.get('RECAPTCHA_SITE_KEY', 'Not configured'),
        'secret_key_present': bool(get_recaptcha_secret_key())
    }