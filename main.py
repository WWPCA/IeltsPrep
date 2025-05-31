import os
from app import app  # noqa: F401

# Import and register recovery routes
try:
    from recovery_routes import register_recovery_routes
    register_recovery_routes(app)
    print("Assessment recovery system integrated successfully.")
except Exception as e:
    print(f"Failed to integrate recovery system: {e}")
import routes  # noqa: F401
from flask_talisman import Talisman
from enhanced_error_handling import setup_global_error_handlers

# Import and register assessment routes
from add_assessment_routes import add_assessment_routes
add_assessment_routes(app)

# Core assessment routes now integrated in routes.py
import writing_assessment_routes  # noqa: F401
# Removed old speaking assessment routes - using new conversational ClearScore assessment structure

# Import assessment structure routes
import assessment_structure_routes  # noqa: F401

# Import terms and support routes
import terms_and_support_routes  # noqa: F401

# Import assessment submission routes for TrueScore® and ClearScore®
import assessment_submission_routes  # noqa: F401

# Import account deletion routes
import account_deletion_routes  # noqa: F401
import account_deletion_routes_enhanced  # noqa: F401

# Import password reset routes
import password_reset_routes  # noqa: F401

# Import and register contact routes
from contact_routes import add_contact_routes
add_contact_routes(app)

# Import and register cart blueprint
from cart_routes import cart_bp
app.register_blueprint(cart_bp, url_prefix='/cart')

# Import and register GDPR blueprint
from gdpr_routes import gdpr_bp
app.register_blueprint(gdpr_bp)

# Browser-based speech recognition integrated into existing routes

# Configure Talisman with tightened Content Security Policy
Talisman(app, 
         force_https=False,  # Let Replit handle HTTPS
         content_security_policy={
             'default-src': ['\'self\''],
             'script-src': ['\'self\'', '\'unsafe-inline\'', 'js.stripe.com', 'cdn.jsdelivr.net', 'www.google.com', 'www.gstatic.com'],
             'style-src': ['\'self\'', '\'unsafe-inline\'', 'cdn.jsdelivr.net', 'fonts.googleapis.com'],
             'img-src': ['\'self\'', 'data:', 'https:'],
             'connect-src': ['\'self\'', 'api.stripe.com', 'wss://*.replit.dev', 'wss://*.replit.com'],
             'frame-src': ['\'self\'', 'js.stripe.com', 'www.google.com'],
             'font-src': ['\'self\'', 'fonts.gstatic.com', 'cdn.jsdelivr.net'],
             'media-src': ['\'self\'', 'blob:'],
         },
         frame_options='SAMEORIGIN')

# Set up global error handlers
setup_global_error_handlers(app)

if __name__ == "__main__":
    # Use environment variable to control debug mode - never debug=True in production
    debug_mode = os.environ.get("FLASK_ENV") == "development"
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=debug_mode)