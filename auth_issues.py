"""
Authentication Issue Tracking Module
This module provides functionality for tracking and monitoring authentication-related issues.
"""
import json
from datetime import datetime, timedelta
from sqlalchemy import func, and_
from app import db
from models import User

class AuthIssueLog(db.Model):
    """Track authentication-related issues for monitoring and support purposes"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Can be null for failed logins
    username = db.Column(db.String(64), nullable=True)  # Store username for failed login attempts
    email = db.Column(db.String(120), nullable=True)  # Store email for failed login attempts
    occurred_at = db.Column(db.DateTime, default=datetime.utcnow)
    issue_type = db.Column(db.String(50), nullable=False)  # login_failed, account_locked, password_reset, etc.
    failure_reason = db.Column(db.String(100), nullable=True)  # invalid_credentials, account_expired, etc.
    attempts = db.Column(db.Integer, nullable=True)  # Number of failed attempts (if applicable)
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    browser_info = db.Column(db.Text, nullable=True)  # JSON string with browser details
    city = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    resolved = db.Column(db.Boolean, default=False)
    resolved_at = db.Column(db.DateTime, nullable=True)
    resolution_notes = db.Column(db.Text, nullable=True)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('auth_issues', lazy=True))
    
    def __repr__(self):
        return f'<AuthIssueLog {self.id} - {"User " + str(self.user_id) if self.user_id else self.username or self.email or "Unknown"} - {self.issue_type}>'
        
    @classmethod
    def log_issue(cls, issue_type, request_obj=None, **kwargs):
        """Log an authentication issue with details from request and additional data"""
        log_entry = cls(
            issue_type=issue_type,
            user_id=kwargs.get('user_id'),
            username=kwargs.get('username'),
            email=kwargs.get('email'),
            failure_reason=kwargs.get('failure_reason'),
            attempts=kwargs.get('attempts')
        )
        
        # Capture request data if available
        if request_obj:
            log_entry.ip_address = request_obj.remote_addr
            log_entry.user_agent = request_obj.user_agent.string
            
            # Extract and store browser info
            browser_info = {
                'browser': request_obj.user_agent.browser,
                'version': request_obj.user_agent.version,
                'platform': request_obj.user_agent.platform,
                'language': request_obj.accept_languages.best
            }
            log_entry.browser_info = json.dumps(browser_info)
            
            # Try to get location data from IP using geoip if available
            try:
                if log_entry.ip_address and hasattr(request_obj, 'geoip'):
                    log_entry.city = request_obj.geoip.get('city')
                    log_entry.country = request_obj.geoip.get('country_name')
            except:
                pass  # Ignore geoip errors
        
        db.session.add(log_entry)
        db.session.commit()
        return log_entry
        
    @classmethod
    def mark_resolved(cls, issue_id, resolution_notes=None):
        """Mark an authentication issue as resolved with optional notes"""
        log_entry = cls.query.get(issue_id)
        if log_entry:
            log_entry.resolved = True
            log_entry.resolved_at = datetime.utcnow()
            if resolution_notes:
                log_entry.resolution_notes = resolution_notes
            db.session.commit()
            return True
        return False

    @classmethod
    def check_suspicious_activity(cls, username=None, email=None, ip_address=None, hours=24, threshold=5):
        """
        Check if there's suspicious login activity for a given user or IP address.
        
        Args:
            username (str, optional): Username to check
            email (str, optional): Email to check
            ip_address (str, optional): IP address to check
            hours (int, optional): Number of hours to look back
            threshold (int, optional): Number of failures that constitute suspicious activity
            
        Returns:
            bool: True if suspicious activity detected, False otherwise
        """
        from sqlalchemy import or_
        
        # Calculate the lookback time
        since_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Build the query based on available parameters
        filters = [
            AuthIssueLog.occurred_at >= since_time,
            AuthIssueLog.issue_type == 'login_failed'
        ]
        
        if username:
            filters.append(AuthIssueLog.username == username)
        if email:
            filters.append(AuthIssueLog.email == email)
        if ip_address:
            filters.append(AuthIssueLog.ip_address == ip_address)
            
        # Must have at least one identifier
        if not username and not email and not ip_address:
            return False
            
        # Count failed login attempts
        count = AuthIssueLog.query.filter(and_(*filters)).count()
        
        return count >= threshold

# Utility functions for authentication error handling
def log_failed_login(username=None, email=None, failure_reason=None, request_obj=None):
    """
    Log a failed login attempt.
    
    Args:
        username (str, optional): Username used in the login attempt
        email (str, optional): Email used in the login attempt
        failure_reason (str, optional): Reason for the failure
        request_obj (Request, optional): Flask request object
        
    Returns:
        AuthIssueLog: The created log entry
    """
    # Calculate number of previous failed attempts for this username/email
    attempts = 1
    since_time = datetime.utcnow() - timedelta(hours=24)
    
    # Build the query based on available parameters
    filters = [
        AuthIssueLog.occurred_at >= since_time,
        AuthIssueLog.issue_type == 'login_failed'
    ]
    
    if username:
        filters.append(AuthIssueLog.username == username)
    elif email:
        filters.append(AuthIssueLog.email == email)
        
    if username or email:
        attempts += AuthIssueLog.query.filter(and_(*filters)).count()
    
    return AuthIssueLog.log_issue(
        issue_type='login_failed',
        username=username,
        email=email,
        failure_reason=failure_reason,
        attempts=attempts,
        request_obj=request_obj
    )

def log_successful_login(user_id, request_obj=None):
    """
    Log a successful login (important for tracking login patterns).
    
    Args:
        user_id (int): User ID of the logged in user
        request_obj (Request, optional): Flask request object
        
    Returns:
        AuthIssueLog: The created log entry
    """
    return AuthIssueLog.log_issue(
        issue_type='login_successful',
        user_id=user_id,
        request_obj=request_obj
    )

def get_auth_issue_statistics(days=30):
    """
    Get statistics about authentication issues for monitoring dashboards.
    
    Args:
        days (int, optional): Number of days to look back, defaults to 30
    
    Returns:
        dict: Statistics about authentication issues
    """
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Base query
    query = AuthIssueLog.query.filter(AuthIssueLog.occurred_at >= start_date)
    
    # Total issues
    total_issues = query.count()
    
    # Failed logins
    failed_logins = query.filter(AuthIssueLog.issue_type == 'login_failed').count()
    
    # Successful logins
    successful_logins = query.filter(AuthIssueLog.issue_type == 'login_successful').count()
    
    # Success rate
    success_rate = (successful_logins / (successful_logins + failed_logins) * 100) if (successful_logins + failed_logins) > 0 else 0
    
    # Issues by failure reason
    issues_by_reason = db.session.query(
        AuthIssueLog.failure_reason, 
        func.count(AuthIssueLog.id)
    ).filter(
        and_(
            AuthIssueLog.occurred_at >= start_date,
            AuthIssueLog.failure_reason.isnot(None)
        )
    ).group_by(
        AuthIssueLog.failure_reason
    ).all()
    
    # Issues by country
    issues_by_country = db.session.query(
        AuthIssueLog.country, 
        func.count(AuthIssueLog.id)
    ).filter(
        and_(
            AuthIssueLog.occurred_at >= start_date,
            AuthIssueLog.country.isnot(None),
            AuthIssueLog.issue_type == 'login_failed'
        )
    ).group_by(
        AuthIssueLog.country
    ).order_by(
        func.count(AuthIssueLog.id).desc()
    ).limit(10).all()
    
    return {
        'total_issues': total_issues,
        'failed_logins': failed_logins,
        'successful_logins': successful_logins,
        'success_rate': success_rate,
        'issues_by_reason': issues_by_reason,
        'issues_by_country': issues_by_country
    }