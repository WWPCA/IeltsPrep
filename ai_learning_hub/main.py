from ai_learning_hub.app import app
from ai_learning_hub.routes import *  # noqa: F401, F403

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)