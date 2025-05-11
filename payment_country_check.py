"""
Payment country check integration.
This module updates the payment_services.py to handle simulated countries.
"""
import logging
from flask import session, has_request_context

def get_effective_country_code(provided_country_code=None, session_dict=None):
    """
    Get the effective country code by checking both the session (for simulations)
    and the provided country code parameter.
    
    Args:
        provided_country_code (str, optional): Country code provided to the function
        session_dict (dict, optional): Session dict for testing (bypasses Flask session)
        
    Returns:
        tuple: (country_code, is_simulated) where:
            - country_code is the effective country code to use
            - is_simulated is a boolean indicating if this is a simulated country
    """
    # Use provided session dict for testing or Flask session in request context
    session_data = session_dict if session_dict is not None else session if has_request_context() else {}
    
    # Check if we have a simulated country in the session
    if session_data.get('simulated_country') and session_data.get('country_code'):
        # Use the simulated country from the session
        simulated_country = session_data.get('country_code')
        logging.info(f"Using simulated country from session: {simulated_country}")
        return simulated_country, True
    
    # Otherwise, use the provided country code
    return provided_country_code, False

def check_country_restriction(country_code, is_country_restricted_func, session_dict=None):
    """
    Check if a country is restricted, considering both real and simulated countries.
    
    Args:
        country_code (str): The country code to check
        is_country_restricted_func (function): Function to check if a country is restricted
        session_dict (dict, optional): Session dict for testing (bypasses Flask session)
        
    Returns:
        None if country is allowed, raises ValueError if country is restricted
    """
    if not country_code:
        # No country code provided, cannot check restrictions
        return
    
    # Get the effective country code (considering simulations)
    effective_country_code, is_simulated = get_effective_country_code(
        country_code, session_dict=session_dict
    )
    
    # Check if the effective country is restricted
    if effective_country_code and is_country_restricted_func(effective_country_code):
        simulation_note = " (simulated)" if is_simulated else ""
        logging.warning(f"Attempted checkout from restricted country: {effective_country_code}{simulation_note}")
        raise ValueError(f"We do not provide services in your region ({effective_country_code}) due to regulatory requirements.")