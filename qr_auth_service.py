"""
QR Code Authentication Service for ieltsaiprep.com
Handles QR code generation, verification, and session management
"""

import json
import uuid
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import os
import logging

logger = logging.getLogger(__name__)

class MockDynamoDBTable:
    """Mock DynamoDB table for testing"""
    def __init__(self, table_name):
        self.table_name = table_name
        self._items = {}
    
    def put_item(self, Item):
        key = Item.get('token_id') or Item.get('assessment_id') or Item.get('user_email')
        self._items[key] = Item
        return {'ResponseMetadata': {'HTTPStatusCode': 200}}
    
    def get_item(self, Key):
        key_value = list(Key.values())[0]
        item = self._items.get(key_value)
        if item:
            return {'Item': item}
        return {}
    
    def update_item(self, Key, **kwargs):
        key_value = list(Key.values())[0]
        if key_value in self._items:
            # Simple update implementation
            if 'UpdateExpression' in kwargs:
                # Parse SET expressions
                if 'used = :used' in kwargs['UpdateExpression']:
                    self._items[key_value]['used'] = True
                if 'used_at = :used_at' in kwargs['UpdateExpression']:
                    self._items[key_value]['used_at'] = kwargs['ExpressionAttributeValues'][':used_at']
        return {'ResponseMetadata': {'HTTPStatusCode': 200}}
    
    def scan(self, **kwargs):
        # Simple scan implementation for testing
        items = list(self._items.values())
        return {'Items': items, 'Count': len(items)}

class QRAuthService:
    """QR Code Authentication Service"""
    
    def __init__(self):
        # Use mock DynamoDB for .replit test environment
        self.use_mock = os.environ.get('USE_MOCK_AWS', 'true').lower() == 'true'
        
        if self.use_mock:
            logger.info("Using mock DynamoDB for test environment")
            self.qr_tokens_table = MockDynamoDBTable('QRTokens-test')
            self.assessments_table = MockDynamoDBTable('IELTSAssessments-test')
        else:
            import boto3
            self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
            self.qr_tokens_table = self.dynamodb.Table('QRTokens-test')
            self.assessments_table = self.dynamodb.Table('IELTSAssessments-test')
        
        # Redis for session management (test instance)
        try:
            import redis
            self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
            self.redis_client.ping()
            logger.info("Connected to Redis for session management")
        except:
            logger.warning("Redis not available, using memory storage")
            self.redis_client = None
            self._memory_sessions = {}
    
    def generate_qr_token(self, user_email: str, purchase_verified: bool = True) -> Dict[str, Any]:
        """
        Generate QR code token after successful purchase verification
        """
        try:
            if not purchase_verified:
                return {
                    'success': False,
                    'error': 'Purchase verification required'
                }
            
            # Generate unique token
            token_id = str(uuid.uuid4())
            created_at = datetime.utcnow()
            expires_at = created_at + timedelta(minutes=10)  # 10-minute expiration
            
            # Store token in DynamoDB
            token_data = {
                'token_id': token_id,
                'user_email': user_email,
                'created_at': created_at.isoformat(),
                'expires_at': int(expires_at.timestamp()),
                'used': False,
                'purpose': 'website_authentication'
            }
            
            self.qr_tokens_table.put_item(Item=token_data)
            
            # Generate QR code data
            qr_data = {
                'token': token_id,
                'domain': 'ieltsaiprep.com',
                'timestamp': int(created_at.timestamp())
            }
            
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
        """
        Verify QR code token and create website session
        """
        try:
            # Get token from DynamoDB
            response = self.qr_tokens_table.get_item(Key={'token_id': token_id})
            
            if 'Item' not in response:
                return {
                    'success': False,
                    'error': 'Invalid token'
                }
            
            token_data = response['Item']
            
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
            
            # Mark token as used (single-use)
            self.qr_tokens_table.update_item(
                Key={'token_id': token_id},
                UpdateExpression='SET used = :used, used_at = :used_at',
                ExpressionAttributeValues={
                    ':used': True,
                    ':used_at': datetime.utcnow().isoformat()
                }
            )
            
            # Create website session
            session_id = self._create_website_session(token_data['user_email'])
            
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
        session_data = {
            'user_email': user_email,
            'authenticated': True,
            'created_at': datetime.utcnow().isoformat(),
            'source': 'qr_authentication'
        }
        
        # Store session (1 hour expiration)
        if self.redis_client:
            self.redis_client.setex(
                f"session:{session_id}",
                3600,  # 1 hour
                json.dumps(session_data)
            )
        else:
            # Memory fallback
            self._memory_sessions[session_id] = {
                **session_data,
                'expires_at': time.time() + 3600
            }
        
        return session_id
    
    def verify_website_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Verify website session for protected routes"""
        try:
            if self.redis_client:
                session_data = self.redis_client.get(f"session:{session_id}")
                if session_data:
                    return json.loads(session_data)
            else:
                # Memory fallback
                session = self._memory_sessions.get(session_id)
                if session and time.time() < session.get('expires_at', 0):
                    return session
                elif session:
                    # Remove expired session
                    del self._memory_sessions[session_id]
            
            return None
            
        except Exception as e:
            logger.error(f"Session verification error: {str(e)}")
            return None
    
    def get_user_assessments(self, user_email: str) -> Dict[str, Any]:
        """Get user assessments for website display"""
        try:
            if self.use_mock:
                # For testing, create sample assessment data
                sample_assessments = [
                    {
                        'assessment_id': f"{user_email}_test_1",
                        'assessment_type': 'academic_speaking',
                        'created_at': datetime.utcnow().isoformat(),
                        'transcript': 'Test speaking assessment transcript',
                        'feedback': 'Good pronunciation and fluency',
                        'overall_score': 7.5
                    },
                    {
                        'assessment_id': f"{user_email}_test_2",
                        'assessment_type': 'academic_writing',
                        'created_at': datetime.utcnow().isoformat(),
                        'essay_text': 'Sample essay text for testing',
                        'assessment_result': {'overall_score': 7.0, 'feedback': 'Well-structured essay'},
                        'overall_score': 7.0
                    }
                ]
                assessments = sample_assessments
            else:
                response = self.assessments_table.scan(
                    FilterExpression='user_email = :email',
                    ExpressionAttributeValues={':email': user_email}
                )
                assessments = response.get('Items', [])
            
            # Filter out audio data, only return text assessments
            filtered_assessments = []
            for assessment in assessments:
                filtered_assessment = {
                    'assessment_id': assessment.get('assessment_id'),
                    'assessment_type': assessment.get('assessment_type'),
                    'created_at': assessment.get('created_at'),
                    'transcript': assessment.get('transcript', ''),
                    'essay_text': assessment.get('essay_text', ''),
                    'assessment_result': assessment.get('assessment_result', {}),
                    'feedback': assessment.get('feedback', ''),
                    'score': assessment.get('overall_score', 0)
                }
                filtered_assessments.append(filtered_assessment)
            
            return {
                'success': True,
                'assessments': filtered_assessments,
                'total_count': len(filtered_assessments)
            }
            
        except Exception as e:
            logger.error(f"Get assessments error: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to retrieve assessments',
                'assessments': []
            }

# Global service instance
qr_auth_service = QRAuthService()