"""
Web views for the AI Learning Hub API
"""
from flask import Blueprint, render_template
from datetime import datetime

# Create a blueprint for the API web views
api_web_bp = Blueprint('api_web', __name__, url_prefix='/api')

@api_web_bp.route('/docs')
def api_docs():
    """API documentation for mobile developers"""
    return render_template('api_docs.html')

@api_web_bp.route('/status')
def api_status():
    """API status page"""
    # Pass the current datetime to the template
    return render_template('api_status.html', now=datetime.utcnow())