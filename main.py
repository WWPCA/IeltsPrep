import os
from app import app  # noqa: F401
import routes  # noqa: F401
from flask_talisman import Talisman

# Import and register assessment routes
from add_assessment_routes import add_assessment_routes
add_assessment_routes(app)

# Import assessment structure routes
import assessment_structure_routes  # noqa: F401

# Import terms and support routes
import terms_and_support_routes  # noqa: F401

# Import and register contact routes
from contact_routes import add_contact_routes
add_contact_routes(app)

# Import and register cart blueprint
from cart_routes import cart_bp
app.register_blueprint(cart_bp, url_prefix='/cart')

# Configure Talisman with security headers but let Replit handle HTTPS
Talisman(app, 
         force_https=False,  # Let Replit handle HTTPS
         content_security_policy={
             'default-src': ['\'self\'', '*.stripe.com', 'https://cdn.jsdelivr.net'],
             'script-src': ['\'self\'', '\'unsafe-inline\'', '*.stripe.com', 'https://cdn.jsdelivr.net'],
             'style-src': ['\'self\'', '\'unsafe-inline\'', 'https://cdn.jsdelivr.net'],
             'img-src': ['\'self\'', 'data:', 'https:'],
             'connect-src': ['\'self\'', 'https:'],
             'frame-src': ['\'self\'', '*.stripe.com'],
             'font-src': ['\'self\'', 'https://cdn.jsdelivr.net'],
         },
         frame_options='SAMEORIGIN', 
         frame_options_allow_from='*')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)