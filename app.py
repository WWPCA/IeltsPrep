import os
import logging

from flask import Flask, Response, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix
from recaptcha_helper import ReCaptchaV3

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

# Initialize Flask extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
csrf = CSRFProtect()
recaptcha_v3 = ReCaptchaV3()

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET") or os.environ.get("FLASK_SECRET_KEY")
if not app.secret_key:
    raise ValueError("SESSION_SECRET or FLASK_SECRET_KEY environment variable must be set")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database - require PostgreSQL in production
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
if not app.config["SQLALCHEMY_DATABASE_URI"]:
    if os.environ.get("FLASK_ENV") == "development":
        logging.warning("DATABASE_URL not set, falling back to SQLite for development")
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ielts_prep.db"
    else:
        raise ValueError("DATABASE_URL must be set in production")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Configure reCAPTCHA with validation - use dev keys for development domains
def get_recaptcha_keys():
    """Get appropriate reCAPTCHA keys based on current domain"""
    # Check if we're on a development domain (Replit)
    current_domain = os.environ.get('REPLIT_DOMAINS', '')
    is_dev_domain = 'replit.dev' in current_domain
    is_production_domain = 'ieltsaiprep.com' in current_domain
    
    if is_production_domain:
        # Use production keys for ieltsaiprep.com
        return (
            os.environ.get("RECAPTCHA_PUBLIC_KEY"),
            os.environ.get("RECAPTCHA_PRIVATE_KEY")
        )
    elif is_dev_domain:
        # Use development keys for Replit domains
        return (
            os.environ.get("RECAPTCHA_DEV_PUBLIC_KEY"),
            os.environ.get("RECAPTCHA_DEV_PRIVATE_KEY")
        )
    else:
        # Default to production keys for custom domains
        return (
            os.environ.get("RECAPTCHA_PUBLIC_KEY"),
            os.environ.get("RECAPTCHA_PRIVATE_KEY")
        )

site_key, secret_key = get_recaptcha_keys()
app.config["RECAPTCHA_SITE_KEY"] = site_key
app.config["RECAPTCHA_SECRET_KEY"] = secret_key
if not (app.config["RECAPTCHA_SITE_KEY"] and app.config["RECAPTCHA_SECRET_KEY"]):
    logging.warning("reCAPTCHA keys missing; CAPTCHA functionality will be disabled")
app.config["RECAPTCHA_THEME"] = "light"
app.config["RECAPTCHA_TYPE"] = "image"
app.config["RECAPTCHA_SIZE"] = "invisible"
app.config["RECAPTCHA_RTABINDEX"] = 10

# Configure URL scheme - use HTTPS for URL generation
app.config["PREFERRED_URL_SCHEME"] = "https"  # Generate HTTPS URLs for all links

# Configure session security
app.config["PERMANENT_SESSION_LIFETIME"] = 3600  # 1 hour session timeout
app.config["SESSION_COOKIE_SECURE"] = True  # HTTPS only cookies
app.config["SESSION_COOKIE_HTTPONLY"] = True  # Prevent XSS
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"  # CSRF protection

# Initialize extensions with the app
db.init_app(app)
login_manager.init_app(app)
csrf.init_app(app)
recaptcha_v3.init_app(app)
setattr(login_manager, 'login_view', 'login')
login_manager.login_message_category = "info"

# Re-enable CSRF protection for security
app.config['WTF_CSRF_TIME_LIMIT'] = None

# Let Replit handle HTTPS - this is for when the app runs outside of Replit
@app.before_request
def check_proxy_headers():
    """Ensure proper security headers are set with Replit's proxy."""
    # Check if running behind Replit proxy
    is_replit = 'REPLIT_DOMAINS' in os.environ
    
    # If not running behind a proxy, and not debug/testing, enforce HTTPS
    if not is_replit and not request.is_secure and not app.debug and not app.testing:
        url = request.url.replace('http://', 'https://', 1)
        return Response('', 301, {'Location': url})

# Add non-redundant security headers and CORS protection
@app.after_request
def add_security_headers(response):
    """Add security headers and CORS protection."""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # CORS protection - only allow requests from our own domain
    origin = request.headers.get('Origin')
    if origin:
        # Get allowed domains
        allowed_domains = []
        
        # Add Replit domains
        replit_domains = os.environ.get('REPLIT_DOMAINS', '')
        if replit_domains:
            for domain in replit_domains.split(','):
                domain = domain.strip()
                if domain:
                    allowed_domains.extend([f'https://{domain}', f'http://{domain}'])
        
        # Add custom domain
        custom_domain = os.environ.get('CUSTOM_DOMAIN', '')
        if custom_domain:
            allowed_domains.append(f'https://{custom_domain}')
        
        # Check if origin is allowed
        if origin in allowed_domains:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
        else:
            # Block unauthorized origins - no CORS headers
            logging.warning(f"Blocked cross-origin request from unauthorized domain: {origin}")
    
    return response

with app.app_context():
    # Import models to create tables
    import models
    db.create_all()
