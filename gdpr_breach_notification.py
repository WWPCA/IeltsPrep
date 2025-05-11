"""
GDPR Data Breach Notification System

This module implements a data breach notification system as required by GDPR Article 33 and 34.
It provides functionality to log data breaches, notify affected users, and report to authorities.
"""

import csv
import json
import logging
import os
from datetime import datetime

from app import db
from flask import current_app, render_template, url_for
from sqlalchemy.dialects.postgresql import JSONB

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure the GDPR logs directory exists
if not os.path.exists('gdpr_logs/breaches'):
    os.makedirs('gdpr_logs/breaches', exist_ok=True)


class DataBreach(db.Model):
    """
    Model for tracking data breaches and notification status.
    Implements GDPR Article 33 (notification to authority) and 34 (notification to data subject).
    """
    id = db.Column(db.Integer, primary_key=True)
    
    # Breach details
    breach_date = db.Column(db.DateTime, nullable=False)
    discovery_date = db.Column(db.DateTime, nullable=False)
    breach_type = db.Column(db.String(100), nullable=False)  # unauthorized access, loss, etc.
    breach_description = db.Column(db.Text, nullable=False)
    affected_data = db.Column(db.Text, nullable=False)  # what data was compromised
    affected_users_count = db.Column(db.Integer, nullable=False)
    
    # Risk assessment
    risk_level = db.Column(db.String(50), nullable=False)  # low, medium, high, very high
    potential_consequences = db.Column(db.Text, nullable=False)
    
    # Containment and recovery
    containment_measures = db.Column(db.Text, nullable=True)
    recovery_actions = db.Column(db.Text, nullable=True)
    
    # Authority notification (Article 33)
    authority_notification_required = db.Column(db.Boolean, default=True)
    authority_notified = db.Column(db.Boolean, default=False)
    authority_notification_date = db.Column(db.DateTime, nullable=True)
    authority_reference = db.Column(db.String(100), nullable=True)
    
    # Data subject notification (Article 34)
    user_notification_required = db.Column(db.Boolean, default=True)
    user_notification_date = db.Column(db.DateTime, nullable=True)
    notification_method = db.Column(db.String(100), nullable=True)  # email, in-app, etc.
    notification_message = db.Column(db.Text, nullable=True)
    
    # Affected users (can be stored as JSON or in a separate table)
    affected_user_ids = db.Column(db.Text, nullable=True)  # CSV of user IDs or JSON
    
    # Record maintenance
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    reported_by = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), default="Open")  # Open, Contained, Resolved
    
    def __repr__(self):
        return f'<DataBreach #{self.id} [{self.breach_type}] {self.status}>'
    
    def to_dict(self):
        """Convert breach record to dictionary for export"""
        return {
            'id': self.id,
            'breach_date': self.breach_date.isoformat() if self.breach_date else None,
            'discovery_date': self.discovery_date.isoformat() if self.discovery_date else None,
            'breach_type': self.breach_type,
            'breach_description': self.breach_description,
            'affected_data': self.affected_data,
            'affected_users_count': self.affected_users_count,
            'risk_level': self.risk_level,
            'potential_consequences': self.potential_consequences,
            'containment_measures': self.containment_measures,
            'recovery_actions': self.recovery_actions,
            'authority_notification_required': self.authority_notification_required,
            'authority_notified': self.authority_notified,
            'authority_notification_date': self.authority_notification_date.isoformat() if self.authority_notification_date else None,
            'authority_reference': self.authority_reference,
            'user_notification_required': self.user_notification_required,
            'user_notification_date': self.user_notification_date.isoformat() if self.user_notification_date else None,
            'notification_method': self.notification_method,
            'notification_message': self.notification_message,
            'status': self.status,
            'reported_by': self.reported_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


def log_data_breach(
    breach_date,
    discovery_date,
    breach_type,
    breach_description,
    affected_data,
    affected_users_count,
    risk_level,
    potential_consequences,
    reported_by,
    authority_notification_required=True,
    user_notification_required=True,
    affected_user_ids=None,
    containment_measures=None,
    recovery_actions=None
):
    """
    Create a new data breach record.
    
    Args:
        breach_date (datetime): Date and time when the breach occurred
        discovery_date (datetime): Date and time when the breach was discovered
        breach_type (str): Type of breach (unauthorized access, loss, etc.)
        breach_description (str): Detailed description of the breach
        affected_data (str): What data was compromised
        affected_users_count (int): Number of affected users
        risk_level (str): Risk level assessment (low, medium, high, very high)
        potential_consequences (str): Potential impact on affected users
        reported_by (str): Person who reported the breach
        authority_notification_required (bool): Whether notification to authorities is required
        user_notification_required (bool): Whether notification to users is required
        affected_user_ids (list): List of affected user IDs
        containment_measures (str): Measures taken to contain the breach
        recovery_actions (str): Actions taken to recover from the breach
        
    Returns:
        DataBreach: The created breach record
    """
    try:
        # Convert affected_user_ids list to JSON or CSV string
        if affected_user_ids:
            if isinstance(affected_user_ids, list):
                affected_user_ids = ','.join(map(str, affected_user_ids))
            elif not isinstance(affected_user_ids, str):
                affected_user_ids = str(affected_user_ids)
        
        # Create new breach record
        breach = DataBreach(
            breach_date=breach_date,
            discovery_date=discovery_date,
            breach_type=breach_type,
            breach_description=breach_description,
            affected_data=affected_data,
            affected_users_count=affected_users_count,
            risk_level=risk_level,
            potential_consequences=potential_consequences,
            reported_by=reported_by,
            authority_notification_required=authority_notification_required,
            user_notification_required=user_notification_required,
            affected_user_ids=affected_user_ids,
            containment_measures=containment_measures,
            recovery_actions=recovery_actions,
            status="Open"
        )
        
        db.session.add(breach)
        db.session.commit()
        
        # Log breach to file
        log_breach_to_file(breach)
        
        logger.info(f"Data breach #{breach.id} logged successfully")
        
        return breach
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error logging data breach: {str(e)}")
        raise


def update_breach_status(breach_id, status, containment_measures=None, recovery_actions=None):
    """
    Update the status of a data breach.
    
    Args:
        breach_id (int): ID of the breach to update
        status (str): New status (Open, Contained, Resolved)
        containment_measures (str): Measures taken to contain the breach
        recovery_actions (str): Actions taken to recover from the breach
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        breach = DataBreach.query.get(breach_id)
        
        if not breach:
            logger.error(f"Data breach #{breach_id} not found")
            return False
        
        breach.status = status
        
        if containment_measures:
            breach.containment_measures = containment_measures
        
        if recovery_actions:
            breach.recovery_actions = recovery_actions
        
        breach.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Log update to file
        log_breach_to_file(breach, update=True)
        
        logger.info(f"Data breach #{breach_id} status updated to {status}")
        
        return True
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating data breach status: {str(e)}")
        return False


def record_authority_notification(breach_id, notification_date, authority_reference):
    """
    Record notification to data protection authority.
    
    Args:
        breach_id (int): ID of the breach
        notification_date (datetime): Date of notification
        authority_reference (str): Reference number or ID from the authority
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        breach = DataBreach.query.get(breach_id)
        
        if not breach:
            logger.error(f"Data breach #{breach_id} not found")
            return False
        
        breach.authority_notified = True
        breach.authority_notification_date = notification_date
        breach.authority_reference = authority_reference
        breach.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Log update to file
        log_breach_to_file(breach, update=True)
        
        logger.info(f"Authority notification recorded for data breach #{breach_id}")
        
        return True
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error recording authority notification: {str(e)}")
        return False


def prepare_user_notification(breach_id, notification_message, notification_method="email"):
    """
    Prepare notification to affected users.
    
    Args:
        breach_id (int): ID of the breach
        notification_message (str): Message to send to affected users
        notification_method (str): Method of notification (email, in-app, etc.)
        
    Returns:
        dict: Dictionary with notification details if successful, None otherwise
    """
    try:
        breach = DataBreach.query.get(breach_id)
        
        if not breach:
            logger.error(f"Data breach #{breach_id} not found")
            return None
        
        breach.notification_message = notification_message
        breach.notification_method = notification_method
        breach.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Get affected user IDs
        affected_user_ids = []
        if breach.affected_user_ids:
            affected_user_ids = breach.affected_user_ids.split(',')
        
        # Prepare notification details
        notification = {
            'breach_id': breach.id,
            'affected_user_ids': affected_user_ids,
            'message': notification_message,
            'method': notification_method,
            'breach_date': breach.breach_date,
            'affected_data': breach.affected_data,
            'risk_level': breach.risk_level,
            'potential_consequences': breach.potential_consequences,
            'containment_measures': breach.containment_measures,
            'recovery_actions': breach.recovery_actions
        }
        
        # Log update to file
        log_breach_to_file(breach, update=True)
        
        logger.info(f"User notification prepared for data breach #{breach_id}")
        
        return notification
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error preparing user notification: {str(e)}")
        return None


def record_user_notification(breach_id, notification_date):
    """
    Record that users have been notified.
    
    Args:
        breach_id (int): ID of the breach
        notification_date (datetime): Date of notification
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        breach = DataBreach.query.get(breach_id)
        
        if not breach:
            logger.error(f"Data breach #{breach_id} not found")
            return False
        
        breach.user_notification_date = notification_date
        breach.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Log update to file
        log_breach_to_file(breach, update=True)
        
        logger.info(f"User notification recorded for data breach #{breach_id}")
        
        return True
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error recording user notification: {str(e)}")
        return False


def log_breach_to_file(breach, update=False):
    """
    Log breach details to a file for audit purposes.
    
    Args:
        breach (DataBreach): The breach record to log
        update (bool): Whether this is an update to an existing record
    """
    try:
        action = "UPDATE" if update else "CREATE"
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f'gdpr_logs/breaches/breach_{breach.id}_{action}_{timestamp}.json'
        
        with open(filename, 'w') as f:
            json.dump(breach.to_dict(), f, indent=2)
        
        logger.info(f"Logged breach details to {filename}")
    
    except Exception as e:
        logger.error(f"Error logging breach to file: {str(e)}")


def generate_breach_report(breach_id):
    """
    Generate a detailed report for a specific breach.
    
    Args:
        breach_id (int): ID of the breach
        
    Returns:
        dict: Report data if successful, None otherwise
    """
    try:
        breach = DataBreach.query.get(breach_id)
        
        if not breach:
            logger.error(f"Data breach #{breach_id} not found")
            return None
        
        report_data = breach.to_dict()
        
        # Add timeline information
        report_data['timeline'] = [
            {
                'event': 'Breach Occurred',
                'date': breach.breach_date.isoformat() if breach.breach_date else None
            },
            {
                'event': 'Breach Discovered',
                'date': breach.discovery_date.isoformat() if breach.discovery_date else None
            }
        ]
        
        if breach.authority_notification_date:
            report_data['timeline'].append({
                'event': 'Authority Notified',
                'date': breach.authority_notification_date.isoformat()
            })
        
        if breach.user_notification_date:
            report_data['timeline'].append({
                'event': 'Users Notified',
                'date': breach.user_notification_date.isoformat()
            })
        
        # Calculate time metrics
        if breach.breach_date and breach.discovery_date:
            time_to_discovery = (breach.discovery_date - breach.breach_date).total_seconds() / 3600  # hours
            report_data['time_to_discovery_hours'] = round(time_to_discovery, 2)
        
        if breach.discovery_date and breach.authority_notification_date:
            time_to_authority_notification = (breach.authority_notification_date - breach.discovery_date).total_seconds() / 3600  # hours
            report_data['time_to_authority_notification_hours'] = round(time_to_authority_notification, 2)
        
        if breach.discovery_date and breach.user_notification_date:
            time_to_user_notification = (breach.user_notification_date - breach.discovery_date).total_seconds() / 3600  # hours
            report_data['time_to_user_notification_hours'] = round(time_to_user_notification, 2)
        
        # Export report to file
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f'gdpr_logs/breaches/breach_{breach.id}_REPORT_{timestamp}.json'
        
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        logger.info(f"Generated breach report: {filename}")
        
        return report_data
    
    except Exception as e:
        logger.error(f"Error generating breach report: {str(e)}")
        return None


def get_breach_notification_template(breach_id):
    """
    Get the template for user breach notification.
    
    Args:
        breach_id (int): ID of the breach
        
    Returns:
        str: HTML notification template if successful, None otherwise
    """
    try:
        breach = DataBreach.query.get(breach_id)
        
        if not breach:
            logger.error(f"Data breach #{breach_id} not found")
            return None
        
        # Render notification template
        template = render_template(
            'gdpr/breach_notification_email.html',
            breach=breach,
            breach_date=breach.breach_date.strftime('%B %d, %Y'),
            discovery_date=breach.discovery_date.strftime('%B %d, %Y'),
            support_email='support@ailearninghub.com',  # Update with your support email
            privacy_url=url_for('gdpr.privacy_policy', _external=True),
            help_url=url_for('contact', _external=True)
        )
        
        return template
    
    except Exception as e:
        logger.error(f"Error getting breach notification template: {str(e)}")
        return None


def export_all_breaches():
    """
    Export all breach records to a CSV file.
    
    Returns:
        str: Path to the exported file if successful, None otherwise
    """
    try:
        breaches = DataBreach.query.all()
        
        if not breaches:
            logger.info("No breach records found to export")
            return None
        
        # Create timestamp for filename
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f'gdpr_logs/breaches/all_breaches_{timestamp}.csv'
        
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = [
                'id', 'breach_date', 'discovery_date', 'breach_type',
                'affected_data', 'affected_users_count', 'risk_level',
                'authority_notified', 'authority_notification_date',
                'user_notification_date', 'status', 'reported_by'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for breach in breaches:
                writer.writerow({
                    'id': breach.id,
                    'breach_date': breach.breach_date.strftime('%Y-%m-%d %H:%M:%S') if breach.breach_date else '',
                    'discovery_date': breach.discovery_date.strftime('%Y-%m-%d %H:%M:%S') if breach.discovery_date else '',
                    'breach_type': breach.breach_type,
                    'affected_data': breach.affected_data,
                    'affected_users_count': breach.affected_users_count,
                    'risk_level': breach.risk_level,
                    'authority_notified': 'Yes' if breach.authority_notified else 'No',
                    'authority_notification_date': breach.authority_notification_date.strftime('%Y-%m-%d %H:%M:%S') if breach.authority_notification_date else '',
                    'user_notification_date': breach.user_notification_date.strftime('%Y-%m-%d %H:%M:%S') if breach.user_notification_date else '',
                    'status': breach.status,
                    'reported_by': breach.reported_by
                })
        
        logger.info(f"Exported all breach records to {filename}")
        return filename
    
    except Exception as e:
        logger.error(f"Error exporting breach records: {str(e)}")
        return None