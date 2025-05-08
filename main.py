from app import app  # noqa: F401
import routes  # noqa: F401
import routes_general_reading  # noqa: F401

# Import and register assessment blueprints
from writing_assessment_routes import writing_assessment
from speaking_assessment_routes import speaking_assessment
from cart_routes import cart_bp

# Register blueprints
app.register_blueprint(writing_assessment)
app.register_blueprint(speaking_assessment)
app.register_blueprint(cart_bp, url_prefix='/cart')

# Import assessment products routes
import integrate_assessment_routes  # noqa: F401

# Import and add contact routes
from contact_routes import add_contact_routes
add_contact_routes(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
