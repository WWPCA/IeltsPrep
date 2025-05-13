"""
Routes for General Training Reading tests.

NOTICE: This entire file has been disabled as part of the 
refactoring to focus on assessments only, not practice tests.
All general reading functionality will be reimplemented using the Assessment model.
"""
from flask import redirect, url_for, flash
from app import app

# Create a placeholder route to avoid errors when importing this file
@app.route('/practice/general-reading/disabled')
def general_reading_disabled():
    """Placeholder route that redirects to home."""
    flash('General reading tests have been replaced with assessments', 'info')
    return redirect(url_for('index'))