"""
Setup issue tracking systems and generate sample data for testing.
This script initializes the database tables for issue tracking and adds sample data.
"""

import sys
from datetime import datetime, timedelta
import random
from flask import Flask
from app import db
import models
from api_issues import APIIssueLog
from auth_issues import AuthIssueLog, log_failed_login
from models import ConnectionIssueLog, User, AssessmentSession

def setup_issue_tracking():
    """Setup issue tracking systems and generate sample data."""
    print("Setting up issue tracking systems...")
    
    # Ensure tables exist
    db.create_all()
    
    # Get a sample user
    user = User.query.first()
    if not user:
        print("No users found in the database. Please create a user first.")
        sys.exit(1)
    
    # Generate sample connection issues
    generate_sample_connection_issues(user.id)
    
    # Generate sample API issues
    generate_sample_api_issues(user.id)
    
    # Generate sample authentication issues
    generate_sample_auth_issues(user.id)
    
    print("Issue tracking systems setup complete.")

def generate_sample_connection_issues(user_id):
    """Generate sample connection issues for testing."""
    print("Generating sample connection issues...")
    
    # Clear existing data (optional)
    ConnectionIssueLog.query.delete()
    db.session.commit()
    
    # Sample products
    products = ['academic_writing', 'academic_speaking', 'general_writing', 'general_speaking']
    
    # Sample test IDs
    test_ids = list(range(1, 20))
    
    # Sample locations
    locations = [
        {'city': 'Manila', 'country': 'Philippines'},
        {'city': 'Toronto', 'country': 'Canada'},
        {'city': 'Vancouver', 'country': 'Canada'},
        {'city': 'Quezon City', 'country': 'Philippines'},
        {'city': 'Calgary', 'country': 'Canada'},
        {'city': 'Cebu', 'country': 'Philippines'},
    ]
    
    # Sample issue types
    issue_types = ['disconnect', 'reconnect', 'session_restart']
    
    # Generate 20 sample issues over the past 30 days
    now = datetime.utcnow()
    for i in range(20):
        # Random date in the past 30 days
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        occurred_at = now - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
        
        # Random product and test
        product_id = random.choice(products)
        test_id = random.choice(test_ids)
        
        # Random location
        location = random.choice(locations)
        
        # Random issue type
        issue_type = random.choice(issue_types)
        
        # Create the issue
        issue = ConnectionIssueLog(
            user_id=user_id,
            product_id=product_id,
            test_id=test_id,
            occurred_at=occurred_at,
            issue_type=issue_type,
            city=location['city'],
            country=location['country'],
            ip_address=f"192.168.0.{random.randint(1, 254)}",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            browser_info='{"browser": "Chrome", "version": "91.0.4472.124", "platform": "Windows", "language": "en-US"}',
            connection_info='{"downlink": 10, "effectiveType": "4g", "rtt": 50}'
        )
        
        # Random resolution status (70% remain open, 30% resolved)
        if random.random() < 0.3:
            issue.resolved = True
            issue.resolved_at = occurred_at + timedelta(minutes=random.randint(5, 60))
            issue.resolution_method = random.choice(['auto_restart', 'admin_action', 'user_resolved'])
        
        db.session.add(issue)
    
    db.session.commit()
    print(f"Added {20} sample connection issues.")

def generate_sample_api_issues(user_id):
    """Generate sample API issues for testing."""
    print("Generating sample API issues...")
    
    # Clear existing data (optional)
    APIIssueLog.query.delete()
    db.session.commit()
    
    # Core API services for TrueScore® and Elaris® technologies
    api_services = [
        {
            'name': 'aws_bedrock',
            'endpoints': [
                'model/amazon.nova-sonic-v1:0/invoke'
            ],
            'errors': [
                {'code': '429', 'message': 'Too Many Requests: Rate limit exceeded'},
                {'code': '400', 'message': 'Bad Request: Invalid input parameters'},
                {'code': '500', 'message': 'Internal Server Error: Service unavailable'},
                {'code': 'timeout', 'message': 'Request timed out after 30 seconds'}
            ]
        },
        {
            'name': 'azure_speech',
            'endpoints': [
                'speechtotext/recognition/conversation/cognitiveservices/v1',
                'pronunciation-assessment'
            ],
            'errors': [
                {'code': '401', 'message': 'Unauthorized: Invalid subscription key'},
                {'code': '429', 'message': 'Too Many Requests: Rate limit exceeded'},
                {'code': '500', 'message': 'Internal Server Error: Service unavailable'},
                {'code': 'timeout', 'message': 'Request timed out after 30 seconds'}
            ]
        },
        {
            'name': 'aws_transcribe',
            'endpoints': [
                'start-transcription-job',
                'get-transcription-job'
            ],
            'errors': [
                {'code': '400', 'message': 'Bad Request: Invalid parameters'},
                {'code': '429', 'message': 'Too Many Requests: Rate limit exceeded'},
                {'code': '500', 'message': 'Internal Server Error: Service unavailable'},
                {'code': 'timeout', 'message': 'Request timed out after 30 seconds'}
            ]
        }
    ]
    
    # Generate 25 sample issues over the past 30 days
    now = datetime.utcnow()
    for i in range(25):
        # Random date in the past 30 days
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        occurred_at = now - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
        
        # Random API service
        api_service = random.choice(api_services)
        api_name = api_service['name']
        
        # Random endpoint
        endpoint = random.choice(api_service['endpoints'])
        
        # Random error
        error = random.choice(api_service['errors'])
        error_code = error['code']
        error_message = error['message']
        
        # Random location
        locations = [
            {'city': 'Manila', 'country': 'Philippines'},
            {'city': 'Toronto', 'country': 'Canada'},
            {'city': 'Vancouver', 'country': 'Canada'},
            {'city': 'Quezon City', 'country': 'Philippines'},
            {'city': 'Calgary', 'country': 'Canada'},
            {'city': 'Cebu', 'country': 'Philippines'},
        ]
        location = random.choice(locations)
        
        # Sample request data
        request_data = {
            'parameters': {
                'temperature': 0.7,
                'max_tokens': 500
            },
            'prompt': 'Sample prompt text (shortened for brevity)'
        }
        
        # Sample response data for error
        response_data = {
            'error': {
                'code': error_code,
                'message': error_message
            }
        }
        
        # Create the issue
        issue = APIIssueLog(
            user_id=user_id if random.random() < 0.8 else None,  # Some requests might be system-initiated
            api_name=api_name,
            endpoint=endpoint,
            occurred_at=occurred_at,
            error_code=error_code,
            error_message=error_message,
            request_data=str(request_data),
            response_data=str(response_data),
            request_duration=random.uniform(0.5, 10.0),
            ip_address=f"192.168.0.{random.randint(1, 254)}",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            city=location['city'],
            country=location['country']
        )
        
        # Random resolution status (60% remain open, 40% resolved)
        if random.random() < 0.4:
            issue.resolved = True
            issue.resolved_at = occurred_at + timedelta(minutes=random.randint(5, 120))
            issue.resolution_notes = random.choice([
                "API service restored automatically", 
                "Increased timeout threshold",
                "Implemented exponential backoff",
                "API key refreshed",
                "False positive"
            ])
        
        db.session.add(issue)
    
    db.session.commit()
    print(f"Added {25} sample API issues.")

def generate_sample_auth_issues(user_id):
    """Generate sample authentication issues for testing."""
    print("Generating sample authentication issues...")
    
    # Clear existing data (optional)
    AuthIssueLog.query.delete()
    db.session.commit()
    
    # Sample usernames and emails (fictional)
    users = [
        {'username': 'testuser', 'email': 'testuser@example.com'},
        {'username': 'jane_doe', 'email': 'jane@example.com'},
        {'username': 'john_smith', 'email': 'john@example.com'},
        {'username': 'user123', 'email': 'user123@example.com'},
        {'username': 'newlearner', 'email': 'learner@example.com'}
    ]
    
    # Sample failure reasons
    failure_reasons = [
        'invalid_credentials',
        'user_not_found',
        'account_locked',
        'account_expired'
    ]
    
    # Sample locations
    locations = [
        {'city': 'Manila', 'country': 'Philippines'},
        {'city': 'Toronto', 'country': 'Canada'},
        {'city': 'Vancouver', 'country': 'Canada'},
        {'city': 'Quezon City', 'country': 'Philippines'},
        {'city': 'Calgary', 'country': 'Canada'},
        {'city': 'Cebu', 'country': 'Philippines'},
    ]
    
    # Generate successful logins for the real user
    now = datetime.utcnow()
    for i in range(10):
        # Random date in the past 30 days
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        occurred_at = now - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
        
        # Random location
        location = random.choice(locations)
        
        # Create the success login issue
        issue = AuthIssueLog(
            user_id=user_id,
            issue_type='login_successful',
            occurred_at=occurred_at,
            ip_address=f"192.168.0.{random.randint(1, 254)}",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            browser_info='{"browser": "Chrome", "version": "91.0.4472.124", "platform": "Windows", "language": "en-US"}',
            city=location['city'],
            country=location['country']
        )
        
        db.session.add(issue)
    
    # Generate 15 sample failed login attempts
    for i in range(15):
        # Random date in the past 30 days
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        occurred_at = now - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
        
        # Random user (not using real user_id for failed attempts)
        user = random.choice(users)
        username = user['username']
        email = user['email']
        
        # Random failure reason
        failure_reason = random.choice(failure_reasons)
        
        # Random location
        location = random.choice(locations)
        
        # Random number of attempts
        attempts = random.randint(1, 6)
        
        # Create the issue
        issue = AuthIssueLog(
            username=username,
            email=email,
            issue_type='login_failed',
            failure_reason=failure_reason,
            attempts=attempts,
            occurred_at=occurred_at,
            ip_address=f"192.168.0.{random.randint(1, 254)}",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            browser_info='{"browser": "Chrome", "version": "91.0.4472.124", "platform": "Windows", "language": "en-US"}',
            city=location['city'],
            country=location['country']
        )
        
        # Random resolution status (70% remain open, 30% resolved)
        if random.random() < 0.3:
            issue.resolved = True
            issue.resolved_at = occurred_at + timedelta(minutes=random.randint(5, 60))
            issue.resolution_notes = "Account access restored after password reset"
        
        db.session.add(issue)
    
    # Generate a few suspicious login patterns (multiple failures from same IP)
    suspicious_ips = [f"192.168.0.{random.randint(1, 254)}" for _ in range(2)]
    for ip in suspicious_ips:
        # Generate 5-10 failed attempts from the same IP
        attempts_count = random.randint(5, 10)
        for i in range(attempts_count):
            # All within last 24 hours
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            occurred_at = now - timedelta(hours=hours_ago, minutes=minutes_ago)
            
            # Random user
            user = random.choice(users)
            
            # Create the issue
            issue = AuthIssueLog(
                username=user['username'],
                email=user['email'],
                issue_type='login_failed',
                failure_reason='invalid_credentials',
                attempts=i+1,  # Increasing attempt count
                occurred_at=occurred_at,
                ip_address=ip,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                browser_info='{"browser": "Chrome", "version": "91.0.4472.124", "platform": "Windows", "language": "en-US"}',
                city='Unknown',
                country='Unknown'
            )
            
            db.session.add(issue)
    
    db.session.commit()
    print(f"Added {10} successful logins and {15 + sum(range(5, 11))} failed login attempts.")

if __name__ == "__main__":
    # Create Flask app context
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///instance/app.db"
    with app.app_context():
        setup_issue_tracking()