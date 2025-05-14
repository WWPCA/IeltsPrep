"""
Terms and Support Routes Module
This module provides routes for terms of service and assessment day guide.
"""

from main import app
from flask import render_template, redirect, url_for
from flask_login import login_required


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


# Add these routes to main.py
print("Terms and support routes added successfully.")