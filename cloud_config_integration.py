"""
Cloud Configuration Integration for IELTS AI Prep
This script integrates cloud-specific configurations for GCP deployment.
"""

import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def integrate_cloud_configurations(app):
    """
    Integrate all cloud-specific configurations into the Flask application.
    
    Args:
        app: Flask application instance
    """
    # Import configuration modules
    try:
        from db_config import configure_cloud_sql
        from session_config import configure_redis_session
        
        # Apply database configuration
        logger.info("Configuring Cloud SQL connection...")
        configure_cloud_sql(app)
        
        # Apply Redis session configuration if running in cloud
        if os.environ.get("CLOUD_RUN") or os.environ.get("REDIS_URL"):
            logger.info("Configuring Redis session storage...")
            configure_redis_session(app)
        else:
            logger.info("Skipping Redis configuration - not running in cloud environment")
        
        # Set additional cloud-specific configuration
        if os.environ.get("CLOUD_RUN"):
            # Ensure proper proxy handling for Cloud Run
            app.config['PREFERRED_URL_SCHEME'] = 'https'
            logger.info("Set preferred URL scheme to HTTPS for Cloud Run")
        
        # Additional security headers for cloud deployment
        @app.after_request
        def add_cloud_security_headers(response):
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'SAMEORIGIN'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            return response
        
        logger.info("Cloud configurations integrated successfully")
        return True
    
    except ImportError as e:
        logger.error(f"Failed to import cloud configuration modules: {e}")
        return False
    except Exception as e:
        logger.error(f"Error integrating cloud configurations: {e}")
        return False


if __name__ == "__main__":
    # This can be used to test configuration integration
    from flask import Flask
    test_app = Flask(__name__)
    integrate_cloud_configurations(test_app)