"""
Custom reCAPTCHA v3 implementation for IELTS GenAI Prep application.
This helper works with invisible reCAPTCHA v3 to provide protection against bots.
"""

import os
import requests
from flask import request

class ReCaptchaV3:
    """Simple reCAPTCHA v3 implementation for Flask applications."""
    
    VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"
    
    def __init__(self, app=None):
        self.site_key = None
        self.secret_key = None
        self.is_enabled = False
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app instance"""
        self.site_key = app.config.get("RECAPTCHA_SITE_KEY", "")
        self.secret_key = app.config.get("RECAPTCHA_SECRET_KEY", "")
        self.is_enabled = bool(self.site_key and self.secret_key)
        
        # Register context processor to make site_key available in templates
        @app.context_processor
        def inject_recaptcha():
            return dict(recaptcha_site_key=self.site_key)
    
    def verify(self, response=None, remote_ip=None, action=None, min_score=0.5):
        """
        Verify the reCAPTCHA response
        
        Args:
            response (str, optional): The g-recaptcha-response token from the form
            remote_ip (str, optional): Remote IP address, defaults to request.remote_addr
            action (str, optional): Expected action name to verify
            min_score (float, optional): Minimum score threshold (0.0-1.0), defaults to 0.5
            
        Returns:
            dict: Verification result with keys 'success', 'score', 'action'
        """
        if not self.is_enabled:
            # If reCAPTCHA is not enabled, always return success
            return {'success': True, 'score': 1.0, 'action': action or 'default'}
        
        if not response:
            # Try to get the token from the form submission
            response = request.form.get('g-recaptcha-response')
            
        if not response:
            # No token found
            return {'success': False, 'score': 0.0, 'action': None, 'error': 'Missing reCAPTCHA response'}
        
        # Prepare verification data
        verify_data = {
            'secret': self.secret_key,
            'response': response,
            'remoteip': remote_ip or request.remote_addr
        }
        
        try:
            # Send verification request to Google
            r = requests.post(self.VERIFY_URL, data=verify_data)
            result = r.json()
            
            # Check basic success
            if not result.get('success', False):
                return {
                    'success': False, 
                    'score': 0.0, 
                    'action': None,
                    'error': result.get('error-codes', ['verification-failed'])
                }
            
            # Get score and action from result
            score = result.get('score', 0.0)
            response_action = result.get('action', '')
            
            # Check score threshold
            if score < min_score:
                return {
                    'success': False,
                    'score': score,
                    'action': response_action,
                    'error': 'Score too low'
                }
            
            # Check action match if specified
            if action and action != response_action:
                return {
                    'success': False,
                    'score': score,
                    'action': response_action,
                    'error': 'Action mismatch'
                }
            
            # All checks passed
            return {
                'success': True,
                'score': score,
                'action': response_action
            }
            
        except Exception as e:
            return {
                'success': False,
                'score': 0.0,
                'action': None,
                'error': str(e)
            }