#!/usr/bin/env python3
"""
IELTS GenAI Prep - Clean Flask Application for UI Replication
This is a simplified version focused on demonstrating the UI components
"""

import os
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

# Add cache buster for development
@app.context_processor
def inject_cache_buster():
    return {'cache_buster': str(int(datetime.now().timestamp()))}

# Mock user class for template compatibility
class MockUser:
    def __init__(self):
        self.is_authenticated = False
        self.admin_role = False
    
    def has_active_assessment_package(self):
        return False

# Add mock current_user to template context
@app.context_processor
def inject_user():
    return {'current_user': MockUser()}

# Routes for UI demonstration
@app.route('/')
def index():
    return render_template('index.html', title='Home')

@app.route('/login')
def login():
    return render_template('login.html', title='Login')

@app.route('/register')
def register():
    # Return a simple form if register.html doesn't exist
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Register - IELTS GenAI Prep</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h3>Register for IELTS GenAI Prep</h3>
                        </div>
                        <div class="card-body">
                            <p>Registration form would go here.</p>
                            <a href="/" class="btn btn-primary">Back to Home</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/profile')
def profile():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Profile - IELTS GenAI Prep</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-header">
                            <h3>My Profile</h3>
                        </div>
                        <div class="card-body">
                            <p>User profile and assessments would go here.</p>
                            <a href="/" class="btn btn-primary">Back to Home</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/assessment-products')
def assessment_products_page():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Assessment Products - IELTS GenAI Prep</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <h2>Assessment Products</h2>
            <p>Assessment packages would be displayed here.</p>
            <a href="/" class="btn btn-primary">Back to Home</a>
        </div>
    </body>
    </html>
    '''

# Assessment selection routes (mock)
@app.route('/academic-speaking-selection')
def academic_speaking_selection():
    return redirect(url_for('index'))

@app.route('/general-speaking-selection') 
def general_speaking_selection():
    return redirect(url_for('index'))

@app.route('/academic-writing-selection')
def academic_writing_selection():
    return redirect(url_for('index'))

@app.route('/general-writing-selection')
def general_writing_selection():
    return redirect(url_for('index'))

@app.route('/privacy-policy')
def privacy_policy():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Privacy Policy - IELTS GenAI Prep</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <h2>Privacy Policy</h2>
            <p>Privacy policy content would go here.</p>
            <a href="/" class="btn btn-primary">Back to Home</a>
        </div>
    </body>
    </html>
    '''

@app.route('/terms-and-payment')
def terms_and_payment():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Terms of Service - IELTS GenAI Prep</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <h2>Terms of Service</h2>
            <p>Terms of service content would go here.</p>
            <a href="/" class="btn btn-primary">Back to Home</a>
        </div>
    </body>
    </html>
    '''

@app.route('/logout')
def logout():
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)