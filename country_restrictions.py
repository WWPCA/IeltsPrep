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

# Configuration settings for regional blocking
# Set this to False to allow EU/UK access (when GDPR compliance is implemented)
BLOCK_EU_UK = True

# List of EU/UK country codes (used for regulatory compliance)
# ISO 3166-1 alpha-2 country codes (2 letter codes)
EU_UK_COUNTRIES = [
    'AT',  # Austria
    'BE',  # Belgium
    'BG',  # Bulgaria
    'HR',  # Croatia
    'CY',  # Cyprus
    'CZ',  # Czech Republic
    'DK',  # Denmark
    'EE',  # Estonia
    'FI',  # Finland
    'FR',  # France
    'DE',  # Germany
    'GR',  # Greece
    'HU',  # Hungary
    'IE',  # Ireland
    'IT',  # Italy
    'LV',  # Latvia
    'LT',  # Lithuania
    'LU',  # Luxembourg
    'MT',  # Malta
    'NL',  # Netherlands
    'PL',  # Poland
    'PT',  # Portugal
    'RO',  # Romania
    'SK',  # Slovakia
    'SI',  # Slovenia
    'ES',  # Spain
    'SE',  # Sweden
    'GB',  # Great Britain
    'UK',  # United Kingdom (redundant with GB, but included for completeness)
]

# List of explicitly allowed countries (whitelisted)
# ISO 3166-1 alpha-2 country codes (2 letter codes)
ALLOWED_COUNTRIES = [
    'US',  # United States
    'CA',  # Canada
    'IN',  # India
    'NP',  # Nepal
    'KW',  # Kuwait
    'QA',  # Qatar
]

# List of country codes that are restricted from accessing the application for other reasons 
# This is kept for backwards compatibility, but we now primarily use the allowlist approach
# ISO 3166-1 alpha-2 country codes (2 letter codes)
RESTRICTED_COUNTRIES = [
    'BR',  # Brazil
    'RU',  # Russia
    'CN',  # China
    'KR',  # South Korea
    'AF',  # Afghanistan
]

# Standardized message for all blocked countries (both EU/UK and other regions)
RESTRICTION_MESSAGE = (
    "We're sorry, but our services are not available in your region due to regulatory requirements. "
    "We're working to expand our coverage. Thank you for your understanding."
)

def is_country_restricted(country_code):
    """
    Check if a country is restricted (not in the allowed list).
    
    Args:
        country_code (str): ISO 3166-1 alpha-2 country code
        
    Returns:
        bool: True if the country is restricted, False otherwise
    """
    if not country_code:
        return False
    
    country_code = country_code.upper()
    
    # First check if the country is explicitly allowed
    if country_code in ALLOWED_COUNTRIES:
        return False
        
    # Otherwise, it's restricted
    return True

def is_eu_uk_country(country_code):
    """
    Check if a country is in the EU/UK list.
    
    Args:
        country_code (str): ISO 3166-1 alpha-2 country code
        
    Returns:
        bool: True if the country is in EU/UK, False otherwise
    """
    if not country_code:
        return False
        
    return country_code.upper() in EU_UK_COUNTRIES
    
def is_country_blocked(country_code):
    """
    Check if a country is blocked for any reason (not allowed or EU/UK).
    
    Args:
        country_code (str): ISO 3166-1 alpha-2 country code
        
    Returns:
        tuple: (is_blocked, reason) where reason is 'restricted' or 'eu_uk' or None
    """
    if not country_code:
        return (False, None)
    
    country_code = country_code.upper()
    
    # Check if country is explicitly allowed first
    if country_code in ALLOWED_COUNTRIES:
        return (False, None)
    
    # Check EU/UK restrictions separately (for different error message)
    if BLOCK_EU_UK and country_code in EU_UK_COUNTRIES:
        return (True, 'eu_uk')
    
    # All other countries not in ALLOWED_COUNTRIES are restricted by default
    return (True, 'restricted')

def country_access_required(f):
    """
    Decorator to restrict access based on country.
    Redirects to a restriction page if the user's country is restricted or blocked.
    
    Usage:
        @app.route('/some-route')
        @country_access_required
        def some_view():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if there's already a country code in the session (for simulations)
        country_code = session.get('country_code')
        
        # If no simulated country, get the real country from IP
        if not country_code or not session.get('simulated_country'):
            from geoip_services import get_country_from_ip
            
            # Get the user's country code
            detected_country, _ = get_country_from_ip()
            
            # Store the country code in the session for future reference
            if detected_country:
                session['country_code'] = detected_country
                country_code = detected_country
        
        # Check if the country is blocked for any reason
        is_blocked, reason = is_country_blocked(country_code)
        if is_blocked:
            # Log with specific reason for internal tracking, but use standard message for user
            if reason == 'eu_uk':
                logger.info(f"Blocked access from EU/UK region: {country_code}")
            else:
                logger.info(f"Blocked access from restricted country: {country_code}")
                
            # Use standardized message for all blocked countries
            flash(RESTRICTION_MESSAGE, "warning")
                
            # Store the reason in session for the restriction page (for admin reference)
            session['restriction_reason'] = reason
            return redirect(url_for('restricted_access'))
            
        return f(*args, **kwargs)
    
    return decorated_function

def validate_billing_country(billing_country):
    """
    Validate that the billing country is in our allowed list.
    Used during checkout to prevent users from non-allowed countries.
    
    Args:
        billing_country (str): The country code from the billing address
        
    Returns:
        tuple: (is_valid, message) where is_valid is a boolean and message is an error message if invalid
    """
    if not billing_country:
        return False, "Billing country information is required."
    
    billing_country = billing_country.upper()
    
    # Check if the country is in our allowed list
    if billing_country in ALLOWED_COUNTRIES:
        return True, ""
    
    # Standardized message for all non-allowed countries
    return False, RESTRICTION_MESSAGE

def get_allowed_countries():
    """
    Get a list of allowed countries for Stripe checkout.
    Returns our explicitly allowed countries list.
    
    Returns:
        list: List of country codes that are allowed
    """
    # Return the explicitly defined allowed countries
    return ALLOWED_COUNTRIES
    
def is_country_allowed(country_code):
    """
    Check if a country is in the allowed list for Stripe checkout.
    
    Args:
        country_code (str): ISO 3166-1 alpha-2 country code
        
    Returns:
        bool: True if the country is in the allowed list, False otherwise
    """
    if not country_code:
        return False  # If no country code is provided, don't allow it by default
        
    return country_code.upper() in ALLOWED_COUNTRIES