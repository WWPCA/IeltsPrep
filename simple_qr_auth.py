"""
Simple QR Authentication Service for .replit testing
Uses in-memory storage for tokens and sessions
"""

import json
import uuid
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class SimpleQRAuthService:
    """Simple QR Authentication Service using in-memory storage"""
    
    def __init__(self):
        self._tokens = {}  # Store QR tokens
        self._sessions = {}  # Store user sessions
        self._assessments = {}  # Store sample assessments
        
        # Initialize with sample data
        self._create_sample_data()
    
    def _create_sample_data(self):
        """Create sample assessment data for testing"""
        sample_user = "test@ieltsaiprep.com"
        
        self._assessments[sample_user] = [
            {
                'assessment_id': f"{sample_user}_speaking_1",
                'assessment_type': 'academic_speaking',
                'created_at': '2024-12-01T10:00:00Z',
                'transcript': 'User spoke about education systems and provided well-structured responses with good vocabulary usage.',
                'feedback': 'Excellent fluency and pronunciation. Good use of complex grammatical structures.',
                'overall_score': 7.5,
                'scores': {
                    'fluency': 7.5,
                    'vocabulary': 7.0,
                    'grammar': 8.0,
                    'pronunciation': 7.5
                }
            },
            {
                'assessment_id': f"{sample_user}_writing_1",
                'assessment_type': 'academic_writing',
                'created_at': '2024-12-01T14:30:00Z',
                'essay_text': 'Education plays a crucial role in shaping society. Universities should focus on both theoretical knowledge and practical skills...',
                'prompt': 'Some people believe that universities should focus on providing graduates with the knowledge and skills needed in the workplace. Others believe universities should provide access to knowledge for its own sake. Discuss both views and give your opinion.',
                'feedback': 'Well-structured essay with clear arguments. Good use of linking words and academic vocabulary.',
                'overall_score': 7.0,
                'scores': {
                    'task_achievement': 7.0,
                    'coherence_cohesion': 7.0,
                    'lexical_resource': 6.5,
                    'grammatical_accuracy': 7.5
                }
            },
            {
                'assessment_id': f"{sample_user}_speaking_2",
                'assessment_type': 'general_speaking',
                'created_at': '2024-12-02T09:15:00Z',
                'transcript': 'Discussed daily routines, travel experiences, and future plans. Demonstrated natural conversation flow.',
                'feedback': 'Natural speaking style with appropriate use of informal language. Good interaction skills.',
                'overall_score': 6.5,
                'scores': {
                    'fluency': 6.5,
                    'vocabulary': 6.0,
                    'grammar': 7.0,
                    'pronunciation': 6.5
                }
            }
        ]
    
    def generate_qr_token(self, user_email: str, purchase_verified: bool = True) -> Dict[str, Any]:
        """Generate QR code token after purchase verification"""
        try:
            if not purchase_verified:
                return {
                    'success': False,
                    'error': 'Purchase verification required'
                }
            
            # Generate unique token
            token_id = str(uuid.uuid4())
            created_at = datetime.utcnow()
            expires_at = created_at + timedelta(minutes=10)
            
            # Store token
            self._tokens[token_id] = {
                'token_id': token_id,
                'user_email': user_email,
                'created_at': created_at.isoformat(),
                'expires_at': int(expires_at.timestamp()),
                'used': False,
                'purpose': 'website_authentication'
            }
            
            # Generate QR code data
            qr_data = {
                'token': token_id,
                'domain': 'ieltsaiprep.com',
                'timestamp': int(created_at.timestamp())
            }
            
            logger.info(f"QR token generated for {user_email}: {token_id}")
            
            return {
                'success': True,
                'token_id': token_id,
                'qr_data': json.dumps(qr_data),
                'expires_in_minutes': 10,
                'expires_at': expires_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"QR token generation error: {str(e)}")
            return {
                'success': False,
                'error': 'Token generation failed'
            }
    
    def verify_qr_token(self, token_id: str, website_domain: str = 'ieltsaiprep.com') -> Dict[str, Any]:
        """Verify QR code token and create website session"""
        try:
            # Get token
            token_data = self._tokens.get(token_id)
            
            if not token_data:
                return {
                    'success': False,
                    'error': 'Invalid token'
                }
            
            # Check if token is already used
            if token_data.get('used', False):
                return {
                    'success': False,
                    'error': 'Token already used'
                }
            
            # Check if token is expired
            if time.time() > token_data['expires_at']:
                return {
                    'success': False,
                    'error': 'Token expired'
                }
            
            # Mark token as used
            token_data['used'] = True
            token_data['used_at'] = datetime.utcnow().isoformat()
            
            # Create website session
            session_id = self._create_website_session(token_data['user_email'])
            
            logger.info(f"QR token verified successfully for {token_data['user_email']}")
            
            return {
                'success': True,
                'user_email': token_data['user_email'],
                'session_id': session_id,
                'message': 'Authentication successful'
            }
            
        except Exception as e:
            logger.error(f"QR token verification error: {str(e)}")
            return {
                'success': False,
                'error': 'Token verification failed'
            }
    
    def _create_website_session(self, user_email: str) -> str:
        """Create website session for authenticated user"""
        session_id = f"web_session_{hashlib.md5(user_email.encode()).hexdigest()}_{int(time.time())}"
        
        self._sessions[session_id] = {
            'user_email': user_email,
            'authenticated': True,
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': time.time() + 3600,  # 1 hour
            'source': 'qr_authentication'
        }
        
        return session_id
    
    def verify_website_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Verify website session for protected routes"""
        try:
            session = self._sessions.get(session_id)
            
            if not session:
                return None
            
            # Check if session is expired
            if time.time() > session.get('expires_at', 0):
                # Remove expired session
                del self._sessions[session_id]
                return None
            
            return session
            
        except Exception as e:
            logger.error(f"Session verification error: {str(e)}")
            return None
    
    def get_user_assessments(self, user_email: str) -> Dict[str, Any]:
        """Get user assessments for website display"""
        try:
            assessments = self._assessments.get(user_email, [])
            
            return {
                'success': True,
                'assessments': assessments,
                'total_count': len(assessments)
            }
            
        except Exception as e:
            logger.error(f"Get assessments error: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to retrieve assessments',
                'assessments': []
            }
    
    def add_user_assessment(self, user_email: str, assessment_data: Dict[str, Any]):
        """Add assessment for user (for testing purposes)"""
        if user_email not in self._assessments:
            self._assessments[user_email] = []
        
        assessment_data['assessment_id'] = f"{user_email}_{len(self._assessments[user_email]) + 1}"
        assessment_data['created_at'] = datetime.utcnow().isoformat()
        
        self._assessments[user_email].append(assessment_data)
        
        logger.info(f"Assessment added for {user_email}: {assessment_data['assessment_type']}")

# Global service instance
qr_auth_service = SimpleQRAuthService()