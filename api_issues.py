"""
API Issue Tracking Module
This module provides functionality for tracking and monitoring API-related issues.
"""
import json
from datetime import datetime
from app import db
from models import User

class APIIssueLog(db.Model):
    """Track API-related issues for monitoring and support purposes"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Can be null for unauthenticated requests
    api_name = db.Column(db.String(100), nullable=False)  # aws_bedrock, openai, polly, etc.
    endpoint = db.Column(db.String(255), nullable=False)  # Specific endpoint that failed
    occurred_at = db.Column(db.DateTime, default=datetime.utcnow)
    error_code = db.Column(db.String(100), nullable=True)  # HTTP status code or API-specific error code
    error_message = db.Column(db.Text, nullable=True)  # Original error message
    request_data = db.Column(db.Text, nullable=True)  # JSON string with request data (sanitized)
    response_data = db.Column(db.Text, nullable=True)  # JSON string with response data
    request_duration = db.Column(db.Float, nullable=True)  # Request duration in seconds
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    resolved = db.Column(db.Boolean, default=False)
    resolved_at = db.Column(db.DateTime, nullable=True)
    resolution_notes = db.Column(db.Text, nullable=True)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('api_issues', lazy=True))
    
    def __repr__(self):
        return f'<APIIssueLog {self.id} - API {self.api_name} - {self.error_code}>'
        
    @classmethod
    def log_issue(cls, api_name, endpoint, error_code=None, error_message=None, request_obj=None, 
                 user_id=None, request_data=None, response_data=None, request_duration=None):
        """Log an API issue with details"""
        # Sanitize request and response data to remove sensitive information
        if request_data:
            if isinstance(request_data, dict):
                # Remove any sensitive fields
                sanitized_data = request_data.copy()
                for key in ['password', 'token', 'key', 'secret', 'auth', 'authorization']:
                    if key in sanitized_data:
                        sanitized_data[key] = '[REDACTED]'
                request_data = json.dumps(sanitized_data)
            elif isinstance(request_data, str):
                request_data = request_data
        
        log_entry = cls(
            user_id=user_id,
            api_name=api_name,
            endpoint=endpoint,
            error_code=error_code,
            error_message=error_message,
            request_data=request_data,
            response_data=response_data if isinstance(response_data, str) else json.dumps(response_data) if response_data else None,
            request_duration=request_duration
        )
        
        # Capture request data if available
        if request_obj:
            log_entry.ip_address = request_obj.remote_addr
            if hasattr(request_obj, 'user_agent'):
                log_entry.user_agent = request_obj.user_agent.string
                
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
        """Mark an API issue as resolved with optional notes"""
        log_entry = cls.query.get(issue_id)
        if log_entry:
            log_entry.resolved = True
            log_entry.resolved_at = datetime.utcnow()
            if resolution_notes:
                log_entry.resolution_notes = resolution_notes
            db.session.commit()
            return True
        return False

# Utility functions for API error handling
def log_api_error(api_name, endpoint, error, request_obj=None, user_id=None, request_data=None, response_data=None, request_duration=None):
    """
    Utility function to log API errors consistently across the application.
    
    Args:
        api_name (str): Name of the API service (e.g., 'aws_bedrock', 'openai')
        endpoint (str): Specific API endpoint that was called
        error (Exception): The error that occurred
        request_obj (Request, optional): Flask request object
        user_id (int, optional): User ID if authenticated
        request_data (dict, optional): Data sent in the request
        response_data (dict, optional): Data received in the response
        request_duration (float, optional): Duration of the request in seconds
    
    Returns:
        APIIssueLog: The created log entry
    """
    # Extract error code and message
    error_code = getattr(error, 'code', None) or getattr(error, 'status_code', None)
    if error_code is None and hasattr(error, 'response') and hasattr(error.response, 'status_code'):
        error_code = error.response.status_code
        
    error_message = str(error)
    
    return APIIssueLog.log_issue(
        api_name=api_name,
        endpoint=endpoint, 
        error_code=error_code,
        error_message=error_message,
        request_obj=request_obj,
        user_id=user_id,
        request_data=request_data,
        response_data=response_data,
        request_duration=request_duration
    )

def get_api_issue_statistics(api_name=None, days=30):
    """
    Get statistics about API issues for monitoring dashboards.
    
    Args:
        api_name (str, optional): Filter by specific API name
        days (int, optional): Number of days to look back, defaults to 30
    
    Returns:
        dict: Statistics about API issues
    """
    from datetime import datetime, timedelta
    from sqlalchemy import func, and_
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Base query
    query = APIIssueLog.query.filter(APIIssueLog.occurred_at >= start_date)
    
    # Apply API name filter if provided
    if api_name:
        query = query.filter(APIIssueLog.api_name == api_name)
    
    # Total issues
    total_issues = query.count()
    
    # Resolved issues
    resolved_issues = query.filter(APIIssueLog.resolved == True).count()
    
    # Resolution rate
    resolution_rate = (resolved_issues / total_issues * 100) if total_issues > 0 else 0
    
    # Issues by API
    issues_by_api = db.session.query(
        APIIssueLog.api_name, 
        func.count(APIIssueLog.id)
    ).filter(
        APIIssueLog.occurred_at >= start_date
    ).group_by(
        APIIssueLog.api_name
    ).all()
    
    # Issues by error code
    issues_by_error = db.session.query(
        APIIssueLog.error_code, 
        func.count(APIIssueLog.id)
    ).filter(
        and_(
            APIIssueLog.occurred_at >= start_date,
            APIIssueLog.error_code.isnot(None)
        )
    ).group_by(
        APIIssueLog.error_code
    ).all()
    
    # Average request duration
    avg_duration = db.session.query(
        func.avg(APIIssueLog.request_duration)
    ).filter(
        and_(
            APIIssueLog.occurred_at >= start_date,
            APIIssueLog.request_duration.isnot(None)
        )
    ).scalar()
    
    return {
        'total_issues': total_issues,
        'resolved_issues': resolved_issues,
        'resolution_rate': resolution_rate,
        'issues_by_api': issues_by_api,
        'issues_by_error': issues_by_error,
        'avg_duration': avg_duration or 0
    }