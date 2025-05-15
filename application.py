#!/usr/bin/env python3
"""
Main Application Entry Point with Enhanced Debugging

This is the main entry point for the application with additional debugging.
"""

import os
import sys
import logging
from flask import Flask, jsonify, render_template

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("application")

# Import the app from app.py
try:
    from app import app
    logger.info("Successfully imported app from app.py")
except Exception as e:
    logger.error(f"Failed to import app from app.py: {str(e)}")
    sys.exit(1)

# Add a debug route for testing
@app.route('/debug')
def debug_route():
    """Debug route to test if the app is working."""
    logger.info("Debug route accessed")
    
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': ', '.join(rule.methods),
            'rule': str(rule)
        })
    
    return jsonify({
        'status': 'ok',
        'time': 'now',
        'routes': routes,
        'config': {
            key: str(value) for key, value in app.config.items() 
            if key not in ['SECRET_KEY', 'SECURITY_PASSWORD_SALT']
        }
    })

# Check if the index route exists
if app.view_functions.get('index') is None:
    logger.warning("No index route found, adding a fallback")
    
    @app.route('/')
    def index():
        """Fallback home page if not already defined."""
        logger.info("Fallback index route accessed")
        return render_template('index.html', title='IELTS GenAI Prep')

if __name__ == "__main__":
    # Run the app in debug mode
    app.run(host="0.0.0.0", port=5000, debug=True)