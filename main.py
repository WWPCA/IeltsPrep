from app import app  # noqa: F401
import routes  # noqa: F401
from flask import Flask
from flask_talisman import Talisman

# Import and register writing assessment blueprint
from writing_assessment_routes import writing_assessment_bp
app.register_blueprint(writing_assessment_bp)

app = Flask(__name__)
# Configure Talisman but allow iframe embedding from same origin
Talisman(app, frame_options='SAMEORIGIN', frame_options_allow_from='*')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)