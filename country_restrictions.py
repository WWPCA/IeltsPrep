"""
Country Access Restrictions
Manages geographic access controls for IELTS GenAI Prep platform
"""

import logging
from functools import wraps
from flask import request, jsonify, flash, redirect, url_for, abort

logger = logging.getLogger(__name__)

# Allowed countries for access (Canada-only restriction)
ALLOWED_COUNTRIES = ['CA', 'CAN', 'CANADA']

# Restriction message for users from non-allowed countries
RESTRICTION_MESSAGE = "IELTS GenAI Prep is currently available only to users in Canada. We apologize for any inconvenience."

def get_user_country():
    """Get user's country from request headers or IP geolocation"""
    try:
        # Check CloudFlare country header (common in production)
        country = request.headers.get('CF-IPCountry')
        if country:
            return country.upper()
        
        # Check other common country headers
        country = request.headers.get('X-Country-Code')
        if country:
            return country.upper()
        
        # For development/testing, assume Canada if no headers
        return 'CA'
        
    except Exception as e:
        logger.error(f"Error determining user country: {e}")
        return 'CA'  # Default to allowed country

def is_country_restricted(country_code=None):
    """Check if a country is restricted from accessing the platform"""
    if country_code is None:
        country_code = get_user_country()
    
    if not country_code:
        return False  # Allow if unable to determine country
    
    return country_code.upper() not in ALLOWED_COUNTRIES

def get_allowed_countries():
    """Get list of allowed countries"""
    return ALLOWED_COUNTRIES.copy()

def country_access_required(f):
    """Decorator to enforce country access restrictions"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_country = get_user_country()
        
        if is_country_restricted(user_country):
            logger.warning(f"Access denied for country: {user_country}")
            
            if request.is_json:
                return jsonify({
                    'success': False,
                    'error': RESTRICTION_MESSAGE,
                    'country_code': user_country
                }), 403
            else:
                flash(RESTRICTION_MESSAGE, 'error')
                abort(403)
        
        return f(*args, **kwargs)
    
    return decorated_function

def log_country_access(user_id=None):
    """Log country access attempt for monitoring"""
    try:
        country = get_user_country()
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        logger.info(f"Access attempt - Country: {country}, IP: {ip_address}, User: {user_id}")
        
        if is_country_restricted(country):
            logger.warning(f"Blocked access from restricted country: {country}")
        
    except Exception as e:
        logger.error(f"Error logging country access: {e}")

def validate_country_for_payment(country_code):
    """Validate country for payment processing"""
    if is_country_restricted(country_code):
        return False, RESTRICTION_MESSAGE
    
    return True, "Country allowed for payment processing"

def get_country_specific_content(country_code=None):
    """Get country-specific content or configuration"""
    if country_code is None:
        country_code = get_user_country()
    
    # Canada-specific configuration
    if country_code in ALLOWED_COUNTRIES:
        return {
            'currency': 'CAD',
            'tax_rate': 0.13,  # HST for Ontario
            'support_email': 'support@ieltsaiprep.com',
            'privacy_policy_url': '/privacy-policy-ca'
        }
    
    # Default configuration for restricted countries (for error pages)
    return {
        'currency': 'USD',
        'tax_rate': 0.0,
        'support_email': 'info@ieltsaiprep.com',
        'privacy_policy_url': '/privacy-policy'
    }