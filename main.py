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

# Import account deletion routes
import account_deletion_routes  # noqa: F401

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

# Old conversational routes removed - using new ClearScore conversational assessment structure

# Configure Talisman with security headers but let Replit handle HTTPS
Talisman(app, 
         force_https=False,  # Let Replit handle HTTPS
         content_security_policy={
             'default-src': ['\'self\'', '*.replit.dev', '*.replit.com', '*.stripe.com', 'https://cdn.jsdelivr.net'],
             'script-src': ['\'self\'', '\'unsafe-inline\'', '*.replit.dev', '*.replit.com', '*.stripe.com', 'https://cdn.jsdelivr.net', 'https://cdnjs.cloudflare.com', 'https://www.google.com', 'https://www.gstatic.com'],
             'style-src': ['\'self\'', '\'unsafe-inline\'', 'https://cdn.jsdelivr.net', 'https://cdnjs.cloudflare.com', 'https://fonts.googleapis.com'],
             'img-src': ['\'self\'', 'data:', 'https:', 'blob:'],
             'connect-src': ['\'self\'', 'https:', 'wss:', 'ws:'],  # Allow WebSocket connections
             'frame-src': ['\'self\'', '*.stripe.com', '*.replit.dev', '*.replit.com', 'https://www.google.com'],
             'font-src': ['\'self\'', 'https://fonts.gstatic.com', 'https://cdn.jsdelivr.net', 'https://cdnjs.cloudflare.com'],
             'media-src': ['\'self\'', 'https:', 'blob:'],
         },
         frame_options='SAMEORIGIN', 
         frame_options_allow_from='*')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)