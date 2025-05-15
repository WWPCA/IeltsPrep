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
app.secret_key = os.environ.get("SESSION_SECRET", "ielts-ai-prep-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///ielts_prep.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Configure reCAPTCHA
app.config["RECAPTCHA_SITE_KEY"] = os.environ.get("RECAPTCHA_PUBLIC_KEY", "")
app.config["RECAPTCHA_SECRET_KEY"] = os.environ.get("RECAPTCHA_PRIVATE_KEY", "")
app.config["RECAPTCHA_THEME"] = "light"
app.config["RECAPTCHA_TYPE"] = "image"
app.config["RECAPTCHA_SIZE"] = "invisible"
app.config["RECAPTCHA_RTABINDEX"] = 10

# Configure URL scheme - use HTTP for Replit environment
app.config["PREFERRED_URL_SCHEME"] = "http"

# Initialize extensions with the app
db.init_app(app)
login_manager.init_app(app)
csrf.init_app(app)
recaptcha_v3.init_app(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"

# Force HTTPS redirect
# Completely disable HTTPS redirection in Replit environment
# @app.before_request
# def force_https():
#     """Redirect all HTTP requests to HTTPS."""
#     if not request.is_secure and not app.debug and not app.testing:
#         url = request.url.replace('http://', 'https://', 1)
#         return Response('', 301, {'Location': url})

# Add Content Security Policy and HTTPS-related headers
@app.after_request
def add_security_headers(response):
    """Add security headers to enhance HTTPS protection."""
    # Content Security Policy
    csp = (
        "default-src 'self'; "
        "script-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://www.google.com https://www.gstatic.com 'unsafe-inline'; "
        "style-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
        "connect-src 'self'; "
        "media-src 'self'; "
        "object-src 'none'; "
        "frame-src https://www.google.com;"
    )
    
    # Set security headers
    response.headers["Content-Security-Policy"] = csp
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    return response

with app.app_context():
    # Import models to create tables
    import models
    db.create_all()
