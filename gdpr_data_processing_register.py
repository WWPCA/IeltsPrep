"""
GDPR Data Processing Register

This module implements a complete Record of Processing Activities (ROPA) as required by GDPR Article 30.
It tracks all data processing activities performed by the application and stores them securely.
"""

import json
import logging
import os
from datetime import datetime

from app import db
from flask import current_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure the GDPR logs directory exists
if not os.path.exists('gdpr_logs'):
    os.makedirs('gdpr_logs')

class DataProcessingRecord(db.Model):
    """
    Model for tracking data processing activities as required by GDPR Article 30.
    Acts as a Record of Processing Activities (ROPA).
    """
    id = db.Column(db.Integer, primary_key=True)
    
    # Processing activity details
    activity_name = db.Column(db.String(255), nullable=False)
    processing_purpose = db.Column(db.Text, nullable=False)
    data_category = db.Column(db.String(255), nullable=False)
    data_subject_category = db.Column(db.String(255), nullable=False)
    processing_description = db.Column(db.Text, nullable=False)
    
    # Controller/Processor details
    data_controller = db.Column(db.String(255), nullable=False)
    data_processor = db.Column(db.String(255), nullable=True)
    dpo_contact = db.Column(db.String(255), nullable=True)
    
    # Legal basis and consent
    legal_basis = db.Column(db.String(255), nullable=False)
    consent_required = db.Column(db.Boolean, default=True)
    
    # Data storage and transfers
    storage_location = db.Column(db.String(255), nullable=False)
    storage_duration = db.Column(db.String(255), nullable=False)
    international_transfer = db.Column(db.Boolean, default=False)
    transfer_safeguards = db.Column(db.Text, nullable=True)
    
    # Technical and organizational measures
    security_measures = db.Column(db.Text, nullable=False)
    access_controls = db.Column(db.Text, nullable=False)
    
    # Record maintenance
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<DataProcessingRecord {self.activity_name}>'
    
    def to_dict(self):
        """Convert record to dictionary for export"""
        return {
            'activity_name': self.activity_name,
            'processing_purpose': self.processing_purpose,
            'data_category': self.data_category,
            'data_subject_category': self.data_subject_category,
            'processing_description': self.processing_description,
            'data_controller': self.data_controller,
            'data_processor': self.data_processor,
            'dpo_contact': self.dpo_contact,
            'legal_basis': self.legal_basis,
            'consent_required': self.consent_required,
            'storage_location': self.storage_location,
            'storage_duration': self.storage_duration,
            'international_transfer': self.international_transfer,
            'transfer_safeguards': self.transfer_safeguards,
            'security_measures': self.security_measures,
            'access_controls': self.access_controls,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

def initialize_processing_records():
    """
    Initialize the standard data processing records for the application.
    This function sets up all the data processing activities tracked by the system.
    """
    try:
        # Check if records already exist
        if DataProcessingRecord.query.count() > 0:
            logger.info("Data processing records already initialized.")
            return
        
        # Define controller details
        controller_name = "AI Learning Hub"
        dpo_contact = "privacy@ailearninghub.com"  # Example email
        
        # Define standard security measures (used for all records)
        standard_security_measures = (
            "1. HTTPS encryption for all data in transit\n"
            "2. Database encryption for sensitive data at rest\n"
            "3. Regular security audits and penetration testing\n"
            "4. Multi-factor authentication for admin access\n"
            "5. Automated vulnerability scanning\n"
            "6. Daily data backups with strong encryption\n"
            "7. Password policy enforcement (complexity, rotation)\n"
            "8. Intrusion detection and prevention systems"
        )
        
        # Define standard access controls (used for all records)
        standard_access_controls = (
            "1. Role-based access control (RBAC)\n"
            "2. Principle of least privilege applied\n"
            "3. Regular access rights review\n"
            "4. Account activity logging and monitoring\n"
            "5. Automatic session timeout\n"
            "6. IP-based access restrictions for sensitive operations\n"
            "7. Employee access revocation process"
        )
        
        # 1. User Registration & Account Management
        registration_record = DataProcessingRecord(
            activity_name="User Registration & Account Management",
            processing_purpose="To create and manage user accounts, authenticate users, and provide personalized experiences",
            data_category="Personal data (email, name), authentication data (password hashes, login history)",
            data_subject_category="IELTS test candidates",
            processing_description="Collection, storage, and use of user account information for registration, login, and account management",
            data_controller=controller_name,
            dpo_contact=dpo_contact,
            legal_basis="Contract (Terms of Service), Consent",
            consent_required=True,
            storage_location="PostgreSQL database, secure cloud storage",
            storage_duration="For duration of account plus 30 days after deletion request",
            security_measures=standard_security_measures,
            access_controls=standard_access_controls
        )
        
        # 2. Assessment Data Processing
        assessment_record = DataProcessingRecord(
            activity_name="IELTS Assessment Data Processing",
            processing_purpose="To assess user performance on IELTS practice tests and provide detailed feedback",
            data_category="Assessment responses, scores, proficiency metrics, improvement tracking",
            data_subject_category="IELTS test candidates",
            processing_description="Collection and analysis of test responses to generate scores and personalized feedback",
            data_controller=controller_name,
            data_processor="GenAI Assessment Services (TrueScore® and Elaris®)",
            dpo_contact=dpo_contact,
            legal_basis="Contract (Terms of Service), Legitimate Interest, Consent",
            consent_required=True,
            storage_location="PostgreSQL database, cloud storage (GCP)",
            storage_duration="Indefinitely while account is active, removable upon request",
            security_measures=standard_security_measures,
            access_controls=standard_access_controls
        )
        
        # 3. Speaking Test Audio Processing
        speaking_record = DataProcessingRecord(
            activity_name="Speaking Test Audio Processing",
            processing_purpose="To assess spoken English ability and provide IELTS band scores and feedback",
            data_category="Audio recordings, transcripts, speaking assessment metrics",
            data_subject_category="IELTS test candidates",
            processing_description="Temporary processing of audio recordings to generate transcripts and AI assessments",
            data_controller=controller_name,
            data_processor="Cloud Speech Services (AWS, GCP, AssemblyAI)",
            dpo_contact=dpo_contact,
            legal_basis="Explicit Consent",
            consent_required=True,
            storage_location="Temporary cloud storage (GCP)",
            storage_duration="Audio is processed immediately and not stored; transcripts deleted after 6 months",
            international_transfer=True,
            transfer_safeguards="Standard Contractual Clauses with service providers",
            security_measures=standard_security_measures + "\n9. Audio data transmitted via encrypted channels\n10. Automated deletion workflow for audio data",
            access_controls=standard_access_controls
        )
        
        # 4. Payment Processing
        payment_record = DataProcessingRecord(
            activity_name="Payment Processing",
            processing_purpose="To process payments for premium access and assessment packages",
            data_category="Payment details, transaction history, billing information",
            data_subject_category="Paying customers",
            processing_description="Collection and processing of payment information to complete transactions",
            data_controller=controller_name,
            data_processor="Stripe Payment Processing",
            dpo_contact=dpo_contact,
            legal_basis="Contract (Payment Agreement), Legal Obligation",
            consent_required=True,
            storage_location="Stripe secure servers, transaction records in PostgreSQL database",
            storage_duration="Payment provider retains data per their policy; local transaction records kept for 7 years for legal compliance",
            international_transfer=True,
            transfer_safeguards="Standard Contractual Clauses with payment processor",
            security_measures=standard_security_measures + "\n9. PCI DSS compliance\n10. No storage of full payment details on our servers",
            access_controls=standard_access_controls + "\n8. Special elevated permissions required for financial data access"
        )
        
        # 5. Marketing Communications
        marketing_record = DataProcessingRecord(
            activity_name="Marketing Communications",
            processing_purpose="To send promotional messages, updates, and educational content",
            data_category="Email address, name, communication preferences, engagement metrics",
            data_subject_category="Opted-in users",
            processing_description="Sending of emails, notifications, and other communications for marketing purposes",
            data_controller=controller_name,
            data_processor="Email Service Provider (SendGrid)",
            dpo_contact=dpo_contact,
            legal_basis="Consent",
            consent_required=True,
            storage_location="Email service provider, PostgreSQL database",
            storage_duration="Until consent withdrawn",
            security_measures=standard_security_measures,
            access_controls=standard_access_controls
        )
        
        # 6. Website Analytics
        analytics_record = DataProcessingRecord(
            activity_name="Website Analytics",
            processing_purpose="To understand user behavior and improve the platform",
            data_category="Usage data, engagement metrics, navigation patterns (pseudonymized)",
            data_subject_category="Website visitors",
            processing_description="Collection and analysis of user interaction data to improve website performance and user experience",
            data_controller=controller_name,
            data_processor="Analytics Provider",
            dpo_contact=dpo_contact,
            legal_basis="Legitimate Interest, Consent for cookies",
            consent_required=True,
            storage_location="Analytics provider, aggregated metrics in PostgreSQL database",
            storage_duration="26 months in raw form, aggregated data kept indefinitely",
            international_transfer=True,
            transfer_safeguards="Standard Contractual Clauses with analytics provider",
            security_measures=standard_security_measures + "\n9. Data pseudonymization\n10. IP address masking",
            access_controls=standard_access_controls
        )
        
        # Add all records to the database
        db.session.add(registration_record)
        db.session.add(assessment_record)
        db.session.add(speaking_record)
        db.session.add(payment_record)
        db.session.add(marketing_record)
        db.session.add(analytics_record)
        
        db.session.commit()
        
        # Log all processing activities to file as well
        export_processing_records_to_file()
        
        logger.info("Successfully initialized data processing records")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error initializing data processing records: {str(e)}")
        raise

def export_processing_records_to_file():
    """Export all processing records to a JSON file for audit purposes"""
    try:
        records = DataProcessingRecord.query.all()
        records_data = [record.to_dict() for record in records]
        
        # Create timestamp for filename
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f'gdpr_logs/processing_register_{timestamp}.json'
        
        with open(filename, 'w') as f:
            json.dump(records_data, f, indent=2)
        
        logger.info(f"Exported processing records to {filename}")
        return filename
    
    except Exception as e:
        logger.error(f"Error exporting processing records: {str(e)}")
        raise

def get_processing_activity_by_name(name):
    """
    Retrieve a processing activity record by name.
    
    Args:
        name (str): The name of the processing activity
        
    Returns:
        DataProcessingRecord: The processing record if found, None otherwise
    """
    return DataProcessingRecord.query.filter_by(activity_name=name).first()

def update_processing_activity(activity_name, **kwargs):
    """
    Update an existing processing activity record.
    
    Args:
        activity_name (str): Name of the activity to update
        **kwargs: Field=value pairs to update
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        record = get_processing_activity_by_name(activity_name)
        
        if not record:
            logger.error(f"Processing activity '{activity_name}' not found")
            return False
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(record, key):
                setattr(record, key, value)
            else:
                logger.warning(f"Field '{key}' does not exist on DataProcessingRecord")
        
        # Update timestamp
        record.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Log the update to file
        export_processing_records_to_file()
        
        logger.info(f"Successfully updated processing activity '{activity_name}'")
        return True
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating processing activity: {str(e)}")
        return False

if __name__ == "__main__":
    # When run directly, this will initialize the processing records
    from app import app
    with app.app_context():
        initialize_processing_records()