#!/usr/bin/env python3
"""
Development script for AI Learning Hub with debug mode enabled.
This script is for local development and testing, separate from the IELTS app.
"""
import os
import sys
from ai_learning_hub.app import app

# Configure development settings
DEBUG_PORT = 5051  # Use a different port for development

if __name__ == "__main__":
    print(f"Starting AI Learning Hub in DEVELOPMENT mode on port {DEBUG_PORT}...")
    print("Debug mode: ENABLED")
    print(f"Access the application at: http://localhost:{DEBUG_PORT}")
    print("Press CTRL+C to stop the server")
    app.config['DEBUG'] = True
    app.config['TESTING'] = True
    app.config['ENV'] = 'development'
    app.run(host="0.0.0.0", port=DEBUG_PORT, debug=True)