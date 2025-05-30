"""
Enhanced AI Assessment Services
Implements TrueScore® and ClearScore® assessment validation and integration
based on technical analysis recommendations.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from app import db
from models import WritingResponse, AssessmentSpeakingResponse, UserAssessmentAttempt
from botocore.exceptions import ClientError, BotoCoreError

# Configure logging
logger = logging.getLogger(__name__)

class TrueScoreValidator:
    """Validator for TrueScore® writing assessment data from AWS Nova Micro"""
    
    REQUIRED_FIELDS = [
        'score', 'feedback', 'coherence', 'lexical_resource', 
        'grammar', 'task_achievement'
    ]
    
    OPTIONAL_FIELDS = [
        'detailed_feedback', 'band_descriptors', 'improvement_suggestions',
        'word_count', 'time_taken', 'assessment_timestamp'
    ]
    
    @staticmethod
    def validate_assessment_data(data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate TrueScore® assessment data structure.
        
        Args:
            data: Assessment data from AWS Nova Micro
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(data, dict):
            return False, "Assessment data must be a dictionary"
        
        # Check required fields
        missing_fields = [field for field in TrueScoreValidator.REQUIRED_FIELDS 
                         if field not in data]
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
        
        # Validate score range (IELTS bands 0-9)
        score = data.get('score')
        if not isinstance(score, (int, float)) or not (0 <= score <= 9):
            return False, "Score must be a number between 0 and 9"
        
        # Validate sub-scores if present
        sub_scores = ['coherence', 'lexical_resource', 'grammar', 'task_achievement']
        for sub_score in sub_scores:
            if sub_score in data:
                value = data[sub_score]
                if not isinstance(value, (int, float)) or not (0 <= value <= 9):
                    return False, f"{sub_score} must be a number between 0 and 9"
        
        # Validate feedback is a string
        if not isinstance(data.get('feedback'), str):
            return False, "Feedback must be a string"
        
        return True, ""

class ClearScoreValidator:
    """Validator for ClearScore® speaking assessment data from AWS Sonic + Nova Micro"""
    
    REQUIRED_FIELDS = [
        'score', 'feedback', 'pronunciation', 'fluency', 
        'grammar', 'vocabulary'
    ]
    
    OPTIONAL_FIELDS = [
        'detailed_feedback', 'band_descriptors', 'improvement_suggestions',
        'speaking_duration', 'assessment_timestamp', 'conversation_flow',
        'confidence_level', 'pace_analysis'
    ]
    
    @staticmethod
    def validate_assessment_data(data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate ClearScore® assessment data structure.
        
        Args:
            data: Assessment data from AWS Sonic + Nova Micro
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(data, dict):
            return False, "Assessment data must be a dictionary"
        
        # Check required fields
        missing_fields = [field for field in ClearScoreValidator.REQUIRED_FIELDS 
                         if field not in data]
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
        
        # Validate score range (IELTS bands 0-9)
        score = data.get('score')
        if not isinstance(score, (int, float)) or not (0 <= score <= 9):
            return False, "Score must be a number between 0 and 9"
        
        # Validate sub-scores
        sub_scores = ['pronunciation', 'fluency', 'grammar', 'vocabulary']
        for sub_score in sub_scores:
            if sub_score in data:
                value = data[sub_score]
                if not isinstance(value, (int, float)) or not (0 <= value <= 9):
                    return False, f"{sub_score} must be a number between 0 and 9"
        
        # Validate feedback is a string
        if not isinstance(data.get('feedback'), str):
            return False, "Feedback must be a string"
        
        return True, ""

class AIAssessmentService:
    """Enhanced AI assessment service with proper error handling and validation"""
    
    @staticmethod
    def process_writing_assessment(text: str, user_id: int, attempt_id: int, task_number: int) -> Dict[str, Any]:
        """
        Process writing assessment using TrueScore® (AWS Nova Micro).
        
        Args:
            text: Writing response text
            user_id: User ID
            attempt_id: Assessment attempt ID
            task_number: Writing task number (1 or 2)
            
        Returns:
            Dictionary with success status and assessment data
        """
        try:
            # Import AWS services here to avoid circular imports
            from nova_writing_assessment import assess_writing_task1, assess_writing_task2
            
            # Validate input
            if not text or not text.strip():
                return {
                    'success': False,
                    'error': 'Writing response cannot be empty',
                    'error_type': 'validation_error'
                }
            
            if len(text.strip()) < 150:
                return {
                    'success': False,
                    'error': 'Writing response must be at least 150 words',
                    'error_type': 'validation_error'
                }
            
            # Call appropriate assessment function
            if task_number == 1:
                aws_response = assess_writing_task1(text, user_id)
            elif task_number == 2:
                aws_response = assess_writing_task2(text, user_id)
            else:
                return {
                    'success': False,
                    'error': 'Invalid task number',
                    'error_type': 'validation_error'
                }
            
            if not aws_response or not aws_response.get('success'):
                return {
                    'success': False,
                    'error': aws_response.get('error', 'Assessment service unavailable'),
                    'error_type': 'assessment_error'
                }
            
            # Validate assessment data
            assessment_data = aws_response.get('assessment_data', {})
            is_valid, error_msg = TrueScoreValidator.validate_assessment_data(assessment_data)
            
            if not is_valid:
                logger.error(f"TrueScore® validation failed: {error_msg}")
                return {
                    'success': False,
                    'error': f'Assessment data validation failed: {error_msg}',
                    'error_type': 'validation_error'
                }
            
            # Store assessment response
            writing_response = WritingResponse(
                attempt_id=attempt_id,
                task_number=task_number,
                response_text=text
            )
            
            # Use enhanced validation method
            writing_response.set_truescore_assessment(assessment_data)
            
            db.session.add(writing_response)
            db.session.commit()
            
            return {
                'success': True,
                'score': assessment_data.get('score'),
                'feedback': assessment_data.get('feedback'),
                'assessment_id': writing_response.id,
                'detailed_scores': {
                    'coherence': assessment_data.get('coherence'),
                    'lexical_resource': assessment_data.get('lexical_resource'),
                    'grammar': assessment_data.get('grammar'),
                    'task_achievement': assessment_data.get('task_achievement')
                }
            }
            
        except (ClientError, BotoCoreError) as e:
            logger.error(f"AWS error in writing assessment: {e}")
            return {
                'success': False,
                'error': 'Assessment service temporarily unavailable',
                'error_type': 'aws_error'
            }
        except Exception as e:
            logger.error(f"Unexpected error in writing assessment: {e}")
            return {
                'success': False,
                'error': 'Internal assessment error',
                'error_type': 'internal_error'
            }
    
    @staticmethod
    def process_speaking_assessment(audio_data: bytes, user_id: int, attempt_id: int, part_number: int) -> Dict[str, Any]:
        """
        Process speaking assessment using ClearScore® (AWS Sonic + Nova Micro).
        
        Args:
            audio_data: Audio recording data
            user_id: User ID
            attempt_id: Assessment attempt ID
            part_number: Speaking part number (1, 2, or 3)
            
        Returns:
            Dictionary with success status and assessment data
        """
        try:
            # Import AWS services here to avoid circular imports
            from nova_sonic_services import analyze_speaking_response
            
            # Validate input
            if not audio_data:
                return {
                    'success': False,
                    'error': 'Audio data cannot be empty',
                    'error_type': 'validation_error'
                }
            
            if part_number not in [1, 2, 3]:
                return {
                    'success': False,
                    'error': 'Invalid speaking part number',
                    'error_type': 'validation_error'
                }
            
            # Process with AWS Sonic
            sonic_response = analyze_speaking_response(audio_data, user_id)
            
            if not sonic_response or not sonic_response.get('success'):
                return {
                    'success': False,
                    'error': sonic_response.get('error', 'Speech analysis service unavailable'),
                    'error_type': 'assessment_error'
                }
            
            # Validate assessment data
            assessment_data = sonic_response.get('assessment_data', {})
            is_valid, error_msg = ClearScoreValidator.validate_assessment_data(assessment_data)
            
            if not is_valid:
                logger.error(f"ClearScore® validation failed: {error_msg}")
                return {
                    'success': False,
                    'error': f'Assessment data validation failed: {error_msg}',
                    'error_type': 'validation_error'
                }
            
            # Store assessment response
            speaking_response = AssessmentSpeakingResponse(
                attempt_id=attempt_id,
                part_number=part_number,
                audio_filename=sonic_response.get('audio_filename'),
                transcript_text=sonic_response.get('transcript')
            )
            
            # Use enhanced validation method
            speaking_response.set_clearscore_assessment(assessment_data)
            
            # Set GCP URLs if available
            gcp_urls = sonic_response.get('gcp_urls', {})
            if gcp_urls:
                speaking_response.set_gcp_urls(
                    audio_url=gcp_urls.get('audio_url'),
                    transcript_url=gcp_urls.get('transcript_url'),
                    assessment_url=gcp_urls.get('assessment_url')
                )
            
            db.session.add(speaking_response)
            db.session.commit()
            
            return {
                'success': True,
                'score': assessment_data.get('score'),
                'feedback': assessment_data.get('feedback'),
                'assessment_id': speaking_response.id,
                'transcript': sonic_response.get('transcript'),
                'detailed_scores': {
                    'pronunciation': assessment_data.get('pronunciation'),
                    'fluency': assessment_data.get('fluency'),
                    'grammar': assessment_data.get('grammar'),
                    'vocabulary': assessment_data.get('vocabulary')
                }
            }
            
        except (ClientError, BotoCoreError) as e:
            logger.error(f"AWS error in speaking assessment: {e}")
            return {
                'success': False,
                'error': 'Assessment service temporarily unavailable',
                'error_type': 'aws_error'
            }
        except Exception as e:
            logger.error(f"Unexpected error in speaking assessment: {e}")
            return {
                'success': False,
                'error': 'Internal assessment error',
                'error_type': 'internal_error'
            }

class GCPStorageValidator:
    """Validator for Google Cloud Storage operations"""
    
    @staticmethod
    def validate_upload_url(url: str) -> bool:
        """Validate GCP storage URL format"""
        from urllib.parse import urlparse
        
        if not url:
            return False
            
        parsed = urlparse(url)
        
        # Check for valid scheme and domain
        if parsed.scheme not in ['http', 'https']:
            return False
            
        if not parsed.netloc:
            return False
            
        # Check for GCP storage domains
        valid_domains = [
            'storage.googleapis.com',
            'storage.cloud.google.com'
        ]
        
        if not any(domain in parsed.netloc for domain in valid_domains):
            return False
            
        return True
    
    @staticmethod
    def upload_assessment_data(bucket_name: str, file_data: bytes, destination_path: str) -> Optional[str]:
        """
        Upload assessment data to GCP storage with validation.
        
        Args:
            bucket_name: GCP storage bucket name
            file_data: Data to upload
            destination_path: Path in the bucket
            
        Returns:
            Public URL if successful, None if failed
        """
        try:
            from google.cloud import storage
            
            client = storage.Client()
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(destination_path)
            
            # Upload with proper content type
            content_type = 'application/octet-stream'
            if destination_path.endswith('.json'):
                content_type = 'application/json'
            elif destination_path.endswith('.txt'):
                content_type = 'text/plain'
            elif destination_path.endswith('.wav'):
                content_type = 'audio/wav'
            
            blob.upload_from_string(file_data, content_type=content_type)
            
            # Return public URL
            public_url = blob.public_url
            
            # Validate the generated URL
            if GCPStorageValidator.validate_upload_url(public_url):
                return public_url
            else:
                logger.error(f"Generated invalid GCP URL: {public_url}")
                return None
                
        except Exception as e:
            logger.error(f"GCP upload error: {e}")
            return None

def create_assessment_summary(user_id: int, assessment_type: str) -> Dict[str, Any]:
    """
    Create a comprehensive assessment summary for a user.
    
    Args:
        user_id: User ID
        assessment_type: Type of assessment (writing/speaking)
        
    Returns:
        Dictionary with assessment summary data
    """
    try:
        # Get all attempts for this user and assessment type
        attempts = UserAssessmentAttempt.query.filter_by(
            user_id=user_id,
            assessment_type=assessment_type,
            status='completed'
        ).order_by(UserAssessmentAttempt.start_time.desc()).all()
        
        if not attempts:
            return {
                'success': False,
                'error': 'No completed assessments found'
            }
        
        summary_data = {
            'user_id': user_id,
            'assessment_type': assessment_type,
            'total_attempts': len(attempts),
            'latest_attempt': attempts[0].start_time.isoformat() if attempts else None,
            'average_score': 0,
            'progress_trend': 'stable',
            'detailed_attempts': []
        }
        
        # Calculate statistics
        if assessment_type == 'writing':
            responses = WritingResponse.query.join(UserAssessmentAttempt).filter(
                UserAssessmentAttempt.user_id == user_id,
                UserAssessmentAttempt.status == 'completed'
            ).all()
            
            scores = []
            for response in responses:
                assessment_data = response.assessment_data
                if assessment_data and 'score' in assessment_data:
                    scores.append(assessment_data['score'])
                    summary_data['detailed_attempts'].append({
                        'attempt_id': response.attempt_id,
                        'task_number': response.task_number,
                        'score': assessment_data['score'],
                        'submission_time': response.submission_time.isoformat()
                    })
            
            if scores:
                summary_data['average_score'] = round(sum(scores) / len(scores), 1)
                # Simple trend analysis
                if len(scores) >= 2:
                    recent_avg = sum(scores[-2:]) / 2
                    older_avg = sum(scores[:-2]) / max(1, len(scores) - 2)
                    if recent_avg > older_avg + 0.5:
                        summary_data['progress_trend'] = 'improving'
                    elif recent_avg < older_avg - 0.5:
                        summary_data['progress_trend'] = 'declining'
        
        elif assessment_type == 'speaking':
            responses = AssessmentSpeakingResponse.query.join(UserAssessmentAttempt).filter(
                UserAssessmentAttempt.user_id == user_id,
                UserAssessmentAttempt.status == 'completed'
            ).all()
            
            scores = []
            for response in responses:
                assessment_data = response.assessment_data
                if assessment_data and 'score' in assessment_data:
                    scores.append(assessment_data['score'])
                    summary_data['detailed_attempts'].append({
                        'attempt_id': response.attempt_id,
                        'part_number': response.part_number,
                        'score': assessment_data['score'],
                        'submission_time': response.submission_time.isoformat()
                    })
            
            if scores:
                summary_data['average_score'] = round(sum(scores) / len(scores), 1)
        
        summary_data['success'] = True
        return summary_data
        
    except Exception as e:
        logger.error(f"Error creating assessment summary: {e}")
        return {
            'success': False,
            'error': 'Failed to generate assessment summary'
        }