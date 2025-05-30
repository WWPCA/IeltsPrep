"""
Database Validation Events
Implements SQLAlchemy event listeners for enhanced validation based on technical analysis.
"""

import re
import json
from datetime import datetime
from sqlalchemy import event
from models import User, Assessment, UserAssessmentAssignment, AssessmentAssignment, WritingResponse, AssessmentSpeakingResponse

def validate_email_format(email):
    """Validate email format using regex"""
    if not email:
        return False
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email) is not None

def validate_json_field(value, field_name):
    """Validate JSON field data"""
    if value is None:
        return True
    try:
        if isinstance(value, str):
            json.loads(value)
        elif not isinstance(value, (dict, list)):
            raise ValueError(f"{field_name} must be valid JSON")
        return True
    except (json.JSONDecodeError, ValueError):
        return False

# User model validation events
@event.listens_for(User.email, 'set')
def validate_user_email(target, value, oldvalue, initiator):
    """Validate email format for User model"""
    if value and not validate_email_format(value):
        raise ValueError("Invalid email format")

@event.listens_for(User.region, 'set')
def validate_user_region(target, value, oldvalue, initiator):
    """Validate region field length"""
    if value and len(value) > 50:
        raise ValueError("Region exceeds maximum length of 50 characters")

@event.listens_for(User._assessment_history, 'set')
def validate_assessment_history(target, value, oldvalue, initiator):
    """Validate assessment history JSON format"""
    if not validate_json_field(value, "assessment_history"):
        raise ValueError("Assessment history must be valid JSON")

@event.listens_for(User._activity_history, 'set')
def validate_activity_history(target, value, oldvalue, initiator):
    """Validate activity history JSON format"""
    if not validate_json_field(value, "activity_history"):
        raise ValueError("Activity history must be valid JSON")

@event.listens_for(User._speaking_scores, 'set')
def validate_speaking_scores(target, value, oldvalue, initiator):
    """Validate speaking scores JSON format"""
    if not validate_json_field(value, "speaking_scores"):
        raise ValueError("Speaking scores must be valid JSON")

@event.listens_for(User._completed_assessments, 'set')
def validate_completed_assessments(target, value, oldvalue, initiator):
    """Validate completed assessments JSON format"""
    if not validate_json_field(value, "completed_assessments"):
        raise ValueError("Completed assessments must be valid JSON")

# Assessment model validation events
@event.listens_for(Assessment.assessment_type, 'set')
def validate_assessment_type(target, value, oldvalue, initiator):
    """Validate assessment type values"""
    valid_types = [
        'academic_writing', 'academic_speaking', 
        'general_writing', 'general_speaking'
    ]
    if value and value not in valid_types:
        raise ValueError(f"Assessment type must be one of: {', '.join(valid_types)}")

@event.listens_for(Assessment.status, 'set')
def validate_assessment_status(target, value, oldvalue, initiator):
    """Validate assessment status values"""
    valid_statuses = ['active', 'inactive', 'draft', 'archived']
    if value and value not in valid_statuses:
        raise ValueError(f"Assessment status must be one of: {', '.join(valid_statuses)}")

@event.listens_for(Assessment._criteria, 'set')
def validate_assessment_criteria(target, value, oldvalue, initiator):
    """Validate assessment criteria JSON format"""
    if not validate_json_field(value, "criteria"):
        raise ValueError("Assessment criteria must be valid JSON")

@event.listens_for(Assessment._questions, 'set')
def validate_assessment_questions(target, value, oldvalue, initiator):
    """Validate assessment questions JSON format"""
    if not validate_json_field(value, "questions"):
        raise ValueError("Assessment questions must be valid JSON")

# UserAssessmentAssignment validation events
@event.listens_for(UserAssessmentAssignment.assessment_type, 'set')
def validate_assignment_type(target, value, oldvalue, initiator):
    """Validate assignment type values"""
    valid_types = ['academic', 'general']
    if value and value not in valid_types:
        raise ValueError(f"Assignment type must be one of: {', '.join(valid_types)}")

@event.listens_for(UserAssessmentAssignment.expiry_date, 'set')
def validate_assignment_expiry_date(target, value, oldvalue, initiator):
    """Validate expiry date is in the future"""
    if value and value <= datetime.utcnow():
        raise ValueError("Expiry date must be in the future")

@event.listens_for(UserAssessmentAssignment.assigned_assessment_ids, 'set')
def validate_assigned_assessment_ids(target, value, oldvalue, initiator):
    """Validate assigned assessment IDs JSON format"""
    if not validate_json_field(value, "assigned_assessment_ids"):
        raise ValueError("Assigned assessment IDs must be valid JSON")
    
    # Additional validation to ensure it's a list
    if value:
        try:
            data = json.loads(value) if isinstance(value, str) else value
            if not isinstance(data, list):
                raise ValueError("Assigned assessment IDs must be a list")
        except (json.JSONDecodeError, TypeError):
            raise ValueError("Assigned assessment IDs must be valid JSON list")

# WritingResponse validation events
@event.listens_for(WritingResponse.task_number, 'set')
def validate_writing_task_number(target, value, oldvalue, initiator):
    """Validate writing task number"""
    if value is not None and value not in [1, 2]:
        raise ValueError("Writing task number must be 1 or 2")

@event.listens_for(WritingResponse.response_text, 'set')
def validate_writing_response_text(target, value, oldvalue, initiator):
    """Validate writing response text"""
    if value is not None:
        if len(value.strip()) == 0:
            raise ValueError("Writing response text cannot be empty")
        if len(value) > 10000:  # Reasonable limit
            raise ValueError("Writing response text exceeds maximum length")

@event.listens_for(WritingResponse._assessment_data, 'set')
def validate_writing_assessment_data(target, value, oldvalue, initiator):
    """Validate writing assessment data JSON format"""
    if not validate_json_field(value, "assessment_data"):
        raise ValueError("Writing assessment data must be valid JSON")

# AssessmentSpeakingResponse validation events
@event.listens_for(AssessmentSpeakingResponse.part_number, 'set')
def validate_speaking_part_number(target, value, oldvalue, initiator):
    """Validate speaking part number"""
    if value is not None and value not in [1, 2, 3]:
        raise ValueError("Speaking part number must be 1, 2, or 3")

@event.listens_for(AssessmentSpeakingResponse._assessment_data, 'set')
def validate_speaking_assessment_data(target, value, oldvalue, initiator):
    """Validate speaking assessment data JSON format"""
    if not validate_json_field(value, "assessment_data"):
        raise ValueError("Speaking assessment data must be valid JSON")

@event.listens_for(AssessmentSpeakingResponse.gcp_audio_url, 'set')
def validate_gcp_audio_url(target, value, oldvalue, initiator):
    """Validate GCP audio URL format"""
    if value:
        from urllib.parse import urlparse
        parsed = urlparse(value)
        if not parsed.scheme in ['http', 'https'] or not parsed.netloc:
            raise ValueError("Invalid GCP audio URL format")

@event.listens_for(AssessmentSpeakingResponse.gcp_transcript_url, 'set')
def validate_gcp_transcript_url(target, value, oldvalue, initiator):
    """Validate GCP transcript URL format"""
    if value:
        from urllib.parse import urlparse
        parsed = urlparse(value)
        if not parsed.scheme in ['http', 'https'] or not parsed.netloc:
            raise ValueError("Invalid GCP transcript URL format")

@event.listens_for(AssessmentSpeakingResponse.gcp_assessment_url, 'set')
def validate_gcp_assessment_url(target, value, oldvalue, initiator):
    """Validate GCP assessment URL format"""
    if value:
        from urllib.parse import urlparse
        parsed = urlparse(value)
        if not parsed.scheme in ['http', 'https'] or not parsed.netloc:
            raise ValueError("Invalid GCP assessment URL format")

# Before insert/update validation events
@event.listens_for(User, 'before_insert')
@event.listens_for(User, 'before_update')
def validate_user_before_save(mapper, connection, target):
    """Comprehensive user validation before save"""
    # Ensure required fields are present
    if not target.email:
        raise ValueError("Email is required")
    
    # Validate email uniqueness (for inserts)
    if mapper.class_ == User and hasattr(target, '_sa_instance_state'):
        if target._sa_instance_state.pending:  # New record
            existing = connection.execute(
                f"SELECT id FROM user WHERE email = '{target.email}'"
            ).fetchone()
            if existing:
                raise ValueError("Email already exists")

@event.listens_for(Assessment, 'before_insert')
@event.listens_for(Assessment, 'before_update')
def validate_assessment_before_save(mapper, connection, target):
    """Comprehensive assessment validation before save"""
    # Ensure required fields are present
    if not target.title or not target.assessment_type:
        raise ValueError("Title and assessment type are required")
    
    # Validate title length
    if len(target.title) > 100:
        raise ValueError("Title exceeds maximum length")

@event.listens_for(WritingResponse, 'before_insert')
@event.listens_for(WritingResponse, 'before_update')
def validate_writing_response_before_save(mapper, connection, target):
    """Comprehensive writing response validation before save"""
    # Ensure required fields are present
    if not target.response_text:
        raise ValueError("Response text is required")
    
    # Validate minimum word count for IELTS writing
    word_count = len(target.response_text.split())
    min_words = 150 if target.task_number == 1 else 250
    if word_count < min_words:
        raise ValueError(f"Response must have at least {min_words} words")

@event.listens_for(AssessmentSpeakingResponse, 'before_insert')
@event.listens_for(AssessmentSpeakingResponse, 'before_update')
def validate_speaking_response_before_save(mapper, connection, target):
    """Comprehensive speaking response validation before save"""
    # Ensure either audio filename or transcript is present
    if not target.audio_filename and not target.transcript_text:
        raise ValueError("Either audio filename or transcript text is required")

def register_all_validation_events():
    """Register all validation events - call this after importing models"""
    print("Database validation events registered successfully")
    return True

# Additional helper functions for validation
def validate_ielts_score(score):
    """Validate IELTS band score (0-9 with 0.5 increments)"""
    if score is None:
        return True
    
    if not isinstance(score, (int, float)):
        return False
    
    # IELTS scores are 0-9 with 0.5 increments
    if score < 0 or score > 9:
        return False
    
    # Check if it's a valid increment (whole number or .5)
    if (score * 2) % 1 != 0:
        return False
    
    return True

def validate_assessment_data_structure(data, assessment_type):
    """Validate assessment data structure based on type"""
    if not data or not isinstance(data, dict):
        return False, "Assessment data must be a dictionary"
    
    if assessment_type == 'writing':
        required_fields = ['score', 'feedback', 'coherence', 'lexical_resource', 'grammar', 'task_achievement']
    elif assessment_type == 'speaking':
        required_fields = ['score', 'feedback', 'pronunciation', 'fluency', 'grammar', 'vocabulary']
    else:
        return False, "Invalid assessment type"
    
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    # Validate all scores
    for field in required_fields:
        if field == 'feedback':
            continue
        if not validate_ielts_score(data.get(field)):
            return False, f"Invalid score for {field}"
    
    return True, ""