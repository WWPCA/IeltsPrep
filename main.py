from app import app  # noqa: F401
import routes  # noqa: F401

# Import and register writing assessment blueprint
from writing_assessment_routes import writing_assessment_bp
app.register_blueprint(writing_assessment_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
