"""
Cloud SQL Configuration for IELTS AI Prep
This module provides database connectivity for GCP Cloud SQL deployment.
"""

import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models"""
    pass


db = SQLAlchemy(model_class=Base)


def configure_cloud_sql(app: Flask) -> None:
    """
    Configure the Flask application to connect to Cloud SQL.
    Supports both local development and Cloud Run deployment.
    
    Args:
        app: Flask application instance
    """
    # Get database configuration from environment variables
    db_user = os.environ.get("DB_USER")
    db_pass = os.environ.get("DB_PASS")
    db_name = os.environ.get("DB_NAME")
    db_host = os.environ.get("DB_HOST", "localhost")
    
    # Check if running on Cloud Run
    if os.environ.get("CLOUD_RUN"):
        # Cloud SQL connection via unix socket
        db_socket_dir = os.environ.get("DB_SOCKET_DIR", "/cloudsql")
        instance_connection_name = os.environ.get("INSTANCE_CONNECTION_NAME")
        
        if not instance_connection_name:
            logging.error("No INSTANCE_CONNECTION_NAME provided for Cloud Run")
            raise ValueError("Missing INSTANCE_CONNECTION_NAME environment variable")
        
        db_uri = f"postgresql://{db_user}:{db_pass}@/{db_name}?host={db_socket_dir}/{instance_connection_name}"
        logging.info(f"Connecting to Cloud SQL via socket: {db_socket_dir}/{instance_connection_name}")
    else:
        # Local development - connect via TCP
        db_uri = f"postgresql://{db_user}:{db_pass}@{db_host}:5432/{db_name}"
        logging.info(f"Connecting to database at: {db_host}")
    
    # Configure database connection
    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,  # Recycle connections after 5 minutes
        "pool_pre_ping": True,  # Check connection liveness
        "pool_size": 10,  # Default pool size
        "max_overflow": 20,  # Allow up to 20 additional connections
    }
    
    # Initialize SQLAlchemy with the app
    db.init_app(app)