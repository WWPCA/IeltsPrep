"""
Comprehensive Input Validation System
This module provides secure input validation for all user inputs across the application.
"""

import re
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from functools import wraps
from flask import request, jsonify

class InputValidator:
    """Comprehensive input validation class"""
    
    @staticmethod
    def validate_email(email: Optional[str]) -> bool:
        """Validate email format"""
        if not email or len(email) > 120:
            return False
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email) is not None
    
    @staticmethod
    def validate_password(password: Optional[str]) -> Dict[str, Any]:
        """
        Validate password strength
        Returns: dict with 'valid' bool and 'errors' list
        """
        errors = []
        
        if not password:
            errors.append("Password is required")
            return {"valid": False, "errors": errors}
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if len(password) > 128:
            errors.append("Password must be less than 128 characters")
        
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one number")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        return {"valid": len(errors) == 0, "errors": errors}
    
    @staticmethod
    def validate_text_input(text: str, max_length: int = 1000, min_length: int = 1) -> Dict[str, Any]:
        """Validate text input with length constraints"""
        if not text:
            return {"valid": False, "error": "Text input is required"}
        
        if len(text) < min_length:
            return {"valid": False, "error": f"Text must be at least {min_length} characters"}
        
        if len(text) > max_length:
            return {"valid": False, "error": f"Text must be less than {max_length} characters"}
        
        # Remove potentially dangerous content
        sanitized_text = text.strip()
        
        return {"valid": True, "sanitized_text": sanitized_text}
    
    @staticmethod
    def validate_assessment_type(assessment_type: str) -> bool:
        """Validate assessment type"""
        valid_types = [
            'academic_writing', 'general_writing', 
            'academic_speaking', 'general_speaking'
        ]
        return assessment_type in valid_types
    
    @staticmethod
    def validate_json_data(data: Any, required_fields: List[str]) -> Dict[str, Any]:
        """Validate JSON data structure"""
        if not isinstance(data, dict):
            return {"valid": False, "error": "Invalid JSON format"}
        
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return {
                "valid": False, 
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }
        
        return {"valid": True}
    
    @staticmethod
    def sanitize_html_input(text: str) -> str:
        """Remove potentially dangerous HTML/script content"""
        if not text:
            return ""
        
        # Remove script tags and their content
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove potentially dangerous HTML tags
        dangerous_tags = ['script', 'iframe', 'object', 'embed', 'form']
        for tag in dangerous_tags:
            text = re.sub(f'<{tag}[^>]*>.*?</{tag}>', '', text, flags=re.IGNORECASE | re.DOTALL)
            text = re.sub(f'<{tag}[^>]*/?>', '', text, flags=re.IGNORECASE)
        
        return text.strip()

def validate_registration_data(func):
    """Decorator for validating registration data"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if request.method == 'POST':
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            age_verified = request.form.get('age_verified') == 'on'
            
            # Validate email
            if not InputValidator.validate_email(email):
                return jsonify({
                    'success': False,
                    'error': 'Invalid email format'
                }), 400
            
            # Validate age verification
            if not age_verified:
                return jsonify({
                    'success': False,
                    'error': 'Age verification is required (must be 16+)'
                }), 400
            
            # Validate password
            password_validation = InputValidator.validate_password(password)
            if not password_validation['valid']:
                return jsonify({
                    'success': False,
                    'error': 'Password validation failed',
                    'details': password_validation['errors']
                }), 400
            
            # Validate password confirmation
            if password != confirm_password:
                return jsonify({
                    'success': False,
                    'error': 'Passwords do not match'
                }), 400
        
        return func(*args, **kwargs)
    return wrapper

def validate_api_request(required_fields: List[str]):
    """Decorator for validating API request data"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if request.method == 'POST':
                try:
                    data = request.get_json()
                    if not data:
                        return jsonify({
                            'success': False,
                            'error': 'No JSON data provided'
                        }), 400
                    
                    validation_result = InputValidator.validate_json_data(data, required_fields)
                    if not validation_result['valid']:
                        return jsonify({
                            'success': False,
                            'error': validation_result['error']
                        }), 400
                    
                except Exception as e:
                    return jsonify({
                        'success': False,
                        'error': 'Invalid JSON format'
                    }), 400
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def validate_assessment_input(func):
    """Decorator for validating assessment input data"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if request.method == 'POST':
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No assessment data provided'
                }), 400
            
            # Validate assessment type
            assessment_type = data.get('assessment_type')
            if not InputValidator.validate_assessment_type(assessment_type):
                return jsonify({
                    'success': False,
                    'error': 'Invalid assessment type'
                }), 400
            
            # Validate text content if present
            if 'text' in data:
                text_validation = InputValidator.validate_text_input(
                    data['text'], 
                    max_length=5000,  # Reasonable limit for essays
                    min_length=10
                )
                if not text_validation['valid']:
                    return jsonify({
                        'success': False,
                        'error': text_validation['error']
                    }), 400
                
                # Sanitize the text
                data['text'] = InputValidator.sanitize_html_input(data['text'])
        
        return func(*args, **kwargs)
    return wrapper