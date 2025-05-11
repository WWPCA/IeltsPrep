"""
Country Access Control Module

This module implements country-based access control,
allowing access only to users from approved countries.
"""

import json
import logging
import os
import urllib.request
import time
import functools
import ipaddress
from datetime import datetime, timedelta
from flask import request, redirect, url_for, flash, session, render_template
from flask_login import current_user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global cache for IP to country lookups to reduce API calls
IP_COUNTRY_CACHE = {}
CACHE_EXPIRY = 24 * 60 * 60  # 24 hours in seconds

# List of allowed country codes
ALLOWED_COUNTRIES = ['CA', 'US', 'IN', 'NP', 'KW', 'QA']

# List of explicitly blocked countries (EU countries and UK for GDPR/regulatory reasons)
EU_COUNTRIES = [
    'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 
    'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 
    'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE'
]
BLOCKED_COUNTRIES = EU_COUNTRIES + ['GB']  # GB is UK

# Internal network ranges that should bypass restrictions
INTERNAL_NETWORKS = [
    '10.0.0.0/8',      # Private network
    '172.16.0.0/12',   # Private network
    '192.168.0.0/16',  # Private network
    '127.0.0.0/8',     # Localhost
]

def is_internal_ip(ip):
    """Check if an IP address is from an internal network"""
    try:
        ip_obj = ipaddress.ip_address(ip)
        for network in INTERNAL_NETWORKS:
            if ip_obj in ipaddress.ip_network(network):
                return True
        return False
    except ValueError:
        # If IP is invalid, assume it's not internal
        return False

def get_country_code(ip_address):
    """
    Get the country code for a given IP address.
    Uses caching to reduce API calls.
    
    Args:
        ip_address (str): The IP address to check
        
    Returns:
        str: Two-letter country code or None if not found
    """
    # Return from cache if available and not expired
    if ip_address in IP_COUNTRY_CACHE:
        cache_time, country_code = IP_COUNTRY_CACHE[ip_address]
        if time.time() - cache_time < CACHE_EXPIRY:
            return country_code
    
    # Skip IP check for internal IPs (for development)
    if is_internal_ip(ip_address):
        logger.info(f"Internal IP detected: {ip_address}. Allowing access.")
        return ALLOWED_COUNTRIES[0]  # Return first allowed country for internal IPs
    
    try:
        # Try ip-api.com first (no API key required, 45 requests per minute limit)
        response = urllib.request.urlopen(f'http://ip-api.com/json/{ip_address}')
        data = json.loads(response.read().decode())
        
        if data.get('status') == 'success':
            country_code = data.get('countryCode')
            # Cache the result
            IP_COUNTRY_CACHE[ip_address] = (time.time(), country_code)
            return country_code
        
        # If ip-api fails, could add fallback services here
        logger.warning(f"Could not determine country for IP {ip_address}")
        return None
        
    except Exception as e:
        logger.error(f"Error determining country for IP {ip_address}: {str(e)}")
        return None

def is_country_allowed(country_code):
    """
    Check if a country is in the allowed list.
    
    Args:
        country_code (str): Two-letter country code
        
    Returns:
        bool: True if country is allowed, False otherwise
    """
    return country_code in ALLOWED_COUNTRIES

def is_country_explicitly_blocked(country_code):
    """
    Check if a country is explicitly blocked (e.g., for regulatory reasons).
    
    Args:
        country_code (str): Two-letter country code
        
    Returns:
        bool: True if country is explicitly blocked, False otherwise
    """
    return country_code in BLOCKED_COUNTRIES

def log_access_attempt(ip_address, country_code, allowed):
    """
    Log access attempts for auditing purposes.
    
    Args:
        ip_address (str): The IP address attempting access
        country_code (str): The detected country code
        allowed (bool): Whether access was allowed
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists('access_logs'):
        os.makedirs('access_logs')
    
    # Get current date for log file name
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = f'access_logs/country_access_{today}.log'
    
    # Log the access attempt
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"{timestamp}|{ip_address}|{country_code}|{'ALLOWED' if allowed else 'BLOCKED'}\n"
    
    with open(log_file, 'a') as f:
        f.write(log_entry)

def country_access_required(view_function):
    """
    Decorator to restrict access to allowed countries only.
    This should be applied to views that require country restriction.
    
    Usage:
        @app.route('/some-route')
        @country_access_required
        def some_view():
            # This will only run if country is allowed
    """
    @functools.wraps(view_function)
    def decorated_function(*args, **kwargs):
        # Check if country restriction is already verified in this session
        if session.get('country_verified') == True:
            return view_function(*args, **kwargs)
        
        # Get client IP address
        ip_address = request.remote_addr
        
        # Handle proxied requests (common in production)
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for and isinstance(forwarded_for, str):
            ip_address = forwarded_for.split(',')[0].strip()
        
        # Get country from IP
        country_code = get_country_code(ip_address)
        
        # If country couldn't be determined, block access
        if not country_code:
            log_access_attempt(ip_address, 'UNKNOWN', False)
            return redirect(url_for('access_restricted_page', reason='unknown'))
        
        # Check if country is explicitly blocked (e.g., EU/UK for GDPR)
        if is_country_explicitly_blocked(country_code):
            log_access_attempt(ip_address, country_code, False)
            return redirect(url_for('access_restricted_page', reason='regulatory'))
        
        # Check if country is allowed
        if is_country_allowed(country_code):
            # Set verified flag in session
            session['country_verified'] = True
            session['country_code'] = country_code
            log_access_attempt(ip_address, country_code, True)
            return view_function(*args, **kwargs)
        else:
            log_access_attempt(ip_address, country_code, False)
            return redirect(url_for('access_restricted_page', reason='not_available'))
    
    return decorated_function

def setup_country_restriction_routes(app):
    """
    Set up the routes needed for country restriction.
    This function should be called from your app initialization.
    
    Args:
        app: Flask application instance
    """
    @app.route('/access-restricted')
    def access_restricted_page():
        reason = request.args.get('reason', 'unknown')
        
        if reason == 'regulatory':
            message = "Access Restricted for Regulatory Compliance"
            description = (
                "We're sorry, but our service is not currently available in your region due to "
                "regulatory requirements. We're working to expand our service area and hope to "
                "be able to serve you in the future."
            )
        elif reason == 'not_available':
            message = "Service Not Available in Your Region"
            description = (
                "We're sorry, but our service is not yet available in your country. "
                "We're working to expand our service area in the future."
            )
        else:
            message = "Access Restricted"
            description = (
                "We're unable to verify your location. Our service is currently only available "
                "in specific regions. Please try again later or contact support if you believe "
                "this is an error."
            )
        
        return render_template(
            'access_restricted.html',
            message=message,
            description=description,
            reason=reason
        )
        
    @app.before_request
    def check_country_verification_age():
        """Periodically recheck country to handle cases like travel"""
        if session.get('country_verified'):
            # If verification is more than a week old, reverify
            last_verified = session.get('country_verified_at')
            if not last_verified or datetime.fromtimestamp(last_verified) < datetime.now() - timedelta(days=7):
                session.pop('country_verified', None)
                session.pop('country_code', None)
                session['country_verified_at'] = time.time()
                
    @app.context_processor
    def inject_country_code():
        """Make country code available to all templates"""
        return {'user_country_code': session.get('country_code')}

def apply_country_restrictions(app):
    """
    Apply country restrictions to all relevant routes in the application.
    This function applies the country_access_required decorator to all routes
    that should be restricted.
    
    Args:
        app: Flask application instance
    """
    # Set up the restriction routes
    setup_country_restriction_routes(app)
    
    # Get a list of all routes in the app
    routes = [str(rule) for rule in app.url_map.iter_rules()]
    
    # Exempt these routes from country restrictions
    exempt_routes = [
        '/access-restricted',
        '/static/<path:filename>',
        '/favicon.ico',
        '/health',
        '/robots.txt',
        '/sitemap.xml'
    ]
    
    # Apply country restrictions to all non-exempt routes
    for endpoint, view_func in app.view_functions.items():
        # Skip endpoints that don't have a route or are exempt
        skip_endpoint = False
        
        # Skip static endpoints
        if endpoint == 'static':
            skip_endpoint = True
        
        # Check exempt routes
        for route in routes:
            # Safely check if route starts with endpoint
            if endpoint and route.startswith('/' + endpoint):
                # Check if this route matches any exempt routes
                for exempt_route in exempt_routes:
                    if route.startswith(exempt_route):
                        skip_endpoint = True
                        break
        
        if skip_endpoint:
            continue
        
        # Wrap the view function with country_access_required
        app.view_functions[endpoint] = country_access_required(view_func)
    
    logger.info("Country restrictions applied to all relevant routes")