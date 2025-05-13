"""
Admin Routes Module
This module provides administrator routes for the IELTS preparation platform.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, User, ConnectionIssueLog, AssessmentSession, Assessment
from api_issues import APIIssueLog, get_api_issue_statistics
from auth_issues import AuthIssueLog, get_auth_issue_statistics
from sqlalchemy import func, distinct, and_
from datetime import datetime, timedelta
import json

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Decorator to check if the user is an admin
def admin_required(f):
    """Decorator to check if the current user is an administrator."""
    def decorated_function(*args, **kwargs):
        # is_admin field removed as it doesn't exist in database
        # Using Value Pack subscription as a temporary way to identify admins
        if not current_user.is_authenticated or current_user.subscription_status != "Value Pack":
            flash("You don't have permission to access this page.", "danger")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def admin_dashboard():
    """Admin dashboard homepage."""
    # Count total users
    total_users = User.query.count()
    
    # Count users registered in the last 7 days
    last_week = datetime.utcnow() - timedelta(days=7)
    new_users = User.query.filter(User.join_date >= last_week).count()
    
    # Count total connection issues
    total_issues = ConnectionIssueLog.query.count()
    
    # Count open connection issues
    open_issues = ConnectionIssueLog.query.filter_by(resolved=False).count()
    
    # Get recent connection issues
    recent_issues = ConnectionIssueLog.query.order_by(
        ConnectionIssueLog.occurred_at.desc()
    ).limit(5).all()
    
    # Prepare data for the template
    data = {
        'total_users': total_users,
        'new_users': new_users,
        'total_issues': total_issues,
        'open_issues': open_issues,
        'recent_issues': recent_issues
    }
    
    return render_template('admin/dashboard.html', **data)

@admin_bp.route('/connection-issues')
@login_required
@admin_required
def connection_issues():
    """Connection issues dashboard."""
    # Retrieve filter parameters
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    issue_type = request.args.get('issue_type')
    product_id = request.args.get('product_id')
    country = request.args.get('country')
    city = request.args.get('city')
    user_id = request.args.get('user_id')
    
    # Build the query with filters
    query = ConnectionIssueLog.query
    
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(ConnectionIssueLog.occurred_at >= from_date)
        except ValueError:
            pass
    
    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d')
            # Add a day to include the end date
            to_date = to_date + timedelta(days=1)
            query = query.filter(ConnectionIssueLog.occurred_at <= to_date)
        except ValueError:
            pass
    
    if issue_type:
        query = query.filter(ConnectionIssueLog.issue_type == issue_type)
    
    if product_id:
        query = query.filter(ConnectionIssueLog.product_id == product_id)
    
    if country:
        query = query.filter(ConnectionIssueLog.country.ilike(f'%{country}%'))
    
    if city:
        query = query.filter(ConnectionIssueLog.city.ilike(f'%{city}%'))
    
    if user_id:
        try:
            user_id_int = int(user_id)
            query = query.filter(ConnectionIssueLog.user_id == user_id_int)
        except ValueError:
            pass
    
    # Get the results
    issues = query.order_by(ConnectionIssueLog.occurred_at.desc()).all()
    
    # Get metrics
    metrics = {
        'total_disconnects': ConnectionIssueLog.query.filter(
            ConnectionIssueLog.issue_type == 'disconnect'
        ).count(),
        'total_reconnects': ConnectionIssueLog.query.filter(
            ConnectionIssueLog.issue_type == 'reconnect'
        ).count(),
        'total_restarts': ConnectionIssueLog.query.filter(
            ConnectionIssueLog.issue_type == 'session_restart'
        ).count(),
        'unique_users': db.session.query(
            func.count(distinct(ConnectionIssueLog.user_id))
        ).scalar()
    }
    
    # Provide the filters for form repopulation
    filters = {
        'date_from': date_from,
        'date_to': date_to,
        'issue_type': issue_type,
        'product_id': product_id,
        'country': country,
        'city': city,
        'user_id': user_id
    }
    
    return render_template(
        'admin/connection_issues.html',
        issues=issues,
        metrics=metrics,
        filters=filters
    )

@admin_bp.route('/connection-issues/<int:issue_id>/resolve', methods=['POST'])
@login_required
@admin_required
def mark_issue_resolved(issue_id):
    """Mark a connection issue as resolved."""
    issue = ConnectionIssueLog.query.get_or_404(issue_id)
    resolution_method = request.form.get('resolution_method', 'admin_action')
    
    # Mark the issue as resolved
    issue.resolved = True
    issue.resolved_at = datetime.utcnow()
    issue.resolution_method = resolution_method
    
    db.session.add(issue)
    db.session.commit()
    
    flash(f"Issue #{issue_id} has been marked as resolved.", "success")
    return redirect(url_for('admin.connection_issues'))

@admin_bp.route('/user/<int:user_id>')
@login_required
@admin_required
def user_profile(user_id):
    """View a user's profile and connection history."""
    user = User.query.get_or_404(user_id)
    
    # Get the user's connection issues
    connection_issues = ConnectionIssueLog.query.filter_by(
        user_id=user_id
    ).order_by(ConnectionIssueLog.occurred_at.desc()).all()
    
    # Get the user's session history
    sessions = AssessmentSession.query.filter_by(
        user_id=user_id
    ).order_by(AssessmentSession.started_at.desc()).all()
    
    return render_template(
        'admin/user_profile.html',
        user=user,
        connection_issues=connection_issues,
        sessions=sessions
    )

@admin_bp.route('/reports/connection-issues')
@login_required
@admin_required
def connection_issues_report():
    """Generate detailed report on connection issues."""
    # Get time period
    period = request.args.get('period', 'week')
    
    if period == 'day':
        start_date = datetime.utcnow() - timedelta(days=1)
        title = 'Last 24 Hours'
    elif period == 'week':
        start_date = datetime.utcnow() - timedelta(days=7)
        title = 'Last 7 Days'
    elif period == 'month':
        start_date = datetime.utcnow() - timedelta(days=30)
        title = 'Last 30 Days'
    else:
        start_date = datetime.utcnow() - timedelta(days=7)
        title = 'Last 7 Days'
    
    # Issues by type
    issues_by_type = db.session.query(
        ConnectionIssueLog.issue_type, 
        func.count(ConnectionIssueLog.id)
    ).filter(
        ConnectionIssueLog.occurred_at >= start_date
    ).group_by(
        ConnectionIssueLog.issue_type
    ).all()
    
    # Issues by product
    issues_by_product = db.session.query(
        ConnectionIssueLog.product_id, 
        func.count(ConnectionIssueLog.id)
    ).filter(
        and_(
            ConnectionIssueLog.occurred_at >= start_date,
            ConnectionIssueLog.product_id.isnot(None)
        )
    ).group_by(
        ConnectionIssueLog.product_id
    ).all()
    
    # Issues by country
    issues_by_country = db.session.query(
        ConnectionIssueLog.country, 
        func.count(ConnectionIssueLog.id)
    ).filter(
        and_(
            ConnectionIssueLog.occurred_at >= start_date,
            ConnectionIssueLog.country.isnot(None)
        )
    ).group_by(
        ConnectionIssueLog.country
    ).order_by(
        func.count(ConnectionIssueLog.id).desc()
    ).limit(10).all()
    
    # Resolution rate
    total_issues = ConnectionIssueLog.query.filter(
        ConnectionIssueLog.occurred_at >= start_date
    ).count()
    
    resolved_issues = ConnectionIssueLog.query.filter(
        and_(
            ConnectionIssueLog.occurred_at >= start_date,
            ConnectionIssueLog.resolved == True
        )
    ).count()
    
    resolution_rate = (resolved_issues / total_issues * 100) if total_issues > 0 else 0
    
    # Prepare data for the template
    report_data = {
        'title': title,
        'period': period,
        'issues_by_type': issues_by_type,
        'issues_by_product': issues_by_product,
        'issues_by_country': issues_by_country,
        'total_issues': total_issues,
        'resolved_issues': resolved_issues,
        'resolution_rate': resolution_rate
    }
    
    return render_template('admin/connection_issues_report.html', **report_data)

@admin_bp.route('/api-issues')
@login_required
@admin_required
def api_issues():
    """API issues dashboard."""
    # Retrieve filter parameters
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    api_name = request.args.get('api_name')
    error_code = request.args.get('error_code')
    user_id = request.args.get('user_id')
    endpoint = request.args.get('endpoint')
    resolved = request.args.get('resolved')
    
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
            # Add a day to include the end date
            to_date = to_date + timedelta(days=1)
            query = query.filter(APIIssueLog.occurred_at <= to_date)
        except ValueError:
            pass
    
    if api_name:
        query = query.filter(APIIssueLog.api_name == api_name)
    
    if error_code:
        query = query.filter(APIIssueLog.error_code.ilike(f'%{error_code}%'))
    
    if endpoint:
        query = query.filter(APIIssueLog.endpoint.ilike(f'%{endpoint}%'))
    
    if resolved:
        if resolved.lower() == 'true':
            query = query.filter(APIIssueLog.resolved == True)
        elif resolved.lower() == 'false':
            query = query.filter(APIIssueLog.resolved == False)
    
    if user_id:
        try:
            user_id_int = int(user_id)
            query = query.filter(APIIssueLog.user_id == user_id_int)
        except ValueError:
            pass
    
    # Get the results
    issues = query.order_by(APIIssueLog.occurred_at.desc()).all()
    
    # Get metrics from statistics function
    metrics = get_api_issue_statistics(api_name=api_name)
    
    # Provide the filters for form repopulation
    filters = {
        'date_from': date_from,
        'date_to': date_to,
        'api_name': api_name,
        'error_code': error_code,
        'endpoint': endpoint,
        'resolved': resolved,
        'user_id': user_id
    }
    
    return render_template(
        'admin/api_issues.html',
        issues=issues,
        metrics=metrics,
        filters=filters
    )

@admin_bp.route('/api-issues/<int:issue_id>/resolve', methods=['POST'])
@login_required
@admin_required
def mark_api_issue_resolved(issue_id):
    """Mark an API issue as resolved."""
    resolution_notes = request.form.get('resolution_notes', '')
    
    if APIIssueLog.mark_resolved(issue_id, resolution_notes):
        flash(f"API issue #{issue_id} has been marked as resolved.", "success")
    else:
        flash(f"Failed to mark API issue #{issue_id} as resolved.", "danger")
        
    return redirect(url_for('admin.api_issues'))

@admin_bp.route('/auth-issues')
@login_required
@admin_required
def auth_issues():
    """Authentication issues dashboard."""
    # Retrieve filter parameters
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    issue_type = request.args.get('issue_type')
    failure_reason = request.args.get('failure_reason')
    username = request.args.get('username')
    email = request.args.get('email')
    ip_address = request.args.get('ip_address')
    
    # Build the query with filters
    query = AuthIssueLog.query
    
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(AuthIssueLog.occurred_at >= from_date)
        except ValueError:
            pass
    
    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d')
            # Add a day to include the end date
            to_date = to_date + timedelta(days=1)
            query = query.filter(AuthIssueLog.occurred_at <= to_date)
        except ValueError:
            pass
    
    if issue_type:
        query = query.filter(AuthIssueLog.issue_type == issue_type)
    
    if failure_reason:
        query = query.filter(AuthIssueLog.failure_reason == failure_reason)
    
    if username:
        query = query.filter(AuthIssueLog.username.ilike(f'%{username}%'))
    
    if email:
        query = query.filter(AuthIssueLog.email.ilike(f'%{email}%'))
    
    if ip_address:
        query = query.filter(AuthIssueLog.ip_address == ip_address)
    
    # Get the results
    issues = query.order_by(AuthIssueLog.occurred_at.desc()).all()
    
    # Get metrics from statistics function
    metrics = get_auth_issue_statistics()
    
    # Get suspicious activity
    # Find users or IPs with high failure counts in the last 24 hours
    day_ago = datetime.utcnow() - timedelta(days=1)
    
    # Group by IP address
    ip_failures = db.session.query(
        AuthIssueLog.ip_address,
        func.count(AuthIssueLog.id).label('attempts')
    ).filter(
        and_(
            AuthIssueLog.occurred_at >= day_ago,
            AuthIssueLog.issue_type == 'login_failed',
            AuthIssueLog.ip_address.isnot(None)
        )
    ).group_by(
        AuthIssueLog.ip_address
    ).having(
        func.count(AuthIssueLog.id) >= 5  # 5 or more attempts is suspicious
    ).all()
    
    # Format suspicious activity for display
    suspicious_activity = []
    
    for ip, attempts in ip_failures:
        # Get the most recent failed attempt for this IP
        recent = AuthIssueLog.query.filter(
            and_(
                AuthIssueLog.ip_address == ip,
                AuthIssueLog.issue_type == 'login_failed'
            )
        ).order_by(AuthIssueLog.occurred_at.desc()).first()
        
        if recent:
            suspicious_activity.append({
                'ip_address': ip,
                'attempts': attempts,
                'username': recent.username,
                'email': recent.email,
                'city': recent.city,
                'country': recent.country,
                'last_attempt': recent.occurred_at
            })
    
    # Provide the filters for form repopulation
    filters = {
        'date_from': date_from,
        'date_to': date_to,
        'issue_type': issue_type,
        'failure_reason': failure_reason,
        'username': username,
        'email': email,
        'ip_address': ip_address
    }
    
    return render_template(
        'admin/auth_issues.html',
        issues=issues,
        metrics=metrics,
        filters=filters,
        suspicious_activity=suspicious_activity,
        suspicious_activity_count=len(suspicious_activity)
    )

@admin_bp.route('/auth-issues/<int:issue_id>/resolve', methods=['POST'])
@login_required
@admin_required
def mark_auth_issue_resolved(issue_id):
    """Mark an authentication issue as resolved."""
    resolution_notes = request.form.get('resolution_notes', '')
    
    if AuthIssueLog.mark_resolved(issue_id, resolution_notes):
        flash(f"Authentication issue #{issue_id} has been marked as resolved.", "success")
    else:
        flash(f"Failed to mark authentication issue #{issue_id} as resolved.", "danger")
        
    return redirect(url_for('admin.auth_issues'))

@admin_bp.route('/api/connection-issues/summary')
@login_required
@admin_required
def connection_issues_summary_api():
    """API endpoint for connection issues summary data."""
    # Get time period
    days = int(request.args.get('days', 7))
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get daily counts
    daily_counts = db.session.query(
        func.date(ConnectionIssueLog.occurred_at).label('date'),
        func.count(ConnectionIssueLog.id).label('count')
    ).filter(
        ConnectionIssueLog.occurred_at >= start_date
    ).group_by(
        func.date(ConnectionIssueLog.occurred_at)
    ).order_by(
        func.date(ConnectionIssueLog.occurred_at)
    ).all()
    
    # Format for JSON response
    date_counts = [
        {
            'date': date.strftime('%Y-%m-%d'),
            'count': count
        }
        for date, count in daily_counts
    ]
    
    return jsonify({
        'success': True,
        'data': date_counts
    })

