from app import app  # noqa: F401
import routes  # noqa: F401
import routes_general_reading  # noqa: F401

# Import and register assessment blueprints
from writing_assessment_routes import writing_assessment
from speaking_assessment_routes import speaking_assessment

# Register blueprints
app.register_blueprint(writing_assessment)
app.register_blueprint(speaking_assessment)

# Import assessment products routes
import integrate_assessment_routes  # noqa: F401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
