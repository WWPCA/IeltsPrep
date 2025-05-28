"""
Terms and Support Routes Module
This module provides routes for terms of service, assessment day guide, and user profile.
"""

from main import app
from flask import render_template, redirect, url_for
from flask_login import login_required, current_user


@app.route('/terms-and-payment')
def terms_and_payment():
    """Display the terms of service and payment information."""
    return render_template('gdpr/terms_of_service.html', 
                          title='Terms of Service and Payment Information')


@app.route('/assessment-day-guide')
@login_required
def test_day():
    """Display the guide for the IELTS assessment day."""
    return render_template('test_day.html', 
                          title='IELTS Assessment Day Guide')


@app.route('/profile')
@login_required
def profile():
    """Display the user's profile."""
    return render_template('profile.html', 
                          title='My Profile')


# Note: Login and logout routes are defined in routes.py


@app.route('/device-specs')
def device_specs():
    """Display the device requirements for the platform."""
    return render_template('device_specs.html', 
                          title='Device Requirements')


@app.route('/privacy-policy')
def privacy_policy():
    """Display the privacy policy."""
    return render_template('gdpr/privacy_policy.html', 
                          title='Privacy Policy')


@app.route('/address-usage-policy')
def address_usage_policy():
    """Display the address usage policy."""
    return render_template('gdpr/address_usage_policy.html', 
                          title='Address Usage Policy')


# Add these routes to main.py
print("Terms and support routes added successfully.")