"""
GeoIP service for detecting user's country based on IP address.
"""

import os
import json
import requests
from flask import request, session
import logging

logger = logging.getLogger(__name__)

# Different GeoIP service options
IP_API_URL = "http://ip-api.com/json/{}"  # Free tier with limited requests
IPINFO_API_URL = "https://ipinfo.io/{}/json"  # Commercial service with API key

def get_country_from_ip(ip_address=None):
    """
    Get the country code from an IP address using various GeoIP services.
    Falls back to different services if the primary one fails.
    
    Args:
        ip_address (str, optional): IP address to look up. If None, uses the current request's IP.
        
    Returns:
        tuple: (country_code, country_name) or (None, None) if detection fails
    """
    # Use session-based caching to avoid repeated lookups
    if 'country_code' in session and 'country_name' in session:
        return session['country_code'], session['country_name']
        
    if not ip_address:
        # Get IP from request headers, respecting proxies
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ip_address:
            ip_address = ip_address.split(',')[0].strip()
    
    if not ip_address:
        logger.warning("No IP address found in request")
        return None, None
        
    # Try IPInfo.io if API key is available
    ipinfo_api_key = os.environ.get('IPINFO_API_KEY')
    if ipinfo_api_key:
        try:
            response = requests.get(
                IPINFO_API_URL.format(ip_address),
                headers={"Authorization": f"Bearer {ipinfo_api_key}"},
                timeout=3
            )
            if response.status_code == 200:
                data = response.json()
                country_code = data.get('country')
                # Get country name from country code or use "Unknown" as fallback
                country_name = data.get('country_name', get_country_name_from_code(country_code))
                
                # Store in session for future requests
                if country_code:
                    session['country_code'] = country_code
                    session['country_name'] = country_name
                    
                return country_code, country_name
        except Exception as e:
            logger.error(f"IPInfo.io API error: {str(e)}")
    
    # Fall back to free IP-API service (limited to 45 requests per minute)
    try:
        response = requests.get(IP_API_URL.format(ip_address), timeout=3)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                country_code = data.get('countryCode')
                country_name = data.get('country')
                
                # Store in session for future requests
                if country_code:
                    session['country_code'] = country_code
                    session['country_name'] = country_name
                    
                return country_code, country_name
    except Exception as e:
        logger.error(f"IP-API error: {str(e)}")
    
    # Fallback to Accept-Language header for a rough guess
    accept_language = request.headers.get('Accept-Language', '')
    if accept_language:
        try:
            # Parse language code (e.g., 'en-US,en;q=0.9')
            # Only a rough approximation as language doesn't always correspond to country
            lang_code = accept_language.split(',')[0].split('-')
            if len(lang_code) > 1:
                country_code = lang_code[1].upper()
                country_name = get_country_name_from_code(country_code)
                return country_code, country_name
        except Exception as e:
            logger.error(f"Accept-Language parsing error: {str(e)}")
    
    # Return None if all methods fail
    return None, None

def get_country_name_from_code(country_code):
    """
    Convert a country code to a country name using a simplified mapping.
    
    Args:
        country_code (str): Two-letter country code
        
    Returns:
        str: Country name or "Unknown Country" if not found
    """
    # This is a simplified mapping - in production, use a complete country code database
    country_mapping = {
        "US": "United States",
        "CA": "Canada",
        "GB": "United Kingdom",
        "AU": "Australia",
        "NZ": "New Zealand",
        "SG": "Singapore", 
        "JP": "Japan",
        "KR": "South Korea",
        "CN": "China",
        "IN": "India",
        "BR": "Brazil",
        "MX": "Mexico",
        "RU": "Russia",
        "TR": "Turkey",
        "TH": "Thailand",
        "MY": "Malaysia",
        "PH": "Philippines",
        "VN": "Vietnam",
        "ID": "Indonesia",
        "EG": "Egypt", 
        "PK": "Pakistan",
        "NG": "Nigeria",
        "KE": "Kenya",
        "ET": "Ethiopia",
        "TZ": "Tanzania",
        "BD": "Bangladesh",
        "NP": "Nepal",
        "AE": "United Arab Emirates",
        "SA": "Saudi Arabia",
    }
    
    return country_mapping.get(country_code, "Unknown Country")

def get_pricing_for_country(country_code=None):
    """
    Get the appropriate pricing for a country.
    
    Args:
        country_code (str, optional): Two-letter country code. If None, detects from IP.
        
    Returns:
        dict: Pricing information for the country
    """
    from models import CountryPricing
    
    if not country_code:
        country_code, _ = get_country_from_ip()
    
    try:
        # Try to get pricing for specific country
        pricing = CountryPricing.query.filter_by(country_code=country_code).first()
        
        # Fall back to default pricing if country-specific pricing not found
        if not pricing:
            pricing = CountryPricing.query.filter_by(is_default=True).first()
            
        # Create a dictionary with pricing information
        if pricing:
            return {
                'country_code': pricing.country_code,
                'country_name': pricing.country_name,
                'monthly_price': pricing.monthly_price,
                'quarterly_price': pricing.quarterly_price,
                'yearly_price': pricing.yearly_price,
                'is_default': pricing.is_default
            }
    except Exception as e:
        logger.error(f"Error getting pricing for country {country_code}: {str(e)}")
    
    # Fallback to default pricing if database query fails
    return {
        'country_code': 'US',
        'country_name': 'United States',
        'monthly_price': 14.99,
        'quarterly_price': 39.99,
        'yearly_price': 149.99,
        'is_default': True
    }