"""
Script to run the AI Learning Hub application separate from the IELTS application.
"""
import os
import sys
from ai_learning_hub.main import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)