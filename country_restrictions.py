"""
Country Access Restrictions
Implements Canada-only access control with IP-based country detection,
billing validation, and session management as per technical review recommendations.
"""

import os
import hashlib
import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import request, session, flash, redirect, url_for, jsonify
from geoip2 import webservice
import geoip2.errors

# Configure logging
logger = logging.getLogger(__name__)

# Configuration
ALLOWED_COUNTRIES = {'CA'}  # Canada-only for initial launch
GEOIP_LICENSE_KEY = os.environ.get('GEOIP_LICENSE_KEY')
SESSION_VALIDATION_INTERVAL = timedelta(hours=1)

# Standard restriction message for consistency
RESTRICTION_MESSAGE = "Access is currently limited to Canada only. Thank you for your interest in IELTS GenAI Prep."

class CountryRestrictionManager:
    """Manages country-based access restrictions with fallback mechanisms"""
    
    def __init__(self):
        self.geoip_client = None
        if GEOIP_LICENSE_KEY:
            try:
                self.geoip_client = webservice.Client(12345, GEOIP_LICENSE_KEY)  # Replace with actual account ID
                logger.info("GeoIP2 service initialized successfully")
            except Exception as e:
                logger.warning(f"GeoIP2 initialization failed: {e}")
    
    def get_user_country(self, ip_address):
        """
        Get user's country with fallback mechanisms
        
        Args:
            ip_address (str): User's IP address
            
        Returns:
            str: Country code or None if detection fails
        """
        try:
            # First try GeoIP2 service
            if self.geoip_client:
                try:
                    response = self.geoip_client.country(ip_address)
                    country_code = response.country.iso_code
                    logger.info(f"Country detected via GeoIP2: {country_code}")
                    return country_code
                except geoip2.errors.AddressNotFoundError:
                    logger.warning(f"IP lookup failed for {ip_address}")
                except Exception as e:
                    logger.error(f"GeoIP2 service error: {e}")
            
            # Fallback to basic detection for development
            if ip_address in ['127.0.0.1', 'localhost', '::1']:
                logger.info("Local development environment detected")
                return 'CA'  # Allow local development
            
            # Log failed detection
            logger.warning(f"Country detection failed for IP: {self._hash_ip(ip_address)}")
            return None
            
        except Exception as e:
            logger.error(f"Country detection error: {e}")
            return None
    
    def _hash_ip(self, ip_address):
        """Hash IP address for privacy-compliant logging"""
        salt = os.environ.get("IP_HASH_SALT", "default_salt_change_in_production")
        return hashlib.sha256((ip_address + salt).encode()).hexdigest()[:16]
    
    def is_country_restricted(self, country_code):
        """
        Check if country is restricted
        
        Args:
            country_code (str): ISO country code
            
        Returns:
            bool: True if restricted, False if allowed
        """
        if not country_code:
            return True  # Restrict if country cannot be determined
        
        return country_code not in ALLOWED_COUNTRIES
    
    def validate_country_session(self, request_obj):
        """
        Validate country session with periodic refresh
        
        Args:
            request_obj: Flask request object
            
        Returns:
            tuple: (is_allowed, error_message)
        """
        try:
            current_time = datetime.utcnow()
            
            # Check if we need to refresh country validation
            last_validated = session.get('country_validated_at')
            if (not last_validated or 
                current_time - datetime.fromisoformat(last_validated) > SESSION_VALIDATION_INTERVAL):
                
                # Refresh country detection
                country_code = self.get_user_country(request_obj.remote_addr)
                session['country_code'] = country_code
                session['country_validated_at'] = current_time.isoformat()
                
                logger.info("Country session refreshed", 
                           extra={'country_code': country_code, 
                                  'ip_hash': self._hash_ip(request_obj.remote_addr)})
            
            country_code = session.get('country_code')
            
            if self.is_country_restricted(country_code):
                error_message = self.get_restriction_message(country_code)
                logger.warning("Access denied for restricted country", 
                             extra={'country_code': country_code})
                return False, error_message
            
            return True, None
            
        except Exception as e:
            logger.error(f"Country session validation error: {e}")
            return False, "Access validation failed"
    
    def get_restriction_message(self, country_code):
        """
        Get appropriate restriction message based on region
        
        Args:
            country_code (str): ISO country code
            
        Returns:
            str: User-friendly restriction message
        """
        if country_code in {'GB', 'IE'}:
            return ("Access is currently limited to Canada only. "
                   "We're working on expanding to additional regions.")
        elif country_code and country_code.startswith('EU'):
            return ("Access is currently limited to Canada only. "
                   "We're working on GDPR compliance for EU access.")
        else:
            return ("Access is currently limited to Canada only. "
                   "Thank you for your interest in IELTS GenAI Prep.")
    
    def validate_billing_country(self, billing_country, stripe_payment_intent=None):
        """
        Validate billing address country with Stripe integration
        
        Args:
            billing_country (str): Billing country code
            stripe_payment_intent (dict, optional): Stripe payment intent data
            
        Returns:
            bool: True if valid Canadian billing address
        """
        try:
            if billing_country != 'CA':
                logger.warning(f"Non-Canadian billing country: {billing_country}")
                return False
            
            # Additional validation with Stripe if available
            if stripe_payment_intent:
                stripe_country = stripe_payment_intent.get('charges', {}).get('data', [{}])[0].get('billing_details', {}).get('address', {}).get('country')
                if stripe_country and stripe_country != 'CA':
                    logger.warning(f"Stripe billing country mismatch: {stripe_country}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Billing validation error: {e}")
            return False

# Global instance
country_manager = CountryRestrictionManager()

def country_access_required(f):
    """
    Decorator to enforce country access restrictions
    
    Usage:
        @app.route('/assessment-products')
        @country_access_required
        def assessment_products():
            return render_template('assessment_products.html')
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        is_allowed, message = country_manager.validate_country_session(request)
        
        if not is_allowed:
            error_message = message if message else RESTRICTION_MESSAGE
            if request.is_json:
                return jsonify({
                    'success': False,
                    'error': error_message,
                    'restricted': True
                }), 403
            else:
                flash(error_message, 'warning')
                return redirect(url_for('index'))
        
        return f(*args, **kwargs)
    
    return decorated_function

def get_user_country_info():
    """
    Get current user's country information from session
    
    Returns:
        dict: Country information including code and validation status
    """
    return {
        'country_code': session.get('country_code'),
        'is_restricted': country_manager.is_country_restricted(session.get('country_code')),
        'validated_at': session.get('country_validated_at'),
        'allowed_countries': list(ALLOWED_COUNTRIES)
    }

def check_country_access(ip_address=None):
    """
    Check country access without session storage (for API endpoints)
    
    Args:
        ip_address (str, optional): IP address to check
        
    Returns:
        dict: Access status and details
    """
    try:
        ip_address = ip_address or request.remote_addr
        country_code = country_manager.get_user_country(ip_address)
        is_restricted = country_manager.is_country_restricted(country_code)
        
        return {
            'allowed': not is_restricted,
            'country_code': country_code,
            'message': country_manager.get_restriction_message(country_code) if is_restricted else None
        }
        
    except Exception as e:
        logger.error(f"Country access check error: {e}")
        return {
            'allowed': False,
            'country_code': None,
            'message': 'Access validation failed'
        }

# Legacy function compatibility for existing imports
def is_country_restricted(country_code):
    """
    Legacy function for backwards compatibility
    
    Args:
        country_code (str): ISO country code
        
    Returns:
        bool: True if country is restricted
    """
    return country_manager.is_country_restricted(country_code)

def get_allowed_countries():
    """
    Get list of allowed countries
    
    Returns:
        list: List of allowed country codes
    """
    return list(ALLOWED_COUNTRIES)

def validate_billing_country(billing_country):
    """
    Legacy function for billing validation
    
    Args:
        billing_country (str): Billing country code
        
    Returns:
        bool: True if valid
    """
    return country_manager.validate_billing_country(billing_country)