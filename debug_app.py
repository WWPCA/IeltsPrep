#!/usr/bin/env python3
"""
Debug Application

This script adds enhanced debugging to the app to identify any issues.
It adds better error handling and logging.
"""

import logging
import os
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("debug_app")

def add_debug_route(app):
    """Add a debug route to test if the application is running."""
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
        
        return {
            'status': 'ok',
            'time': datetime.utcnow().isoformat(),
            'routes': routes,
            'config': {
                key: str(value) for key, value in app.config.items() 
                if key not in ['SECRET_KEY', 'SECURITY_PASSWORD_SALT']
            }
        }

def install_error_handlers(app):
    """Install custom error handlers with improved logging."""
    @app.errorhandler(404)
    def page_not_found(e):
        logger.warning(f"404 error: {request.path}")
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        logger.error(f"500 error: {str(e)}")
        return render_template('errors/500.html'), 500

def main():
    """Main debug function."""
    try:
        from app import app
        logger.info("Imported app successfully")
        
        # Add debug route
        add_debug_route(app)
        logger.info("Added debug route")
        
        # Install error handlers
        from flask import request, render_template
        install_error_handlers(app)
        logger.info("Installed error handlers")
        
        # Run app in debug mode
        app.run(host="0.0.0.0", port=5000, debug=True)
    except Exception as e:
        logger.error(f"Error starting app: {str(e)}")
        raise

if __name__ == "__main__":
    main()