"""
DynamoDB Data Access Layer for IELTS GenAI Prep
Replaces SQLAlchemy models with DynamoDB Global Tables for serverless architecture
"""
import boto3
import json
import os
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from werkzeug.security import generate_password_hash, check_password_hash
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

class DynamoDBConnection:
    """Manages DynamoDB connection and region switching"""
    
    def __init__(self, region='us-east-1'):
        self.region = region
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.regions = ['us-east-1', 'eu-west-1', 'ap-southeast-1']
    
    def get_table(self, table_name: str):
        """Get DynamoDB table with automatic region fallback"""
        try:
            return self.dynamodb.Table(table_name)
        except ClientError as e:
            logger.warning(f"Failed to connect to {table_name} in {self.region}: {e}")
            # Try other regions for fallback
            for region in self.regions:
                if region != self.region:
                    try:
                        dynamodb = boto3.resource('dynamodb', region_name=region)
                        return dynamodb.Table(table_name)
                    except ClientError:
                        continue
            raise e


class UserDAL:
    """User Data Access Layer using DynamoDB Global Tables"""
    
    def __init__(self, connection: DynamoDBConnection):
        self.conn = connection
        # Use existing table names from serverless.yml
        stage = os.environ.get('STAGE', 'prod')
        table_name = f'ielts-genai-prep-users-{stage}'
        self.table = connection.get_table(table_name)
    
    def create_user(self, username: str, email: str, password: str, 
                   full_name: str = None, **kwargs) -> Dict[str, Any]:
        """Create a new user"""
        user_id = self._generate_user_id()
        password_hash = generate_password_hash(password)
        
        now = datetime.utcnow().isoformat()
        user_item = {
            'email': email.lower(),  # Primary key as per serverless.yml
            'user_id': user_id,
            'username': username,
            'password_hash': password_hash,
            'full_name': full_name,
            'profile_picture': None,
            'bio': None,
            'join_date': now,
            'last_login': None,
            'created_at': now,
            'reset_token': None,
            'reset_token_expires': None,
            'is_active': True,
            'assessment_package_status': 'none',
            'assessment_package_expiry': None,
            'subscription_status': 'none',
            'subscription_expiry': None,
            'preferred_language': 'en',
            'preferences': '{}'
        }
        
        try:
            # Check if email already exists
            if self.get_user_by_email(email):
                raise ValueError("Email already exists")
            
            # Check if username already exists
            if self.get_user_by_username(username):
                raise ValueError("Username already exists")
            
            self.table.put_item(Item=user_item)
            return self._format_user_response(user_item)
            
        except ClientError as e:
            logger.error(f"Failed to create user: {e}")
            raise
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID - requires scan since user_id is not primary key"""
        try:
            response = self.table.scan(
                FilterExpression='user_id = :user_id',
                ExpressionAttributeValues={':user_id': user_id}
            )
            
            if response['Items']:
                return self._format_user_response(response['Items'][0])
            return None
        except ClientError as e:
            logger.error(f"Failed to get user by ID {user_id}: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email - primary key lookup"""
        try:
            response = self.table.get_item(Key={'email': email.lower()})
            if 'Item' in response:
                return self._format_user_response(response['Item'])
            return None
        except ClientError as e:
            logger.error(f"Failed to get user by email {email}: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username - scan operation (consider adding GSI for performance)"""
        try:
            response = self.table.scan(
                FilterExpression='username = :username',
                ExpressionAttributeValues={':username': username}
            )
            
            if response['Items']:
                return self._format_user_response(response['Items'][0])
            return None
        except ClientError as e:
            logger.error(f"Failed to get user by username {username}: {e}")
            return None
    
    def update_user(self, email: str, **kwargs) -> bool:
        """Update user fields by email (primary key)"""
        if not kwargs:
            return True
        
        # Build update expression
        update_expr = "SET "
        expr_attr_values = {}
        expr_attr_names = {}
        
        for key, value in kwargs.items():
            if key in ['email']:  # Skip primary key
                continue
            
            attr_name = f"#{key}"
            attr_value = f":{key}"
            
            update_expr += f"{attr_name} = {attr_value}, "
            expr_attr_names[attr_name] = key
            expr_attr_values[attr_value] = value
        
        update_expr = update_expr.rstrip(', ')
        
        try:
            self.table.update_item(
                Key={'email': email.lower()},
                UpdateExpression=update_expr,
                ExpressionAttributeNames=expr_attr_names,
                ExpressionAttributeValues=expr_attr_values
            )
            return True
        except ClientError as e:
            logger.error(f"Failed to update user {email}: {e}")
            return False
    
    def check_password(self, user_id: str, password: str) -> bool:
        """Check user password"""
        user = self.get_user_by_id(user_id)
        if user and user.get('password_hash'):
            return check_password_hash(user['password_hash'], password)
        return False
    
    def set_password(self, user_id: str, password: str) -> bool:
        """Set user password"""
        password_hash = generate_password_hash(password)
        return self.update_user(user_id, password_hash=password_hash)
    
    def has_active_assessment_package(self, user_id: str) -> bool:
        """Check if user has active assessment package"""
        user = self.get_user_by_id(user_id)
        if not user or not user.get('assessment_package_expiry'):
            return False
        
        expiry = datetime.fromisoformat(user['assessment_package_expiry'])
        return (user.get('assessment_package_status') == 'active' and 
                expiry > datetime.utcnow())
    
    def _generate_user_id(self) -> str:
        """Generate unique user ID"""
        timestamp = int(datetime.utcnow().timestamp() * 1000000)
        random_part = secrets.token_hex(8)
        return f"user_{timestamp}_{random_part}"
    
    def _format_user_response(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Format DynamoDB item for application use"""
        # Convert DynamoDB format to application format
        user = {
            'id': item['user_id'],
            'user_id': item['user_id'],
            'username': item['username'],
            'email': item['email'],
            'password_hash': item['password_hash'],
            'full_name': item.get('full_name'),
            'profile_picture': item.get('profile_picture'),
            'bio': item.get('bio'),
            'is_active': item.get('is_active', True),
            'preferred_language': item.get('preferred_language', 'en'),
            'assessment_package_status': item.get('assessment_package_status', 'none'),
            'assessment_package_expiry': item.get('assessment_package_expiry'),
            'subscription_status': item.get('subscription_status', 'none'),
            'subscription_expiry': item.get('subscription_expiry')
        }
        
        # Parse timestamps
        for field in ['join_date', 'last_login', 'created_at', 'reset_token_expires']:
            if item.get(field):
                try:
                    user[field] = datetime.fromisoformat(item[field])
                except (ValueError, TypeError):
                    user[field] = None
            else:
                user[field] = None
        
        # Parse preferences JSON
        try:
            user['preferences'] = json.loads(item.get('preferences', '{}'))
        except (json.JSONDecodeError, TypeError):
            user['preferences'] = {}
        
        return user


class QRTokenDAL:
    """QR Token Data Access Layer for single-use encrypted QR authentication"""
    
    def __init__(self, connection: DynamoDBConnection):
        self.conn = connection
        self.table = connection.get_table('ielts-genai-qr-tokens')
        self.encryption_key = self._get_encryption_key()
    
    def create_qr_token(self, browser_session_id: str, ttl_seconds: int = 120) -> Dict[str, Any]:
        """Create encrypted single-use QR token"""
        token_id = self._generate_token_id()
        nonce = secrets.token_hex(16)
        
        # Create expiration timestamp
        expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
        ttl_timestamp = int(expires_at.timestamp())
        
        # Encrypt the token payload
        payload = {
            'token_id': token_id,
            'browser_session_id': browser_session_id,
            'nonce': nonce,
            'created_at': datetime.utcnow().isoformat()
        }
        
        encrypted_code = self._encrypt_payload(payload)
        
        qr_item = {
            'token_id': token_id,
            'browser_session_id': browser_session_id,
            'encrypted_code': encrypted_code,
            'nonce': nonce,
            'status': 'pending',
            'expires_at': expires_at.isoformat(),
            'claimed_user_id': None,
            'created_at': datetime.utcnow().isoformat(),
            'ttl': ttl_timestamp  # DynamoDB TTL attribute
        }
        
        try:
            self.table.put_item(Item=qr_item)
            return {
                'token_id': token_id,
                'qr_code': encrypted_code,
                'expires_at': expires_at.isoformat()
            }
        except ClientError as e:
            logger.error(f"Failed to create QR token: {e}")
            raise
    
    def consume_qr_token(self, encrypted_code: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Consume QR token (single-use, validates and marks as claimed)"""
        try:
            # Decrypt and validate the code
            payload = self._decrypt_payload(encrypted_code)
            if not payload:
                return None
            
            token_id = payload.get('token_id')
            if not token_id:
                return None
            
            # Get the token from DynamoDB
            response = self.table.get_item(Key={'token_id': token_id})
            if 'Item' not in response:
                return None
            
            qr_token = response['Item']
            
            # Validate token state
            if qr_token['status'] != 'pending':
                logger.warning(f"QR token {token_id} already consumed or expired")
                return None
            
            if qr_token['nonce'] != payload.get('nonce'):
                logger.warning(f"QR token {token_id} nonce mismatch")
                return None
            
            # Check expiration
            expires_at = datetime.fromisoformat(qr_token['expires_at'])
            if expires_at <= datetime.utcnow():
                self._mark_token_expired(token_id)
                return None
            
            # Mark as claimed (single-use)
            success = self._mark_token_claimed(token_id, user_id)
            if success:
                return {
                    'token_id': token_id,
                    'browser_session_id': qr_token['browser_session_id'],
                    'user_id': user_id
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to consume QR token: {e}")
            return None
    
    def _mark_token_claimed(self, token_id: str, user_id: str) -> bool:
        """Atomically mark token as claimed"""
        try:
            self.table.update_item(
                Key={'token_id': token_id},
                UpdateExpression='SET #status = :claimed, claimed_user_id = :user_id',
                ConditionExpression='#status = :pending',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':claimed': 'claimed',
                    ':pending': 'pending',
                    ':user_id': user_id
                }
            )
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                logger.warning(f"QR token {token_id} already claimed")
            else:
                logger.error(f"Failed to claim QR token {token_id}: {e}")
            return False
    
    def _mark_token_expired(self, token_id: str) -> bool:
        """Mark token as expired"""
        try:
            self.table.update_item(
                Key={'token_id': token_id},
                UpdateExpression='SET #status = :expired',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={':expired': 'expired'}
            )
            return True
        except ClientError as e:
            logger.error(f"Failed to expire QR token {token_id}: {e}")
            return False
    
    def _generate_token_id(self) -> str:
        """Generate unique token ID"""
        timestamp = int(datetime.utcnow().timestamp() * 1000000)
        random_part = secrets.token_hex(8)
        return f"qr_{timestamp}_{random_part}"
    
    def _get_encryption_key(self) -> str:
        """Get encryption key from environment or generate for development"""
        import os
        return os.environ.get('QR_ENCRYPTION_KEY', 'dev_qr_encryption_key_change_in_production')
    
    def _encrypt_payload(self, payload: Dict[str, Any]) -> str:
        """Encrypt QR payload using HMAC-based encryption"""
        import hmac
        
        payload_json = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            self.encryption_key.encode(),
            payload_json.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Combine payload and signature
        encrypted_data = {
            'payload': payload_json,
            'signature': signature
        }
        
        # Base64 encode for URL safety
        import base64
        encrypted_bytes = json.dumps(encrypted_data).encode()
        return base64.urlsafe_b64encode(encrypted_bytes).decode()
    
    def _decrypt_payload(self, encrypted_code: str) -> Optional[Dict[str, Any]]:
        """Decrypt and validate QR payload"""
        import hmac
        import base64
        
        try:
            # Decode from base64
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_code.encode())
            encrypted_data = json.loads(encrypted_bytes.decode())
            
            payload_json = encrypted_data['payload']
            signature = encrypted_data['signature']
            
            # Verify signature
            expected_signature = hmac.new(
                self.encryption_key.encode(),
                payload_json.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                logger.warning("QR token signature verification failed")
                return None
            
            return json.loads(payload_json)
            
        except Exception as e:
            logger.warning(f"Failed to decrypt QR payload: {e}")
            return None


class AssessmentEntitlementDAL:
    """Assessment Entitlement Data Access Layer"""
    
    def __init__(self, connection: DynamoDBConnection):
        self.conn = connection
        stage = os.environ.get('STAGE', 'prod')
        table_name = f'ielts-genai-prep-entitlements-{stage}'
        self.table = connection.get_table(table_name)
    
    def create_entitlement(self, user_id: str, product_id: str, remaining_uses: int,
                          expires_at: Optional[datetime] = None, 
                          transaction_id: Optional[str] = None) -> str:
        """Create assessment entitlement"""
        entitlement_id = self._generate_entitlement_id()
        
        entitlement_item = {
            'entitlement_id': entitlement_id,
            'user_id': user_id,
            'product_id': product_id,
            'remaining_uses': remaining_uses,
            'expires_at': expires_at.isoformat() if expires_at else None,
            'transaction_id': transaction_id,
            'created_at': datetime.utcnow().isoformat(),
            'GSI1PK': f'USER#{user_id}',  # For user lookups
            'GSI1SK': f'PRODUCT#{product_id}#{entitlement_id}'
        }
        
        try:
            self.table.put_item(Item=entitlement_item)
            return entitlement_id
        except ClientError as e:
            logger.error(f"Failed to create entitlement: {e}")
            raise
    
    def get_user_entitlements(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all entitlements for a user"""
        try:
            response = self.table.query(
                IndexName='GSI1',
                KeyConditionExpression='GSI1PK = :pk',
                ExpressionAttributeValues={':pk': f'USER#{user_id}'}
            )
            
            return [self._format_entitlement_response(item) for item in response['Items']]
        except ClientError as e:
            logger.error(f"Failed to get entitlements for user {user_id}: {e}")
            return []
    
    def consume_entitlement(self, user_id: str, product_id: str) -> bool:
        """Consume one use of an entitlement"""
        entitlements = self.get_user_entitlements(user_id)
        
        # Find active entitlement for product
        for entitlement in entitlements:
            if (entitlement['product_id'] == product_id and 
                entitlement['remaining_uses'] > 0):
                
                # Check expiration
                if entitlement['expires_at']:
                    if entitlement['expires_at'] <= datetime.utcnow():
                        continue
                
                # Decrement usage
                try:
                    self.table.update_item(
                        Key={'entitlement_id': entitlement['entitlement_id']},
                        UpdateExpression='SET remaining_uses = remaining_uses - :dec',
                        ConditionExpression='remaining_uses > :zero',
                        ExpressionAttributeValues={':dec': 1, ':zero': 0}
                    )
                    return True
                except ClientError as e:
                    if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                        continue  # Try next entitlement
                    logger.error(f"Failed to consume entitlement: {e}")
        
        return False
    
    def _generate_entitlement_id(self) -> str:
        """Generate unique entitlement ID"""
        timestamp = int(datetime.utcnow().timestamp() * 1000000)
        random_part = secrets.token_hex(8)
        return f"ent_{timestamp}_{random_part}"
    
    def _format_entitlement_response(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Format DynamoDB item for application use"""
        entitlement = dict(item)
        
        # Parse timestamps
        for field in ['created_at', 'expires_at']:
            if item.get(field):
                try:
                    entitlement[field] = datetime.fromisoformat(item[field])
                except (ValueError, TypeError):
                    entitlement[field] = None
        
        return entitlement


# Main DAL Manager
class IELTSGenAIDAL:
    """Main Data Access Layer for IELTS GenAI Prep"""
    
    def __init__(self, region='us-east-1'):
        self.connection = DynamoDBConnection(region)
        self.users = UserDAL(self.connection)
        self.qr_tokens = QRTokenDAL(self.connection)
        self.entitlements = AssessmentEntitlementDAL(self.connection)
    
    def health_check(self) -> Dict[str, Any]:
        """Check DynamoDB connectivity and table status"""
        try:
            # Test basic connectivity
            self.users.table.table_status
            return {
                'status': 'healthy',
                'region': self.connection.region,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'region': self.connection.region,
                'timestamp': datetime.utcnow().isoformat()
            }


# Global DAL instance
dal = None

def get_dal() -> IELTSGenAIDAL:
    """Get global DAL instance"""
    global dal
    if dal is None:
        dal = IELTSGenAIDAL()
    return dal