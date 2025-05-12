"""
Redis Session Configuration for IELTS AI Prep
This module provides session handling with Redis for scalable deployment.
"""

import os
import redis
from datetime import timedelta
from flask import Flask
from flask_session import Session


def configure_redis_session(app: Flask) -> None:
    """
    Configure Redis-based session handling for the Flask application.
    This allows session data to be shared across multiple instances.
    
    Args:
        app: Flask application instance
    """
    # Get Redis connection URL from environment variables
    redis_url = os.environ.get("REDIS_URL")
    
    if not redis_url:
        # Fall back to local Redis for development if no URL is specified
        app.config["SESSION_TYPE"] = "filesystem"
        app.logger.warning("No REDIS_URL found, using filesystem sessions (not recommended for production)")
    else:
        # Configure Redis session
        app.config["SESSION_TYPE"] = "redis"
        app.config["SESSION_REDIS"] = redis.from_url(redis_url)
        app.config["SESSION_USE_SIGNER"] = True
        app.config["SESSION_PERMANENT"] = False
        app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=1)
        app.logger.info("Redis session configured with URL: %s", redis_url.split("@")[-1])
    
    # Initialize Flask-Session
    Session(app)