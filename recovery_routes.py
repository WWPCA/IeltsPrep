"""
Recovery Routes Module

This module provides Flask routes for handling assessment recovery functionality,
allowing users to resume or restart interrupted speaking assessments.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_required, current_user
from datetime import datetime
import logging

from assessment_recovery_system import AssessmentRecoveryManager, get_recovery_status
from account_activation import authenticated_user_required
from models import UserTestAttempt
from app import db

logger = logging.getLogger(__name__)

# Create blueprint for recovery routes
recovery_bp = Blueprint('recovery', __name__, url_prefix='/recovery')

@recovery_bp.route('/status')
@login_required
@authenticated_user_required
def recovery_status():
    """Check if recovery options are available for current user."""
    try:
        user_id = current_user.id
        assessment_id = request.args.get('assessment_id')
        
        if not assessment_id:
            return jsonify({'available': False, 'reason': 'No assessment ID provided'})
        
        recovery_options = AssessmentRecoveryManager.get_recovery_options(user_id, assessment_id)
        return jsonify(recovery_options)
        
    except Exception as e:
        logger.error(f"Failed to get recovery status: {e}")
        return jsonify({'available': False, 'reason': 'System error'})

@recovery_bp.route('/options/<assessment_id>')
@login_required
@authenticated_user_required
def show_recovery_options(assessment_id):
    """Display recovery options page for interrupted assessment."""
    try:
        user_id = current_user.id
        recovery_data = AssessmentRecoveryManager.get_recovery_options(user_id, assessment_id)
        
        if not recovery_data['available']:
            flash(f"Recovery not available: {recovery_data['reason']}", 'warning')
            return redirect(url_for('assessment_routes.speaking_assessments'))
        
        # Get assessment number for display
        assessment_record = UserTestAttempt.query.filter_by(
            user_id=user_id,
            assessment_id=assessment_id
        ).first()
        
        assessment_number = 1
        if assessment_record and assessment_record.assessment_name:
            # Extract number from assessment name like "Speaking Assessment 1"
            try:
                assessment_number = int(assessment_record.assessment_name.split()[-1])
            except:
                assessment_number = 1
        
        return render_template('assessment_recovery.html', 
                             recovery_data=recovery_data,
                             assessment_id=assessment_id,
                             assessment_number=assessment_number)
        
    except Exception as e:
        logger.error(f"Failed to show recovery options: {e}")
        flash('Unable to load recovery options. Please try again.', 'error')
        return redirect(url_for('assessment_routes.speaking_assessments'))

@recovery_bp.route('/execute/<assessment_id>', methods=['POST'])
@login_required
@authenticated_user_required
def execute_recovery(assessment_id):
    """Execute the chosen recovery option (resume or restart)."""
    try:
        user_id = current_user.id
        recovery_choice = request.form.get('recovery_choice')
        recovery_token = request.form.get('recovery_token')
        
        if not recovery_choice or not recovery_token:
            flash('Invalid recovery request. Please try again.', 'error')
            return redirect(url_for('recovery.show_recovery_options', assessment_id=assessment_id))
        
        if recovery_choice == 'resume':
            result = AssessmentRecoveryManager.resume_assessment(user_id, assessment_id, recovery_token)
            if result['success']:
                # Store recovered conversation state in session
                session['conversation_state'] = result['conversation_state']
                session['current_assessment_id'] = assessment_id
                flash(result['message'], 'success')
                return redirect(url_for('conversational_speaking.continue_conversation', assessment_id=assessment_id))
            else:
                flash(f"Resume failed: {result['error']}", 'error')
                return redirect(url_for('recovery.show_recovery_options', assessment_id=assessment_id))
        
        elif recovery_choice == 'restart':
            result = AssessmentRecoveryManager.restart_assessment(user_id, assessment_id, recovery_token)
            if result['success']:
                # Store fresh conversation state in session
                session['conversation_state'] = result['conversation_state']
                session['current_assessment_id'] = assessment_id
                flash(result['message'], 'success')
                return redirect(url_for('conversational_speaking.start_conversation', assessment_id=assessment_id))
            else:
                flash(f"Restart failed: {result['error']}", 'error')
                return redirect(url_for('recovery.show_recovery_options', assessment_id=assessment_id))
        
        else:
            flash('Invalid recovery option selected.', 'error')
            return redirect(url_for('recovery.show_recovery_options', assessment_id=assessment_id))
        
    except Exception as e:
        logger.error(f"Failed to execute recovery: {e}")
        flash('Recovery operation failed. Please contact support.', 'error')
        return redirect(url_for('assessment_routes.speaking_assessments'))

@recovery_bp.route('/save-state', methods=['POST'])
@login_required
@authenticated_user_required
def save_assessment_state():
    """API endpoint to save current assessment state for recovery."""
    try:
        user_id = current_user.id
        data = request.get_json()
        
        assessment_id = data.get('assessment_id')
        conversation_state = data.get('conversation_state')
        
        if not assessment_id or not conversation_state:
            return jsonify({'success': False, 'error': 'Missing required data'})
        
        recovery_token = AssessmentRecoveryManager.save_assessment_state(
            user_id, assessment_id, conversation_state
        )
        
        if recovery_token:
            return jsonify({
                'success': True, 
                'recovery_token': recovery_token,
                'message': 'Assessment state saved successfully'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to save state'})
        
    except Exception as e:
        logger.error(f"Failed to save assessment state via API: {e}")
        return jsonify({'success': False, 'error': 'System error'})

@recovery_bp.route('/cleanup')
@login_required
def cleanup_expired():
    """Manual cleanup of expired recovery data (admin use)."""
    try:
        # Only allow admins to trigger cleanup
        if not current_user.is_admin:
            flash('Access denied.', 'error')
            return redirect(url_for('main.index'))
        
        AssessmentRecoveryManager.cleanup_expired_recoveries()
        flash('Expired recovery data cleaned up successfully.', 'success')
        return redirect(url_for('admin_routes.admin_dashboard'))
        
    except Exception as e:
        logger.error(f"Failed to cleanup expired recoveries: {e}")
        flash('Cleanup operation failed.', 'error')
        return redirect(url_for('admin_routes.admin_dashboard'))

# JavaScript helper for automatic state saving
@recovery_bp.route('/auto-save.js')
def recovery_javascript():
    """Serve JavaScript for automatic assessment state saving."""
    js_code = """
// Automatic Assessment Recovery System
class AssessmentRecovery {
    constructor() {
        this.saveInterval = 30000; // Save every 30 seconds
        this.autoSaveTimer = null;
        this.isConnected = true;
        this.init();
    }
    
    init() {
        this.startAutoSave();
        this.monitorConnection();
        this.handlePageUnload();
    }
    
    startAutoSave() {
        this.autoSaveTimer = setInterval(() => {
            this.saveCurrentState();
        }, this.saveInterval);
    }
    
    saveCurrentState() {
        const assessmentId = window.currentAssessmentId;
        const conversationState = window.conversationState;
        
        if (!assessmentId || !conversationState) return;
        
        fetch('/recovery/save-state', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                assessment_id: assessmentId,
                conversation_state: conversationState
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Assessment state saved for recovery');
            }
        })
        .catch(error => {
            console.error('Failed to save assessment state:', error);
        });
    }
    
    monitorConnection() {
        window.addEventListener('online', () => {
            this.isConnected = true;
            this.saveCurrentState(); // Save immediately when back online
        });
        
        window.addEventListener('offline', () => {
            this.isConnected = false;
            this.showConnectionWarning();
        });
    }
    
    handlePageUnload() {
        window.addEventListener('beforeunload', (e) => {
            // Save state before page unload
            this.saveCurrentState();
        });
    }
    
    showConnectionWarning() {
        const warning = document.createElement('div');
        warning.id = 'connection-warning';
        warning.className = 'alert alert-warning position-fixed top-0 start-50 translate-middle-x';
        warning.style.zIndex = '9999';
        warning.innerHTML = `
            <i class="fas fa-wifi me-2"></i>
            Connection lost. Your progress is being saved automatically.
        `;
        document.body.appendChild(warning);
        
        // Remove warning when connection restored
        window.addEventListener('online', () => {
            const warningElement = document.getElementById('connection-warning');
            if (warningElement) {
                warningElement.remove();
            }
        });
    }
    
    manualSave() {
        this.saveCurrentState();
    }
    
    stop() {
        if (this.autoSaveTimer) {
            clearInterval(this.autoSaveTimer);
        }
    }
}

// Initialize recovery system when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.assessmentRecovery = new AssessmentRecovery();
});
    """
    
    from flask import Response
    return Response(js_code, mimetype='application/javascript')

def register_recovery_routes(app):
    """Register recovery routes with the Flask app."""
    app.register_blueprint(recovery_bp)
    
    # Add template filter for datetime formatting
    @app.template_filter('format_datetime')
    def format_datetime(value):
        if isinstance(value, str):
            try:
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                return dt.strftime('%B %d, %Y at %I:%M %p')
            except:
                return value
        return value