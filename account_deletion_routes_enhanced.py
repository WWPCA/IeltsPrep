"""
Enhanced Account Deletion Routes

This module provides the Flask routes for the enhanced account deletion system
with suspension periods and reactivation functionality.
"""

from flask import request, jsonify, render_template, flash, redirect, url_for
from flask_login import login_required, current_user, logout_user
from app import app, db
from enhanced_account_deletion_service import AccountDeletionService
import logging

logger = logging.getLogger(__name__)

@app.route('/delete-account-request', methods=['POST'])
@login_required
def delete_account_request():
    """Handle account deletion request via AJAX."""
    try:
        # Process the deletion request
        result = AccountDeletionService.request_account_deletion(current_user.id)
        
        if result["success"]:
            # If deletion was scheduled (user has active assessments), logout the user
            if current_user.deletion_requested:
                logout_user()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in delete account request: {str(e)}")
        return jsonify({
            "success": False, 
            "message": "An error occurred processing your request"
        }), 500

@app.route('/reactivate-account/<token>')
def reactivate_account(token):
    """Handle account reactivation from email link."""
    try:
        result = AccountDeletionService.reactivate_account(token)
        
        if result["success"]:
            flash("Your account has been successfully reactivated! You can now log in.", "success")
            return redirect(url_for('login'))
        else:
            flash(result["message"], "error")
            return redirect(url_for('index'))
            
    except Exception as e:
        logger.error(f"Error in account reactivation: {str(e)}")
        flash("An error occurred while reactivating your account.", "error")
        return redirect(url_for('index'))

@app.route('/reactivate-account-page/<token>')
def reactivate_account_page(token):
    """Display account reactivation confirmation page."""
    return render_template('account/reactivate_account.html', token=token)

# Add route to main application
print("Enhanced account deletion routes added successfully.")