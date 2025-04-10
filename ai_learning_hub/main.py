from ai_learning_hub.app import app
from ai_learning_hub.routes import *

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)