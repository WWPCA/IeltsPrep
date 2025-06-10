"""
Simplified Admin Routes Module for Mobile App Store Operations
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from functools import wraps
from flask_login import login_required, current_user
from models import db, User, ConnectionIssueLog, AssessmentSession, Assessment
from api_issues import APIIssueLog, get_api_issue_statistics
from scheduled_tasks import execute_daily_tasks_now, execute_weekly_tasks_now
from enhanced_email_service import email_service
from sqlalchemy import func, distinct, and_
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger()

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorator to check if the current user is an administrator."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('You must be logged in to access this page.', 'error')
            return redirect(url_for('login'))
        
        if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
            flash('Administrator access required.', 'error')
            return redirect(url_for('index'))
        
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@admin_required
def admin_dashboard():
    """Simplified admin dashboard for mobile app operations."""
    try:
        # Basic user statistics
        total_users = User.query.count()
        recent_users = User.query.filter(
            User.id >= func.max(User.id) - 100
        ).count()
        
        # Assessment statistics
        total_assessments = Assessment.query.count()
        recent_assessments = AssessmentSession.query.count()
        
        # API issue statistics
        api_stats = get_api_issue_statistics()
        
        # Connection issues
        connection_issues = ConnectionIssueLog.query.filter(
            ConnectionIssueLog.resolved == False
        ).count()
        
        return render_template('admin/simple_dashboard.html',
                             total_users=total_users,
                             recent_users=recent_users,
                             total_assessments=total_assessments,
                             recent_assessments=recent_assessments,
                             api_stats=api_stats,
                             connection_issues=connection_issues)
    
    except Exception as e:
        logger.error(f"Error loading admin dashboard: {e}")
        flash('Error loading dashboard data.', 'error')
        return render_template('admin/simple_dashboard.html',
                             total_users=0,
                             recent_users=0,
                             total_assessments=0,
                             recent_assessments=0,
                             api_stats={},
                             connection_issues=0)

@admin_bp.route('/users')
@admin_required
def user_list():
    """Simple user management interface."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        users = User.query.order_by(User.id.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return render_template('admin/users.html', users=users)
    
    except Exception as e:
        logger.error(f"Error loading users: {e}")
        flash('Error loading user data.', 'error')
        return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/api-issues')
@admin_required
def api_issues():
    """API issues dashboard."""
    try:
        # Filter parameters
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        api_name = request.args.get('api_name')
        
        # Build the query with filters
        query = APIIssueLog.query
        
        if date_from:
            try:
                from_date = datetime.strptime(date_from, '%Y-%m-%d')
                query = query.filter(APIIssueLog.occurred_at >= from_date)
            except ValueError:
                pass
        
        if date_to:
            try:
                to_date = datetime.strptime(date_to, '%Y-%m-%d')
                to_date = to_date + timedelta(days=1)
                query = query.filter(APIIssueLog.occurred_at <= to_date)
            except ValueError:
                pass
        
        if api_name:
            query = query.filter(APIIssueLog.api_name == api_name)
        
        issues = query.order_by(APIIssueLog.occurred_at.desc()).limit(100).all()
        
        # Get metrics
        metrics = get_api_issue_statistics()
        
        return render_template('admin/api_issues.html',
                             issues=issues,
                             metrics=metrics,
                             filters={
                                 'date_from': date_from,
                                 'date_to': date_to,
                                 'api_name': api_name
                             })
    
    except Exception as e:
        logger.error(f"Error loading API issues: {e}")
        flash('Error loading API issues.', 'error')
        return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/test-email', methods=['POST'])
@admin_required
def test_email_sending():
    """Test email sending functionality."""
    try:
        test_email = request.form.get('test_email', current_user.email)
        
        if email_service.send_email(
            to_email=test_email,
            subject="IELTS GenAI Prep - Email Test",
            html_content="<h2>Email System Test</h2><p>This is a test email from the admin panel.</p>",
            text_content="Email System Test - This is a test email from the admin panel."
        ):
            flash(f'Test email sent successfully to {test_email}', 'success')
        else:
            flash('Failed to send test email', 'error')
    
    except Exception as e:
        logger.error(f"Error sending test email: {e}")
        flash(f'Error sending test email: {str(e)}', 'error')
    
    return redirect(url_for('admin.admin_dashboard'))

# Register the blueprint
def register_admin_routes(app):
    """Register admin routes with the app."""
    app.register_blueprint(admin_bp)