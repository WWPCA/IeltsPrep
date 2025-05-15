#!/usr/bin/env python3
"""
Test Main Application

This is a simplified version of the main application for debugging purposes.
"""

import os
import sys
from flask import Flask, render_template, redirect, url_for, jsonify

# Create a simple test app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "debug-secret-key")

# Basic routes for testing
@app.route('/')
def index():
    """Basic home page."""
    return render_template('index.html', title='IELTS GenAI Prep Test')

@app.route('/debug')
def debug():
    """Debug information route."""
    return jsonify({
        'status': 'ok',
        'message': 'Debug route is working',
        'routes': [str(rule) for rule in app.url_map.iter_rules()],
        'environment': {
            'FLASK_ENV': os.environ.get('FLASK_ENV'),
            'FLASK_DEBUG': os.environ.get('FLASK_DEBUG'),
        }
    })

# Simplified error handlers
@app.errorhandler(404)
def page_not_found(e):
    return jsonify(error="Page not found", status=404), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify(error="Internal server error", status=500), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)