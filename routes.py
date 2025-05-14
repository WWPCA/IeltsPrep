import os
import json
import time
import uuid
import base64
import urllib
import logging
import random
import requests
from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, session, abort, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_parse
from functools import wraps
from app import app, db, recaptcha_v3
from models import User, AssessmentStructure, SpeakingPrompt, Assessment, UserAssessmentAssignment, PaymentRecord
from utils import get_user_region, get_translation, compress_audio
from payment_services import create_stripe_checkout_session, create_payment_record, verify_stripe_payment, create_stripe_checkout_speaking
import assessment_assignment_service
from openai_writing_assessment import assess_writing_task1, assess_writing_task2, assess_complete_writing_test
from aws_services import analyze_speaking_response, analyze_pronunciation, transcribe_audio, generate_polly_speech
# Using only get_country_from_ip since we've moved to fixed pricing
from geoip_services import get_country_from_ip
from country_restrictions import country_access_required, is_country_restricted, RESTRICTION_MESSAGE

# Import the assessment details route
try:
    from add_assessment_details_route import assessment_details_route
except ImportError:
    # Define it directly if the import fails
    def assessment_details_route(assessment_type, assessment_id):
        """Show details about an assessment before starting it"""
        if assessment_type not in ['listening', 'reading', 'writing', 'speaking']:
            abort(404)
        
        assessment = Assessment.query.get_or_404(assessment_id)
        
        # All assessments require an assessment package
        if not current_user.has_active_assessment_package():
            flash('This assessment requires an assessment package. Please purchase an assessment package to access GenAI-powered skill evaluations.', 'warning')
            return redirect(url_for('assessment_products_page'))
        
        # Check if user has already used this assessment during current assessment package period
        if current_user.has_taken_assessment(assessment_id, assessment_type):
            flash('You have already used this assessment during your current assessment package period. Each assessment can only be used once per assessment package.', 'warning')
            return redirect(url_for('assessment_products_page'))
        
        return render_template('assessment_details.html', 
                              title=f'IELTS {assessment_type.capitalize()} Assessment',
                              assessment=assessment,
                              assessment_type=assessment_type)

# Add the assessment details route
app.add_url_rule('/assessment/<assessment_type>/<int:assessment_id>/details', 
                 'assessment_details', 
                 assessment_details_route, 
                 methods=['GET'])

# Main index route
@app.route('/')
def index():
    """Home page with information about the platform"""
    return render_template('index.html', title='IELTS GenAI Prep - Home')

# User authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page with form validation"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember_me = 'remember_me' in request.form
        
        user = User.query.filter((User.username == username) | (User.email == username)).first()
        
        if user and user.check_password(password):
            if not user.account_activated:
                flash('Your account has not been activated yet. Please check your email for the activation link.', 'warning')
                return redirect(url_for('login'))
            
            login_user(user, remember=remember_me)
            user.update_streak()  # Update streak on login
            db.session.commit()
            
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            
            return redirect(next_page)
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html', title='Login')

@app.route('/logout')
def logout():
    """Log user out and redirect to home page"""
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page with form validation"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

# Custom cache buster to force browsers to reload CSS, JS on new deployments
@app.context_processor
def inject_cache_buster():
    """Add cache_buster variable to all templates to prevent browser caching"""
    cache_buster = int(time.time())
    return dict(cache_buster=cache_buster)

def assessment_package_required(f):
    """
    Decorator to check if user has active assessment packages
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this feature.', 'warning')
            return redirect(url_for('login'))
            
        if not current_user.has_active_assessment_package():
            flash('This feature requires an active assessment package. Please purchase a package to access this feature.', 'warning')
            return redirect(url_for('assessment_products_page'))
            
        return f(*args, **kwargs)
    return decorated_function

# Remove this after all routes are updated
# Legacy name mapping for backward compatibility with any old code
# Removed legacy backward compatibility line

# Streak tracking removed as requested

# Note: Restricted access page is now handled by country_access_control.py via the /access-restricted route

# Test route for country restrictions (admin only)
