"""
GDPR Compliance Routes

This module provides Flask routes for GDPR compliance features:
- Privacy policy and terms display
- Consent management
- Data access requests
- Right to be forgotten (data deletion)
- Cookie preferences
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session, send_file
from flask_login import login_required, current_user
from models import db, User
import json
import os
import datetime
from io import BytesIO
import gdpr_framework as gdpr

# Initialize blueprint
gdpr_bp = Blueprint('gdpr', __name__)

# ==================================================
# Privacy Policy and Terms
# ==================================================

@gdpr_bp.route('/privacy-policy')
def privacy_policy():
    """Display the privacy policy"""
    return render_template('gdpr/privacy_policy.html')

@gdpr_bp.route('/terms-of-service')
def terms_of_service():
    """Display the terms of service"""
    return render_template('gdpr/terms_of_service.html')

@gdpr_bp.route('/cookie-policy')
def cookie_policy():
    """Display the cookie policy"""
    cookie_categories = gdpr.get_cookie_categories()
    return render_template('gdpr/cookie_policy.html', cookie_categories=cookie_categories)

@gdpr_bp.route('/address-usage-policy')
def address_usage_policy():
    """Display the customer address usage policy"""
    return render_template('gdpr/address_usage_policy.html')

# ==================================================
# Cookie Management
# ==================================================

@gdpr_bp.route('/cookie-preferences', methods=['GET', 'POST'])
def cookie_preferences():
    """Manage cookie preferences"""
    cookie_categories = gdpr.get_cookie_categories()
    
    if request.method == 'POST':
        preferences = {
            'essential': True,  # Always required
            'functional': 'functional' in request.form,
            'analytics': 'analytics' in request.form,
            'marketing': 'marketing' in request.form
        }
        
        # Save preferences
        user_id = current_user.id if current_user.is_authenticated else None
        gdpr.update_cookie_preferences(preferences, user_id)
        
        flash('Your cookie preferences have been updated.', 'success')
        
        # Redirect to referring page or dashboard
        next_page = request.args.get('next') or url_for('index')
        return redirect(next_page)
    
    # Get current preferences
    user_id = current_user.id if current_user.is_authenticated else None
    preferences = gdpr.get_user_cookie_preferences(user_id)
    
    return render_template(
        'gdpr/cookie_preferences.html',
        cookie_categories=cookie_categories,
        preferences=preferences
    )

@gdpr_bp.route('/api/cookie-preferences', methods=['POST'])
def api_cookie_preferences():
    """API endpoint for updating cookie preferences"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
    
    preferences = {
        'essential': True,  # Always required
        'functional': data.get('functional', False),
        'analytics': data.get('analytics', False),
        'marketing': data.get('marketing', False)
    }
    
    # Save preferences
    user_id = current_user.id if current_user.is_authenticated else None
    success = gdpr.update_cookie_preferences(preferences, user_id)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Failed to update preferences'}), 500

# ==================================================
# Consent Management
# ==================================================

@gdpr_bp.route('/consent-settings')
@login_required
def consent_settings():
    """Manage user consent settings"""
    consent = gdpr.get_user_consent_settings(current_user.id)
    
    # Record view of consent settings
    gdpr.log_consent_activity(current_user.id, 'view_consent_settings', {
        'timestamp': datetime.datetime.utcnow().isoformat()
    })
    
    return render_template('gdpr/consent_settings.html', consent=consent)

@gdpr_bp.route('/update-consent', methods=['POST'])
@login_required
def update_consent():
    """Update user consent settings"""
    consent_data = {
        'marketing_emails': 'marketing_emails' in request.form,
        'data_processing': True,  # Required
        'audio_processing': 'audio_processing' in request.form,
        'analytics': 'analytics' in request.form,
        'third_party_sharing': 'third_party_sharing' in request.form
    }
    
    success = gdpr.update_user_consent(current_user.id, consent_data)
    
    if success:
        # Record consent update
        gdpr.log_consent_activity(current_user.id, 'update_consent', {
            'timestamp': datetime.datetime.utcnow().isoformat(),
            'new_settings': consent_data
        })
        
        flash('Your consent settings have been updated.', 'success')
    else:
        flash('There was an error updating your consent settings.', 'danger')
    
    return redirect(url_for('gdpr.consent_settings'))

# ==================================================
# Data Access
# ==================================================

@gdpr_bp.route('/my-data')
@login_required
def my_data():
    """Data access dashboard"""
    return render_template('gdpr/my_data.html')

@gdpr_bp.route('/request-data-export', methods=['GET', 'POST'])
@login_required
def request_data_export():
    """Request data export"""
    if request.method == 'POST':
        export_format = request.form.get('format', 'json')
        include_assessments = 'include_assessments' in request.form
        
        # Generate verification code
        verification_code = gdpr.generate_verification_code(
            current_user.id, 
            'export', 
            expiry_minutes=30
        )
        
        # In a production system, this would send an email with the code
        # For development, we'll just show it
        
        flash(f'Your verification code is: {verification_code}', 'info')
        return redirect(url_for('gdpr.verify_data_export'))
    
    return render_template('gdpr/request_data_export.html')

@gdpr_bp.route('/verify-data-export', methods=['GET', 'POST'])
@login_required
def verify_data_export():
    """Verify data export request"""
    if request.method == 'POST':
        verification_code = request.form.get('verification_code')
        
        if gdpr.verify_code(current_user.id, 'export', verification_code):
            export_format = request.form.get('format', 'json')
            
            # Generate export
            success, export_data = gdpr.generate_user_data_report(current_user.id, export_format)
            
            if success:
                # Record successful export
                gdpr.log_consent_activity(current_user.id, 'data_export_completed', {
                    'timestamp': datetime.datetime.utcnow().isoformat(),
                    'format': export_format
                })
                
                # Serve file for download
                if export_format == 'json':
                    mimetype = 'application/json'
                    filename = f'user_data_{current_user.id}.json'
                else:  # CSV
                    mimetype = 'text/csv'
                    filename = f'user_data_{current_user.id}.csv'
                
                # Create in-memory file-like object
                data = BytesIO(export_data.encode('utf-8'))
                data.seek(0)
                
                return send_file(
                    data,
                    mimetype=mimetype,
                    as_attachment=True,
                    download_name=filename
                )
            else:
                flash('Error generating data export. Please try again.', 'danger')
        else:
            flash('Invalid verification code. Please try again.', 'danger')
    
    return render_template('gdpr/verify_data_export.html')

# ==================================================
# Data Deletion
# ==================================================

@gdpr_bp.route('/request-data-deletion', methods=['GET', 'POST'])
@login_required
def request_data_deletion():
    """Request data deletion"""
    if request.method == 'POST':
        deletion_type = request.form.get('deletion_type', 'partial')
        
        # Generate verification code
        verification_code = gdpr.generate_verification_code(
            current_user.id, 
            'deletion', 
            expiry_minutes=30
        )
        
        # Store deletion type in session
        session['deletion_type'] = deletion_type
        
        # In a production system, this would send an email with the code
        # For development, we'll just show it
        
        flash(f'Your verification code is: {verification_code}', 'info')
        return redirect(url_for('gdpr.verify_data_deletion'))
    
    return render_template('gdpr/request_data_deletion.html')

@gdpr_bp.route('/verify-data-deletion', methods=['GET', 'POST'])
@login_required
def verify_data_deletion():
    """Verify data deletion request"""
    if request.method == 'POST':
        verification_code = request.form.get('verification_code')
        deletion_type = session.get('deletion_type', 'partial')
        
        if gdpr.verify_code(current_user.id, 'deletion', verification_code):
            # Process deletion
            success, message = gdpr.process_deletion_request(
                current_user.id,
                deletion_type,
                verification_code
            )
            
            if success:
                # Record deletion
                gdpr.log_consent_activity(current_user.id, 'data_deletion_completed', {
                    'timestamp': datetime.datetime.utcnow().isoformat(),
                    'deletion_type': deletion_type
                })
                
                flash(message, 'success')
                
                # If it was a complete deletion, log out
                if deletion_type == 'complete':
                    session.clear()
                    return redirect(url_for('logout'))
                
                return redirect(url_for('gdpr.my_data'))
            else:
                flash(f'Error processing deletion request: {message}', 'danger')
        else:
            flash('Invalid verification code. Please try again.', 'danger')
    
    return render_template('gdpr/verify_data_deletion.html')

# ==================================================
# API Routes
# ==================================================

@gdpr_bp.route('/api/consent-status')
@login_required
def api_consent_status():
    """API endpoint to get user consent status"""
    consent = gdpr.get_user_consent_settings(current_user.id)
    return jsonify({'success': True, 'consent': consent})

@gdpr_bp.route('/api/update-consent', methods=['POST'])
@login_required
def api_update_consent():
    """API endpoint to update user consent"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
    
    success = gdpr.update_user_consent(current_user.id, data)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Failed to update consent'}), 500