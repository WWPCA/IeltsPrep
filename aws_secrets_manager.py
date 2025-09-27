"""
AWS Secrets Manager Integration for IELTS GenAI Prep
Securely manages JWT secrets, API keys, and encryption keys
"""
import os
import json
import boto3
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError
from functools import lru_cache

logger = logging.getLogger(__name__)

class SecretsManager:
    """AWS Secrets Manager client with caching and fallback"""
    
    def __init__(self, region: str = None):
        self.region = region or os.environ.get('AWS_REGION', 'us-east-1')
        self.secrets_client = boto3.client('secretsmanager', region_name=self.region)
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Development mode check - using centralized environment detection
        from environment_utils import is_development
        self.is_development = is_development()
        
        if self.is_development:
            logger.info("[SECRETS] Running in development mode with local fallbacks")
        else:
            logger.info(f"[SECRETS] Initialized for region: {self.region}")
    
    def get_secret(self, secret_name: str, return_json: bool = True) -> Optional[Any]:
        """
        Retrieve secret from AWS Secrets Manager with TTL caching
        
        Args:
            secret_name: Name of the secret in AWS Secrets Manager
            return_json: Whether to parse JSON response
            
        Returns:
            Secret value or None if not found
        """
        # Check cache first with TTL
        cache_key = f"{secret_name}:{return_json}"
        if cache_key in self.cache:
            cached_time, cached_value = self.cache[cache_key]
            if (datetime.utcnow() - cached_time).seconds < self.cache_ttl:
                return cached_value
        
        try:
            # Development fallback
            if self.is_development:
                return self._get_development_secret(secret_name, return_json)
            
            # Production AWS Secrets Manager
            response = self.secrets_client.get_secret_value(SecretId=secret_name)
            secret_value = response['SecretString']
            
            if return_json:
                try:
                    parsed_value = json.loads(secret_value)
                except json.JSONDecodeError:
                    logger.warning(f"[SECRETS] Secret {secret_name} is not valid JSON")
                    parsed_value = secret_value
            else:
                parsed_value = secret_value
            
            # Cache the result
            self.cache[cache_key] = (datetime.utcnow(), parsed_value)
            
            logger.info(f"[SECRETS] Successfully retrieved: {secret_name}")
            return parsed_value
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            
            if error_code == 'ResourceNotFoundException':
                logger.error(f"[SECRETS] Secret not found: {secret_name}")
            elif error_code == 'InvalidRequestException':
                logger.error(f"[SECRETS] Invalid request for secret: {secret_name}")
            elif error_code == 'InvalidParameterException':
                logger.error(f"[SECRETS] Invalid parameter for secret: {secret_name}")
            elif error_code == 'DecryptionFailure':
                logger.error(f"[SECRETS] Decryption failed for secret: {secret_name}")
            elif error_code == 'InternalServiceError':
                logger.error(f"[SECRETS] AWS internal error for secret: {secret_name}")
            else:
                logger.error(f"[SECRETS] Unknown error for secret {secret_name}: {e}")
            
            return None
        except Exception as e:
            logger.error(f"[SECRETS] Unexpected error retrieving {secret_name}: {e}")
            return None
    
    def _get_development_secret(self, secret_name: str, return_json: bool = True) -> Optional[Any]:
        """Development fallback secrets (never use in production)"""
        development_secrets = {
            'ielts-genai-prep/jwt': {
                'JWT_SECRET': 'dev_jwt_secret_change_in_production_12345',
                'JWT_ALGORITHM': 'HS256',
                'JWT_ACCESS_TOKEN_EXPIRES_MINUTES': 15
            },
            'ielts-genai-prep/qr-encryption': {
                'QR_ENCRYPTION_KEY': 'dev_qr_encryption_key_change_in_production',
                'QR_SIGNING_KEY': 'dev_qr_signing_key_change_in_production'
            },
            'ielts-genai-prep/apple-store': {
                'APPLE_SHARED_SECRET': 'dev_apple_secret',
                'APPLE_TEAM_ID': 'dev_team_id',
                'APPLE_KEY_ID': 'dev_key_id'
            },
            'ielts-genai-prep/google-play': {
                'GOOGLE_SERVICE_ACCOUNT_JSON': '{"type": "service_account", "project_id": "dev"}',
                'GOOGLE_PACKAGE_NAME': 'com.ieltsgenaiprep.dev'
            },
            'ielts-genai-prep/recaptcha': {
                'RECAPTCHA_SECRET_KEY': 'dev_recaptcha_secret',
                'RECAPTCHA_SITE_KEY': 'dev_recaptcha_site'
            },
            'ielts-genai-prep/kms': {
                'KMS_KEY_ID': 'alias/ielts-genai-prep-dev',
                'DATA_ENCRYPTION_KEY_SPEC': 'AES_256'
            }
        }
        
        if secret_name in development_secrets:
            logger.warning(f"[SECRETS] Using development secret: {secret_name}")
            secret_data = development_secrets[secret_name]
            return secret_data if return_json else json.dumps(secret_data)
        
        logger.error(f"[SECRETS] Development secret not found: {secret_name}")
        return None
    
    def create_secret(self, secret_name: str, secret_value: Dict[str, Any], 
                     description: str = None) -> bool:
        """Create a new secret in AWS Secrets Manager"""
        try:
            if self.is_development:
                logger.info(f"[SECRETS] Would create secret in production: {secret_name}")
                return True
            
            self.secrets_client.create_secret(
                Name=secret_name,
                SecretString=json.dumps(secret_value),
                Description=description or f"Secret for {secret_name}",
                ReplicationRegions=[
                    {
                        'Region': 'eu-west-1',
                        'KmsKeyId': 'alias/aws/secretsmanager'
                    },
                    {
                        'Region': 'ap-southeast-1', 
                        'KmsKeyId': 'alias/aws/secretsmanager'
                    }
                ]
            )
            
            logger.info(f"[SECRETS] Created secret: {secret_name}")
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceExistsException':
                logger.warning(f"[SECRETS] Secret already exists: {secret_name}")
                return True
            else:
                logger.error(f"[SECRETS] Failed to create secret {secret_name}: {e}")
                return False
        except Exception as e:
            logger.error(f"[SECRETS] Unexpected error creating {secret_name}: {e}")
            return False
    
    def update_secret(self, secret_name: str, secret_value: Dict[str, Any]) -> bool:
        """Update existing secret"""
        try:
            if self.is_development:
                logger.info(f"[SECRETS] Would update secret in production: {secret_name}")
                return True
            
            self.secrets_client.update_secret(
                SecretId=secret_name,
                SecretString=json.dumps(secret_value)
            )
            
            # Clear cache
            self.cache.clear()
            
            logger.info(f"[SECRETS] Updated secret: {secret_name}")
            return True
            
        except ClientError as e:
            logger.error(f"[SECRETS] Failed to update secret {secret_name}: {e}")
            return False
        except Exception as e:
            logger.error(f"[SECRETS] Unexpected error updating {secret_name}: {e}")
            return False
    
    def clear_cache(self):
        """Clear the secrets cache"""
        self.cache.clear()
        logger.info("[SECRETS] Cache cleared")

# Global secrets manager instance
secrets_manager = None

def get_secrets_manager() -> SecretsManager:
    """Get global secrets manager instance"""
    global secrets_manager
    if secrets_manager is None:
        secrets_manager = SecretsManager()
    return secrets_manager

def get_jwt_config() -> Dict[str, Any]:
    """Get JWT configuration from secrets"""
    secrets = get_secrets_manager()
    jwt_secrets = secrets.get_secret('ielts-genai-prep/jwt')
    
    if not jwt_secrets:
        raise RuntimeError("JWT secrets not available - check AWS Secrets Manager configuration")
    
    return {
        'SECRET_KEY': jwt_secrets['JWT_SECRET'],
        'ALGORITHM': jwt_secrets.get('JWT_ALGORITHM', 'HS256'),
        'ACCESS_TOKEN_EXPIRES_MINUTES': jwt_secrets.get('JWT_ACCESS_TOKEN_EXPIRES_MINUTES', 15)
    }

def get_qr_encryption_config() -> Dict[str, str]:
    """Get QR encryption configuration"""
    secrets = get_secrets_manager()
    qr_secrets = secrets.get_secret('ielts-genai-prep/qr-encryption')
    
    if not qr_secrets:
        raise RuntimeError("QR encryption secrets not available")
    
    return {
        'ENCRYPTION_KEY': qr_secrets['QR_ENCRYPTION_KEY'],
        'SIGNING_KEY': qr_secrets['QR_SIGNING_KEY']
    }

def get_apple_store_config() -> Dict[str, str]:
    """Get Apple App Store configuration"""
    secrets = get_secrets_manager()
    apple_secrets = secrets.get_secret('ielts-genai-prep/apple-store')
    
    if not apple_secrets:
        raise RuntimeError("Apple Store secrets not available")
    
    return apple_secrets

def get_google_play_config() -> Dict[str, str]:
    """Get Google Play Store configuration"""
    secrets = get_secrets_manager()
    google_secrets = secrets.get_secret('ielts-genai-prep/google-play')
    
    if not google_secrets:
        raise RuntimeError("Google Play secrets not available")
    
    return google_secrets

def get_recaptcha_config() -> Dict[str, str]:
    """Get reCAPTCHA configuration"""
    secrets = get_secrets_manager()
    recaptcha_secrets = secrets.get_secret('ielts-genai-prep/recaptcha')
    
    if not recaptcha_secrets:
        raise RuntimeError("reCAPTCHA secrets not available")
    
    return recaptcha_secrets

def get_kms_config() -> Dict[str, str]:
    """Get KMS encryption configuration"""
    secrets = get_secrets_manager()
    kms_secrets = secrets.get_secret('ielts-genai-prep/kms')
    
    if not kms_secrets:
        raise RuntimeError("KMS secrets not available")
    
    return kms_secrets

def validate_secrets_configuration():
    """Validate that all required secrets are available"""
    required_secrets = [
        'ielts-genai-prep/jwt',
        'ielts-genai-prep/qr-encryption', 
        'ielts-genai-prep/apple-store',
        'ielts-genai-prep/google-play',
        'ielts-genai-prep/recaptcha',
        'ielts-genai-prep/kms'
    ]
    
    secrets = get_secrets_manager()
    missing_secrets = []
    
    for secret_name in required_secrets:
        if not secrets.get_secret(secret_name):
            missing_secrets.append(secret_name)
    
    if missing_secrets:
        if secrets.is_development:
            logger.warning(f"[SECRETS] Missing secrets (using dev fallbacks): {missing_secrets}")
        else:
            raise RuntimeError(f"Required secrets missing: {missing_secrets}")
    else:
        logger.info("[SECRETS] All required secrets validated")
    
    return True