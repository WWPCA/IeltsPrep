"""
API Issue Tracking Module
This module provides functionality for tracking and monitoring API-related issues.
"""

import json
from datetime import datetime, timedelta
from app import db
from flask import request

class APIIssueLog(db.Model):
    """Track API-related issues for monitoring and support purposes"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    api_name = db.Column(db.String(100), nullable=False)
    endpoint = db.Column(db.String(255), nullable=False)
    occurred_at = db.Column(db.DateTime, default=datetime.utcnow)
    error_code = db.Column(db.String(100), nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    request_data = db.Column(db.Text, nullable=True)
    response_data = db.Column(db.Text, nullable=True)
    request_duration = db.Column(db.Float, nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    attempt_count = db.Column(db.Integer, default=1)
    resolved = db.Column(db.Boolean, default=False)
    resolved_at = db.Column(db.DateTime, nullable=True)
    resolution_notes = db.Column(db.Text, nullable=True)

    user = db.relationship('User', backref=db.backref('api_issues', lazy=True))

    def __repr__(self):
        return f'<APIIssueLog {self.api_name}:{self.endpoint}>'

    @classmethod
    def log_issue(cls, api_name, endpoint, error_code=None, error_message=None, request_obj=None, 
                 user_id=None, request_data=None, response_data=None, request_duration=None):
        """Log an API issue with details"""
        try:
            issue = cls(
                api_name=api_name,
                endpoint=endpoint,
                error_code=error_code,
                error_message=str(error_message) if error_message else None,
                user_id=user_id,
                request_data=json.dumps(request_data) if request_data else None,
                response_data=json.dumps(response_data) if response_data else None,
                request_duration=request_duration,
                ip_address=request_obj.remote_addr if request_obj else None,
                user_agent=request_obj.headers.get('User-Agent') if request_obj else None
            )
            
            db.session.add(issue)
            db.session.commit()
            return issue
        except Exception as e:
            db.session.rollback()
            print(f"Failed to log API issue: {e}")
            return None

    @classmethod
    def mark_resolved(cls, issue_id, resolution_notes=None):
        """Mark an API issue as resolved with optional notes"""
        try:
            issue = cls.query.get(issue_id)
            if issue:
                issue.resolved = True
                issue.resolved_at = datetime.utcnow()
                issue.resolution_notes = resolution_notes
                db.session.commit()
                return True
        except Exception as e:
            db.session.rollback()
            print(f"Failed to mark issue as resolved: {e}")
        return False

def log_api_error(api_name, endpoint, error, request_obj=None, user_id=None, request_data=None, response_data=None, request_duration=None):
    """
    Utility function to log API errors consistently across the application.
    """
    return APIIssueLog.log_issue(
        api_name=api_name,
        endpoint=endpoint,
        error_code=getattr(error, 'code', None),
        error_message=str(error),
        request_obj=request_obj,
        user_id=user_id,
        request_data=request_data,
        response_data=response_data,
        request_duration=request_duration
    )

def get_api_issue_statistics(api_name=None, days=30):
    """
    Get statistics about API issues for monitoring dashboards.
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    query = APIIssueLog.query.filter(APIIssueLog.occurred_at >= cutoff_date)
    
    if api_name:
        query = query.filter(APIIssueLog.api_name == api_name)
    
    total_issues = query.count()
    resolved_issues = query.filter(APIIssueLog.resolved == True).count()
    unresolved_issues = total_issues - resolved_issues
    
    return {
        'total_issues': total_issues,
        'resolved_issues': resolved_issues,
        'unresolved_issues': unresolved_issues,
        'resolution_rate': round((resolved_issues / total_issues * 100) if total_issues > 0 else 0, 2)
    }