from app import app  # noqa: F401
import routes  # noqa: F401

# Register the pronunciation coach blueprint
from pronunciation_routes import pronunciation_bp
app.register_blueprint(pronunciation_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
