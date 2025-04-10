"""
Utility functions for the AI Learning Hub mobile API
"""
from flask import jsonify
import json
import time
from datetime import datetime
import traceback

def api_response(data=None, message=None, success=True, status_code=200):
    """
    Standard API response format for mobile clients
    
    Args:
        data (dict, optional): Data to return to the client
        message (str, optional): Message to return to the client
        success (bool): Whether the request was successful
        status_code (int): HTTP status code
        
    Returns:
        tuple: (response_dict, status_code)
    """
    response = {
        'success': success,
        'timestamp': int(time.time()),
        'api_version': '1.0'
    }
    
    if message:
        response['message'] = message
        
    if data is not None:
        response['data'] = data
        
    return jsonify(response), status_code

def error_response(message, status_code=400, error_code=None, error_details=None):
    """
    Error response format for mobile clients
    
    Args:
        message (str): Error message
        status_code (int): HTTP status code
        error_code (str, optional): Application-specific error code
        error_details (dict, optional): Additional error details
        
    Returns:
        tuple: (response_dict, status_code)
    """
    response = {
        'success': False,
        'message': message,
        'timestamp': int(time.time()),
        'api_version': '1.0'
    }
    
    if error_code:
        response['error_code'] = error_code
        
    if error_details:
        response['error_details'] = error_details
        
    return jsonify(response), status_code

def handle_api_exception(e):
    """
    Handle exceptions in API routes
    
    Args:
        e (Exception): The exception to handle
        
    Returns:
        tuple: (response_dict, status_code)
    """
    # Log the exception
    print(f"API Error: {str(e)}")
    print(traceback.format_exc())
    
    # Return an error response
    return error_response(
        message="An internal server error occurred",
        status_code=500,
        error_code="internal_error",
        error_details={"error_type": type(e).__name__}
    )

# Mobile-specific utility functions
def get_device_info(request):
    """
    Extract device information from the request headers
    
    Args:
        request: Flask request object
        
    Returns:
        dict: Device information
    """
    headers = request.headers
    
    return {
        'platform': headers.get('X-Platform', 'unknown'),
        'app_version': headers.get('X-App-Version', 'unknown'),
        'device_model': headers.get('X-Device-Model', 'unknown'),
        'os_version': headers.get('X-OS-Version', 'unknown')
    }

def is_mobile_client(request):
    """
    Check if the request is from a mobile client
    
    Args:
        request: Flask request object
        
    Returns:
        bool: True if the request is from a mobile client
    """
    return request.headers.get('X-Platform') in ['ios', 'android']