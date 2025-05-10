"""
Country Restrictions Configuration
This module defines which countries are restricted from accessing the application.
"""

import os
import logging
from flask import request, redirect, url_for, flash, session, jsonify
from functools import wraps

# Set up logging
logger = logging.getLogger(__name__)

# List of country codes that are restricted from accessing the application
# ISO 3166-1 alpha-2 country codes (2 letter codes)
RESTRICTED_COUNTRIES = [
    'BR',  # Brazil
    'RU',  # Russia
    'CN',  # China
    'KR',  # South Korea
]

# Message to display to users from restricted countries
RESTRICTION_MESSAGE = (
    "We're sorry, but our services are not available in your region due to regulatory requirements. "
    "We're working to expand our coverage. Thank you for your understanding."
)

def is_country_restricted(country_code):
    """
    Check if a country is in the restricted list.
    
    Args:
        country_code (str): ISO 3166-1 alpha-2 country code
        
    Returns:
        bool: True if the country is restricted, False otherwise
    """
    if not country_code:
        return False
        
    return country_code.upper() in RESTRICTED_COUNTRIES

def country_access_required(f):
    """
    Decorator to restrict access based on country.
    Redirects to a restriction page if the user's country is restricted.
    
    Usage:
        @app.route('/some-route')
        @country_access_required
        def some_view():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from geoip_services import get_country_from_ip
        
        # Get the user's country code
        country_code, _ = get_country_from_ip()
        
        # Store the country code in the session for future reference
        if country_code:
            session['country_code'] = country_code
        
        # Check if the country is restricted
        if country_code and is_country_restricted(country_code):
            logger.info(f"Blocked access from restricted country: {country_code}")
            flash(RESTRICTION_MESSAGE, "warning")
            return redirect(url_for('restricted_access'))
            
        return f(*args, **kwargs)
    
    return decorated_function

def validate_billing_country(billing_country):
    """
    Validate that the billing country is not restricted.
    Used during checkout to prevent users from restricted countries.
    
    Args:
        billing_country (str): The country code from the billing address
        
    Returns:
        tuple: (is_valid, message) where is_valid is a boolean and message is an error message if invalid
    """
    if is_country_restricted(billing_country):
        return False, f"We do not currently provide services in {billing_country}. Please contact support for assistance."
    
    return True, ""

def get_allowed_countries():
    """
    Get a list of allowed countries for Stripe checkout.
    This excludes all restricted countries.
    
    Returns:
        list: List of country codes that are allowed
    """
    # This is a simplified list - in a real application, you'd have a complete list of countries
    ALL_COUNTRIES = [
        'US', 'CA', 'GB', 'DE', 'FR', 'IT', 'ES', 'AU', 'NZ', 'JP', 'SG', 'HK',
        'MY', 'IN', 'AE', 'SA', 'ZA', 'NG', 'EG', 'IL', 'TR', 'MX', 'AR', 'CO',
        'CL', 'PE', 'VE', 'TH', 'ID', 'PH', 'VN', 'TW', 'KZ', 'UA', 'SE', 'NO',
        'DK', 'FI', 'NL', 'BE', 'CH', 'AT', 'PL', 'CZ', 'SK', 'HU', 'RO', 'BG',
        'GR', 'PT', 'IE', 'UY', 'PR', 'PY', 'EC', 'BO', 'JM', 'TT', 'BS', 'BB',
        'CR', 'PA', 'DO', 'HN', 'GT', 'SV', 'NI'
    ]
    
    # No need to filter since we're not including restricted countries in the list above
    return ALL_COUNTRIES