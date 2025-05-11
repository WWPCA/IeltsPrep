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

# List of country codes that are restricted from accessing the application for other reasons
# ISO 3166-1 alpha-2 country codes (2 letter codes)
RESTRICTED_COUNTRIES = [
    'BR',  # Brazil
    'RU',  # Russia
    'CN',  # China
    'KR',  # South Korea
]

# Message to display to users from generally restricted countries
RESTRICTION_MESSAGE = (
    "We're sorry, but our services are not available in your region due to regulatory requirements. "
    "We're working to expand our coverage. Thank you for your understanding."
)

# Message to display to users from EU/UK (different reason - GDPR compliance)
EU_UK_RESTRICTION_MESSAGE = (
    "We're sorry, but our services are not currently available in European Union and United Kingdom regions. "
    "We're working to implement enhanced data protection features to serve these regions in the future."
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
    Check if a country is blocked for any reason (restricted or EU/UK).
    
    Args:
        country_code (str): ISO 3166-1 alpha-2 country code
        
    Returns:
        tuple: (is_blocked, reason) where reason is 'restricted' or 'eu_uk' or None
    """
    if not country_code:
        return (False, None)
    
    country_code = country_code.upper()
    
    # Check general restrictions first
    if country_code in RESTRICTED_COUNTRIES:
        return (True, 'restricted')
    
    # Check EU/UK restrictions if enabled
    if BLOCK_EU_UK and country_code in EU_UK_COUNTRIES:
        return (True, 'eu_uk')
    
    return (False, None)

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
            if reason == 'eu_uk':
                logger.info(f"Blocked access from EU/UK region: {country_code}")
                flash(EU_UK_RESTRICTION_MESSAGE, "warning")
            else:
                logger.info(f"Blocked access from restricted country: {country_code}")
                flash(RESTRICTION_MESSAGE, "warning")
                
            # Store the reason in session for the restriction page
            session['restriction_reason'] = reason
            return redirect(url_for('restricted_access'))
            
        return f(*args, **kwargs)
    
    return decorated_function

def validate_billing_country(billing_country):
    """
    Validate that the billing country is not restricted or blocked.
    Used during checkout to prevent users from restricted/blocked countries.
    
    Args:
        billing_country (str): The country code from the billing address
        
    Returns:
        tuple: (is_valid, message) where is_valid is a boolean and message is an error message if invalid
    """
    is_blocked, reason = is_country_blocked(billing_country)
    
    if is_blocked:
        if reason == 'eu_uk':
            return False, f"Due to data protection requirements, we do not currently provide services in {billing_country}. We're working to serve these regions in the future."
        else:
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
    
    # Filter out restricted countries
    allowed_countries = [country for country in ALL_COUNTRIES if country not in RESTRICTED_COUNTRIES]
    return allowed_countries
    
def is_country_allowed(country_code):
    """
    Check if a country is allowed for Stripe checkout.
    
    Args:
        country_code (str): ISO 3166-1 alpha-2 country code
        
    Returns:
        bool: True if the country is allowed, False if it's restricted
    """
    if not country_code:
        return True  # If no country code is provided, allow it
        
    return country_code.upper() not in RESTRICTED_COUNTRIES