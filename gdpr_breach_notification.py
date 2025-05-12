"""
GDPR Breach Notification System
This module provides functions for automated breach detection, assessment, and notification.
"""

import os
import json
import logging
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import requests
from flask import render_template
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app import db
from models import User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Data Protection Authority contact information
DPA_CONTACTS = {
    'CA': {
        'name': 'Office of the Privacy Commissioner',
        'method': 'web_form',
        'url': 'https://www.priv.gc.ca/en/report-a-concern/',
        'email': 'notification@priv.gc.ca'
    },
    'US': {
        'name': 'Federal Trade Commission',
        'method': 'portal',
        'url': 'https://www.ftccomplaintassistant.gov/',
        'email': 'security@ftc.gov'
    },
    'IN': {
        'name': 'Data Protection Authority of India',
        'method': 'email',
        'email': 'info@dpai.gov.in'
    },
    'NP': {
        'name': 'Ministry of Communication and Information Technology',
        'method': 'email',
        'email': 'info@mocit.gov.np'
    },
    'KW': {
        'name': 'Communication and Information Technology Regulatory Authority',
        'method': 'portal',
        'url': 'https://www.citra.gov.kw/',
        'email': 'info@citra.gov.kw'
    },
    'QA': {
        'name': 'Ministry of Transport and Communications',
        'method': 'email',
        'email': 'info@motc.gov.qa'
    },
    # For future EU/UK expansion
    'EU': {
        'name': 'European Data Protection Board',
        'method': 'one_stop_shop',
        'url': 'https://edpb.europa.eu/',
        'email': 'edpb@edpb.europa.eu'
    },
    'GB': {
        'name': 'Information Commissioner\'s Office',
        'method': 'portal',
        'url': 'https://ico.org.uk/report-a-breach/',
        'email': 'security@ico.org.uk'
    }
}


class DataBreach(db.Model):
    """Model for tracking data breaches and notification status."""
    id = db.Column(db.Integer, primary_key=True)
    detected_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    breach_type = db.Column(db.String(100), nullable=False)
    severity = db.Column(db.String(50), nullable=False)  # low, medium, high, critical
    description = db.Column(db.Text)
    affected_data = db.Column(db.Text)  # JSON string of affected data categories
    affected_users_count = db.Column(db.Integer, default=0)
    is_contained = db.Column(db.Boolean, default=False)
    containment_measures = db.Column(db.Text)
    
    # Authority notification
    requires_authority_notification = db.Column(db.Boolean, default=True)
    authority_notification_approved = db.Column(db.Boolean, default=False)
    authority_notification_sent = db.Column(db.Boolean, default=False)
    authority_notification_time = db.Column(db.DateTime)
    authority_notification_proof = db.Column(db.Text)  # JSON string with notification details
    
    # User notification
    requires_user_notification = db.Column(db.Boolean, default=True)
    user_notification_approved = db.Column(db.Boolean, default=False)
    user_notification_sent = db.Column(db.Boolean, default=False)
    user_notification_time = db.Column(db.DateTime)
    
    # Remediation
    remediation_status = db.Column(db.String(50), default='pending')  # pending, in_progress, completed
    remediation_measures = db.Column(db.Text)
    remediation_completed = db.Column(db.DateTime)
    
    # Relations
    affected_users = relationship('AffectedUser', backref='data_breach', lazy=True)
    
    def __repr__(self):
        return f'<DataBreach {self.id}: {self.breach_type} ({self.severity})>'
    
    def is_notification_due(self):
        """Check if the 72-hour deadline for authority notification is approaching."""
        if self.authority_notification_sent:
            return False
            
        deadline = self.detected_at + datetime.timedelta(hours=72)
        now = datetime.datetime.utcnow()
        
        # Return True if less than 12 hours remaining
        return (deadline - now).total_seconds() < (12 * 3600)
    
    def to_dict(self):
        """Convert breach data to dictionary for templates and API responses."""
        return {
            'id': self.id,
            'detected_at': self.detected_at.isoformat(),
            'breach_type': self.breach_type,
            'severity': self.severity,
            'description': self.description,
            'affected_data': json.loads(self.affected_data) if self.affected_data else {},
            'affected_users_count': self.affected_users_count,
            'is_contained': self.is_contained,
            'containment_measures': self.containment_measures,
            'requires_authority_notification': self.requires_authority_notification,
            'authority_notification_status': 'sent' if self.authority_notification_sent else 
                                            'approved' if self.authority_notification_approved else 'pending',
            'requires_user_notification': self.requires_user_notification,
            'user_notification_status': 'sent' if self.user_notification_sent else 
                                       'approved' if self.user_notification_approved else 'pending',
            'remediation_status': self.remediation_status
        }


class AffectedUser(db.Model):
    """Model for tracking users affected by a data breach."""
    id = db.Column(db.Integer, primary_key=True)
    data_breach_id = db.Column(db.Integer, db.ForeignKey('data_breach.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    affected_data = db.Column(db.Text)  # JSON string of affected data for this user
    notification_sent = db.Column(db.Boolean, default=False)
    notification_time = db.Column(db.DateTime)
    
    # Relations
    user = relationship('User', backref=db.backref('breach_notifications', lazy=True))


def detect_potential_breach(event_type, details, severity='medium'):
    """
    Register a potential data breach event from automated detection.
    
    Args:
        event_type (str): Type of security event (e.g., 'unauthorized_access', 'data_exposure')
        details (dict): Details about the event
        severity (str): Initial severity assessment (low, medium, high, critical)
        
    Returns:
        DataBreach: The created breach record
    """
    logger.info(f"Potential data breach detected: {event_type}")
    
    # Create the breach record
    breach = DataBreach(
        breach_type=event_type,
        severity=severity,
        description=details.get('description', ''),
        affected_data=json.dumps(details.get('affected_data', {})),
        affected_users_count=details.get('affected_users_count', 0)
    )
    
    db.session.add(breach)
    db.session.commit()
    
    # Link affected users if available
    if 'affected_user_ids' in details and details['affected_user_ids']:
        for user_id in details['affected_user_ids']:
            affected_user = AffectedUser(
                data_breach_id=breach.id,
                user_id=user_id,
                affected_data=json.dumps(details.get('user_data', {}).get(str(user_id), {}))
            )
            db.session.add(affected_user)
        
        db.session.commit()
    
    # Send alert to administrators
    alert_administrators(breach)
    
    return breach


def alert_administrators(breach):
    """
    Send immediate alert to administrators about a potential breach.
    
    Args:
        breach (DataBreach): The breach record
    """
    # Email notification to administrators
    admin_email = os.environ.get('ADMIN_EMAIL')
    
    if not admin_email:
        logger.warning("Admin email not configured, can't send breach alert")
        return
    
    try:
        message = MIMEMultipart('alternative')
        message['Subject'] = f"URGENT: Data Breach Alert - {breach.severity.upper()} severity"
        message['From'] = os.environ.get('NOTIFICATION_EMAIL', 'notifications@ieltsaiprep.com')
        message['To'] = admin_email
        
        # Plain text version
        text = f"""
        URGENT: Potential Data Breach Detected
        
        Breach ID: {breach.id}
        Type: {breach.breach_type}
        Severity: {breach.severity.upper()}
        Detected: {breach.detected_at.strftime('%Y-%m-%d %H:%M:%S UTC')}
        Affected Users: {breach.affected_users_count}
        
        Description:
        {breach.description}
        
        Please log in to the admin dashboard immediately to review and take action:
        https://ieltsaiprep.com/admin/breach/{breach.id}
        
        REMINDER: GDPR requires notification to authorities within 72 hours.
        """
        
        # HTML version
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .urgent {{ color: red; font-weight: bold; }}
                .info {{ margin: 20px 0; }}
                .action {{ background-color: #f8f8f8; padding: 15px; margin: 20px 0; }}
                .reminder {{ font-weight: bold; color: #c00; }}
            </style>
        </head>
        <body>
            <h1 class="urgent">URGENT: Potential Data Breach Detected</h1>
            
            <div class="info">
                <p><strong>Breach ID:</strong> {breach.id}</p>
                <p><strong>Type:</strong> {breach.breach_type}</p>
                <p><strong>Severity:</strong> {breach.severity.upper()}</p>
                <p><strong>Detected:</strong> {breach.detected_at.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                <p><strong>Affected Users:</strong> {breach.affected_users_count}</p>
            </div>
            
            <div class="description">
                <h2>Description:</h2>
                <p>{breach.description}</p>
            </div>
            
            <div class="action">
                <h2>Action Required:</h2>
                <p>Please log in to the admin dashboard immediately to review and take action:</p>
                <p><a href="https://ieltsaiprep.com/admin/breach/{breach.id}">Breach Management Dashboard</a></p>
            </div>
            
            <p class="reminder">REMINDER: GDPR requires notification to authorities within 72 hours.</p>
        </body>
        </html>
        """
        
        message.attach(MIMEText(text, 'plain'))
        message.attach(MIMEText(html, 'html'))
        
        # Send email
        smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        smtp_username = os.environ.get('SMTP_USERNAME')
        smtp_password = os.environ.get('SMTP_PASSWORD')
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(message)
        
        logger.info(f"Breach alert sent to administrator: {admin_email}")
        
    except Exception as e:
        logger.error(f"Failed to send breach alert: {str(e)}")


def prepare_authority_notification(breach_id):
    """
    Prepare notification to the relevant data protection authorities.
    
    Args:
        breach_id (int): ID of the breach record
        
    Returns:
        dict: The prepared notification data
    """
    breach = DataBreach.query.get(breach_id)
    if not breach:
        logger.error(f"Breach ID {breach_id} not found")
        return None
    
    # Get all affected countries
    affected_countries = db.session.query(User.country).join(
        AffectedUser, AffectedUser.user_id == User.id
    ).filter(
        AffectedUser.data_breach_id == breach_id
    ).distinct().all()
    
    affected_countries = [c[0] for c in affected_countries if c[0]]
    
    # Prepare notifications for each country
    notifications = {}
    for country_code in affected_countries:
        # Use a default if the country is not in our DPA contacts
        dpa_info = DPA_CONTACTS.get(country_code, DPA_CONTACTS.get('US'))
        
        notification = {
            'dpa': dpa_info['name'],
            'country': country_code,
            'method': dpa_info['method'],
            'contact': dpa_info.get('email') or dpa_info.get('url'),
            'content': generate_authority_notification_content(breach, country_code)
        }
        
        notifications[country_code] = notification
    
    return notifications


def generate_authority_notification_content(breach, country_code):
    """
    Generate the content for authority notification based on country-specific templates.
    
    Args:
        breach (DataBreach): The breach record
        country_code (str): Two-letter country code
        
    Returns:
        dict: The notification content with subject and body
    """
    # Get breach details
    breach_data = breach.to_dict()
    
    # Get country-specific template if exists
    try:
        template_base = f"gdpr/breach_notification_{country_code.lower()}"
        # Try to render the template
        notification_subject = render_template(f"{template_base}_subject.txt", breach=breach_data)
        notification_body = render_template(f"{template_base}_body.txt", breach=breach_data)
    except:
        # Fall back to generic template
        notification_subject = render_template("gdpr/breach_notification_subject.txt", breach=breach_data)
        notification_body = render_template("gdpr/breach_notification_body.txt", breach=breach_data)
    
    return {
        'subject': notification_subject,
        'body': notification_body
    }


def send_authority_notification(breach_id, approved_by_user_id):
    """
    Send approved notifications to the relevant data protection authorities.
    
    Args:
        breach_id (int): ID of the breach record
        approved_by_user_id (int): ID of the admin who approved the notification
        
    Returns:
        dict: Result of the notification attempts
    """
    breach = DataBreach.query.get(breach_id)
    if not breach:
        logger.error(f"Breach ID {breach_id} not found")
        return {'success': False, 'error': 'Breach not found'}
    
    if not breach.authority_notification_approved:
        logger.error(f"Breach ID {breach_id} notification not approved")
        return {'success': False, 'error': 'Notification not approved'}
    
    notifications = prepare_authority_notification(breach_id)
    results = {}
    
    for country_code, notification in notifications.items():
        method = notification['method']
        result = {'success': False, 'details': 'Unknown error'}
        
        try:
            if method == 'email':
                # Send email notification
                result = send_email_notification(
                    notification['contact'],
                    notification['content']['subject'],
                    notification['content']['body']
                )
            elif method == 'portal' or method == 'web_form':
                # For portals, we can't automate the submission but can prepare the data
                result = {
                    'success': True, 
                    'details': f"Prepared for manual submission to {notification['dpa']} portal",
                    'url': notification['contact'],
                    'data': notification['content']
                }
            elif method == 'one_stop_shop':
                # Special handling for EU one-stop-shop
                result = {
                    'success': True,
                    'details': f"Prepared for manual submission via One-Stop-Shop mechanism",
                    'url': notification['contact'],
                    'data': notification['content']
                }
            else:
                result = {'success': False, 'details': f"Unsupported notification method: {method}"}
                
        except Exception as e:
            result = {'success': False, 'details': str(e)}
        
        results[country_code] = result
    
    # Update breach record
    successful_notifications = [k for k, v in results.items() if v['success']]
    
    if successful_notifications:
        breach.authority_notification_sent = True
        breach.authority_notification_time = datetime.datetime.utcnow()
        breach.authority_notification_proof = json.dumps(results)
        db.session.commit()
        
        logger.info(f"Authority notifications sent for breach ID {breach_id}")
    else:
        logger.error(f"All authority notifications failed for breach ID {breach_id}")
    
    return {
        'success': bool(successful_notifications),
        'results': results
    }


def send_email_notification(recipient, subject, body):
    """
    Send an email notification.
    
    Args:
        recipient (str): Email recipient
        subject (str): Email subject
        body (str): Email body text
        
    Returns:
        dict: Result of the email sending attempt
    """
    try:
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = os.environ.get('NOTIFICATION_EMAIL', 'notifications@ieltsaiprep.com')
        message['To'] = recipient
        
        message.attach(MIMEText(body, 'plain'))
        
        # Send email
        smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        smtp_username = os.environ.get('SMTP_USERNAME')
        smtp_password = os.environ.get('SMTP_PASSWORD')
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(message)
        
        return {'success': True, 'details': f"Email sent to {recipient}"}
        
    except Exception as e:
        return {'success': False, 'details': str(e)}


def prepare_user_notifications(breach_id):
    """
    Prepare notifications to affected users.
    
    Args:
        breach_id (int): ID of the breach record
        
    Returns:
        dict: The prepared user notifications
    """
    breach = DataBreach.query.get(breach_id)
    if not breach:
        logger.error(f"Breach ID {breach_id} not found")
        return None
    
    # Only proceed if user notification is required and approved
    if not breach.requires_user_notification or not breach.user_notification_approved:
        return None
    
    # Get all affected users
    affected_users = db.session.query(
        User, AffectedUser
    ).join(
        AffectedUser, AffectedUser.user_id == User.id
    ).filter(
        AffectedUser.data_breach_id == breach_id
    ).all()
    
    # Prepare notifications for each user
    notifications = {}
    for user, affected_user in affected_users:
        # Skip users who have already been notified
        if affected_user.notification_sent:
            continue
            
        notification = {
            'user_id': user.id,
            'email': user.email,
            'name': getattr(user, 'name', user.email),
            'content': generate_user_notification_content(breach, user, affected_user)
        }
        
        notifications[user.id] = notification
    
    return notifications


def generate_user_notification_content(breach, user, affected_user):
    """
    Generate the content for user notification.
    
    Args:
        breach (DataBreach): The breach record
        user (User): The affected user
        affected_user (AffectedUser): The affected user record for this breach
        
    Returns:
        dict: The notification content with subject and body
    """
    # Get breach details
    breach_data = breach.to_dict()
    
    # Add user-specific data
    user_data = {
        'id': user.id,
        'email': user.email,
        'name': getattr(user, 'name', user.email),
        'affected_data': json.loads(affected_user.affected_data) if affected_user.affected_data else {}
    }
    
    # Render templates
    notification_subject = render_template("gdpr/user_breach_notification_subject.txt", 
                                          breach=breach_data, user=user_data)
    notification_body = render_template("gdpr/user_breach_notification_body.txt", 
                                        breach=breach_data, user=user_data)
    
    return {
        'subject': notification_subject,
        'body': notification_body,
        'in_app_message': notification_body  # Could be different if needed
    }


def send_user_notifications(breach_id):
    """
    Send approved notifications to affected users.
    
    Args:
        breach_id (int): ID of the breach record
        
    Returns:
        dict: Result of the notification attempts
    """
    breach = DataBreach.query.get(breach_id)
    if not breach:
        logger.error(f"Breach ID {breach_id} not found")
        return {'success': False, 'error': 'Breach not found'}
    
    if not breach.user_notification_approved:
        logger.error(f"Breach ID {breach_id} user notification not approved")
        return {'success': False, 'error': 'User notification not approved'}
    
    notifications = prepare_user_notifications(breach_id)
    if not notifications:
        return {'success': False, 'error': 'No notifications to send or already sent'}
    
    results = {}
    
    for user_id, notification in notifications.items():
        result = {'success': False, 'details': 'Unknown error'}
        
        try:
            # Send email notification
            email_result = send_email_notification(
                notification['email'],
                notification['content']['subject'],
                notification['content']['body']
            )
            
            # Also send in-app notification if email was successful
            if email_result['success']:
                # Record the notification in the database
                affected_user = AffectedUser.query.filter_by(
                    data_breach_id=breach_id,
                    user_id=user_id
                ).first()
                
                if affected_user:
                    affected_user.notification_sent = True
                    affected_user.notification_time = datetime.datetime.utcnow()
                    db.session.commit()
            
            result = email_result
                
        except Exception as e:
            result = {'success': False, 'details': str(e)}
        
        results[user_id] = result
    
    # Update breach record if at least one notification was successful
    successful_notifications = len([k for k, v in results.items() if v['success']])
    
    if successful_notifications > 0:
        breach.user_notification_sent = True
        breach.user_notification_time = datetime.datetime.utcnow()
        db.session.commit()
        
        logger.info(f"User notifications sent for breach ID {breach_id}: {successful_notifications} successful")
    else:
        logger.error(f"All user notifications failed for breach ID {breach_id}")
    
    return {
        'success': successful_notifications > 0,
        'count': successful_notifications,
        'results': results
    }


def approve_authority_notification(breach_id, admin_id):
    """
    Approve a breach for notification to authorities.
    
    Args:
        breach_id (int): ID of the breach record
        admin_id (int): ID of the admin approving the notification
        
    Returns:
        bool: Success of the approval
    """
    breach = DataBreach.query.get(breach_id)
    if not breach:
        return False
    
    breach.authority_notification_approved = True
    db.session.commit()
    
    return True


def approve_user_notification(breach_id, admin_id):
    """
    Approve a breach for notification to affected users.
    
    Args:
        breach_id (int): ID of the breach record
        admin_id (int): ID of the admin approving the notification
        
    Returns:
        bool: Success of the approval
    """
    breach = DataBreach.query.get(breach_id)
    if not breach:
        return False
    
    breach.user_notification_approved = True
    db.session.commit()
    
    return True


def get_breach_status(breach_id):
    """
    Get comprehensive status of a breach and its notifications.
    
    Args:
        breach_id (int): ID of the breach record
        
    Returns:
        dict: Status information about the breach
    """
    breach = DataBreach.query.get(breach_id)
    if not breach:
        return None
    
    # Get breach details
    breach_data = breach.to_dict()
    
    # Add notification preparation status
    authority_notifications = None
    if breach.authority_notification_approved and not breach.authority_notification_sent:
        authority_notifications = prepare_authority_notification(breach_id)
    
    user_notifications = None
    if breach.user_notification_approved and not breach.user_notification_sent:
        user_notifications = prepare_user_notifications(breach_id)
    
    # Calculate time remaining for 72-hour deadline
    deadline = breach.detected_at + datetime.timedelta(hours=72)
    now = datetime.datetime.utcnow()
    hours_remaining = max(0, (deadline - now).total_seconds() / 3600)
    
    status = {
        'breach': breach_data,
        'deadline': {
            'timestamp': deadline.isoformat(),
            'hours_remaining': round(hours_remaining, 1),
            'is_critical': hours_remaining < 12
        },
        'authority_notifications': authority_notifications,
        'user_notifications': user_notifications,
        'affected_users_count': db.session.query(AffectedUser).filter_by(data_breach_id=breach_id).count()
    }
    
    return status


def monitor_for_suspicious_activity():
    """
    Run monitoring checks for suspicious database activity.
    Should be scheduled to run regularly (e.g., every 15 minutes).
    
    Returns:
        list: Any breach events that were detected
    """
    detected_breaches = []
    
    # Check for unusual database access patterns
    # This would need to be customized for your specific application
    # Example: Unusual number of queries from a single IP, excessive data retrieval, etc.
    
    # Placeholder for demonstration
    if False:  # Replace with actual detection logic
        breach = detect_potential_breach(
            'unusual_database_access',
            {
                'description': 'Unusual pattern of database access detected from unknown IP',
                'affected_data': {'tables': ['users', 'test_results']},
                'affected_users_count': 15,
                'affected_user_ids': [1, 2, 3]  # Example user IDs
            },
            severity='high'
        )
        detected_breaches.append(breach.id)
    
    # Check for unauthorized API usage
    # Example: API calls with invalid tokens, excessive failed auth attempts
    
    # Check for unusual file access patterns
    # Example: Mass downloads of user data or audio files
    
    return detected_breaches


def check_notification_deadlines():
    """
    Check for breaches approaching the 72-hour notification deadline.
    Should be scheduled to run regularly (e.g., every hour).
    
    Returns:
        list: Breach IDs that need urgent attention
    """
    now = datetime.datetime.utcnow()
    deadline_threshold = now + datetime.timedelta(hours=12)  # Alert if less than 12 hours remaining
    
    # Find breaches that require notification and are approaching the deadline
    urgent_breaches = DataBreach.query.filter(
        DataBreach.detected_at + datetime.timedelta(hours=72) <= deadline_threshold,
        DataBreach.requires_authority_notification == True,
        DataBreach.authority_notification_sent == False
    ).all()
    
    # Send urgent reminders for each
    for breach in urgent_breaches:
        hours_remaining = (breach.detected_at + datetime.timedelta(hours=72) - now).total_seconds() / 3600
        
        logger.warning(f"URGENT: Breach ID {breach.id} has {hours_remaining:.1f} hours remaining for notification")
        
        # Send urgent email to administrators
        admin_email = os.environ.get('ADMIN_EMAIL')
        if admin_email:
            try:
                message = MIMEMultipart('alternative')
                message['Subject'] = f"URGENT: {hours_remaining:.1f} hours remaining for breach notification"
                message['From'] = os.environ.get('NOTIFICATION_EMAIL', 'notifications@ieltsaiprep.com')
                message['To'] = admin_email
                
                text = f"""
                URGENT GDPR COMPLIANCE ALERT
                
                Breach ID {breach.id} has only {hours_remaining:.1f} hours remaining for mandatory authority notification.
                
                Breach Type: {breach.breach_type}
                Severity: {breach.severity}
                Detected: {breach.detected_at.strftime('%Y-%m-%d %H:%M:%S UTC')}
                
                Please take immediate action to approve and submit the authority notification:
                https://ieltsaiprep.com/admin/breach/{breach.id}
                
                FAILURE TO NOTIFY WITHIN 72 HOURS MAY RESULT IN REGULATORY PENALTIES.
                """
                
                message.attach(MIMEText(text, 'plain'))
                
                # Send email
                smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
                smtp_port = int(os.environ.get('SMTP_PORT', '587'))
                smtp_username = os.environ.get('SMTP_USERNAME')
                smtp_password = os.environ.get('SMTP_PASSWORD')
                
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()
                    server.login(smtp_username, smtp_password)
                    server.send_message(message)
                
            except Exception as e:
                logger.error(f"Failed to send urgent deadline reminder: {str(e)}")
    
    return [breach.id for breach in urgent_breaches]