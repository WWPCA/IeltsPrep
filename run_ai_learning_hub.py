#!/usr/bin/env python3
"""
Script to run the AI Learning Hub application separate from the IELTS application.
"""
import os
import sys
import subprocess

# Use port 5050 to avoid conflicts with the IELTS app on port 5000
PORT = 5050

# Launch the AI Learning Hub app using Gunicorn for production deployment
if __name__ == "__main__":
    cmd = f"gunicorn --bind 0.0.0.0:{PORT} --reuse-port --reload ai_learning_hub.main:app"
    print(f"Starting AI Learning Hub application on port {PORT}...")
    print(f"Command: {cmd}")
    subprocess.run(cmd, shell=True)