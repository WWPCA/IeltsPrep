"""
Payment country check integration.
This module updates the payment_services.py to handle simulated countries.
"""
import logging
from flask import session

def get_effective_country_code(provided_country_code=None):
    """
    Get the effective country code by checking both the session (for simulations)
    and the provided country code parameter.
    
    Args:
        provided_country_code (str, optional): Country code provided to the function
        
    Returns:
        tuple: (country_code, is_simulated) where:
            - country_code is the effective country code to use
            - is_simulated is a boolean indicating if this is a simulated country
    """
    # Check for simulated country in session
    session_country = session.get('country_code')
    is_simulated = session.get('simulated_country', False)
    
    if session_country and is_simulated:
        return session_country, True
    
    # Otherwise use the provided country code
    return provided_country_code, False

def check_country_restriction(country_code, is_country_restricted_func):
    """
    Check if a country is restricted, considering both real and simulated countries.
    
    Args:
        country_code (str): The country code to check
        is_country_restricted_func (function): Function to check if a country is restricted
        
    Returns:
        None if country is allowed, raises ValueError if country is restricted
    """
    # Check effective country code (real or simulated)
    effective_country, is_simulated = get_effective_country_code(country_code)
    
    if effective_country and is_country_restricted_func(effective_country):
        if is_simulated:
            logging.warning(f"Attempted checkout from simulated restricted country: {effective_country}")
            raise ValueError(f"We do not provide services in your simulated region ({effective_country}) due to regulatory requirements.")
        else:
            logging.warning(f"Attempted checkout from restricted country: {effective_country}")
            raise ValueError(f"We do not provide services in your region ({effective_country}) due to regulatory requirements.")