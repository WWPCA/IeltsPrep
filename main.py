import os
from app import app  # noqa: F401

# Core application routes
import routes  # noqa: F401
from flask_talisman import Talisman
from enhanced_error_handling import setup_global_error_handlers

# Import terms and support routes
import terms_and_support_routes  # noqa: F401

# Import password reset routes
import password_reset_routes  # noqa: F401

# Import GDPR routes
from gdpr_routes import gdpr_bp
app.register_blueprint(gdpr_bp)

# Import admin routes
from admin_routes import admin_bp
from cookie_consent_routes import cookie_consent_bp
app.register_blueprint(admin_bp)
app.register_blueprint(cookie_consent_bp)

# Cookie policy route
@app.route('/cookie-policy')
def cookie_policy():
    """Cookie policy page"""
    return render_template('cookie_policy.html')

# Configure Talisman with tightened Content Security Policy
Talisman(app, 
         force_https=False,  # Let Replit handle HTTPS
         content_security_policy={
             'default-src': ['\'self\''],
             'script-src': ['\'self\'', '\'unsafe-inline\'', 'cdn.jsdelivr.net', 'www.google.com', 'www.gstatic.com'],
             'style-src': ['\'self\'', '\'unsafe-inline\'', 'cdn.jsdelivr.net', 'fonts.googleapis.com'],
             'img-src': ['\'self\'', 'data:', 'https:'],
             'connect-src': ['\'self\'', 'wss://*.replit.dev', 'wss://*.replit.com'],
             'frame-src': ['\'self\'', 'www.google.com'],
             'font-src': ['\'self\'', 'fonts.gstatic.com', 'cdn.jsdelivr.net'],
             'media-src': ['\'self\'', 'blob:'],
         },
         frame_options='SAMEORIGIN')

# Set up global error handlers
setup_global_error_handlers()

if __name__ == "__main__":
    # Use environment variable to control debug mode - never debug=True in production
    debug_mode = os.environ.get("FLASK_ENV") == "development"
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=debug_mode)