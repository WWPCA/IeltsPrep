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

# Configure Talisman but allow iframe embedding from same origin and disable HTTPS forcing
Talisman(app, 
         force_https=False,
         frame_options='SAMEORIGIN', 
         frame_options_allow_from='*')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)