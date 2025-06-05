"""
Response Helpers
Standardized response functions to reduce code duplication
"""

from flask import jsonify

def success_response(data=None, message="Success"):
    """Standardized success response"""
    response = {"success": True, "message": message}
    if data:
        response.update(data)
    return jsonify(response)

def error_response(message="An error occurred", error_code=None, status_code=400):
    """Standardized error response"""
    response = {"success": False, "error": message}
    if error_code:
        response["error_code"] = error_code
    return jsonify(response), status_code

def validation_error(field, message):
    """Standardized validation error response"""
    return error_response(f"{field}: {message}", "validation_error", 422)
