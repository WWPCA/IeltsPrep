"""
Static file server for QR authentication testing
Serves only HTML/CSS/JS files - all API calls go to Lambda backend
"""

from flask import Flask, send_from_directory, render_template
import os

app = Flask(__name__)

@app.route('/')
def home():
    """Serve QR login page"""
    return render_template('qr_login.html')

@app.route('/assessments')
def assessments():
    """Serve assessments page"""
    return render_template('assessments.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)