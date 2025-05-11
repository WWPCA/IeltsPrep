"""
Google Cloud Storage Integration
This module provides integration with Google Cloud Storage for scalable storage
of user data, transcripts, and assessment results. It is designed for GDPR compliance
and to support over 1 million users.
"""

import os
import json
import logging
import datetime
from flask import current_app, session
from google.cloud import storage
from google.oauth2 import service_account

# Configure logging
logger = logging.getLogger(__name__)

# Default bucket names
DEFAULT_BUCKET_NAME = "ielts-assessments-default"
EU_BUCKET_NAME = "ielts-assessments-eu"

# Storage class for different data types
TRANSCRIPT_STORAGE_CLASS = "STANDARD"  # Frequently accessed for 6 months
ASSESSMENT_STORAGE_CLASS = "NEARLINE"  # Less frequently accessed

# Retention periods
TRANSCRIPT_RETENTION_DAYS = 180  # 6 months retention for transcripts
ASSESSMENT_RETENTION_DAYS = None  # Keep assessments indefinitely (or until account deletion)

def _get_storage_client():
    """
    Initialize and return a Google Cloud Storage client.
    
    Returns:
        google.cloud.storage.Client: Authenticated storage client
    
    Raises:
        EnvironmentError: If credentials are missing
    """
    # Check if credentials are set
    credentials_json = os.environ.get('GCP_CREDENTIALS')
    
    if not credentials_json:
        # For development & testing, look for credentials file
        credentials_path = os.environ.get('GCP_CREDENTIALS_PATH')
        if credentials_path and os.path.exists(credentials_path):
            return storage.Client.from_service_account_json(credentials_path)
        else:
            # Log warning but don't fail - we'll use local storage as fallback
            logger.warning("GCP credentials not found - using local storage fallback")
            return None
    
    # Parse credentials JSON from environment variable
    try:
        credentials_info = json.loads(credentials_json)
        credentials = service_account.Credentials.from_service_account_info(credentials_info)
        return storage.Client(credentials=credentials)
    except Exception as e:
        logger.error(f"Error initializing GCP storage client: {str(e)}")
        return None

def _get_bucket_name(user_id=None, country_code=None):
    """
    Determine the appropriate bucket based on user location for data residency.
    
    Args:
        user_id (int, optional): User ID for reference
        country_code (str, optional): Country code for data residency
        
    Returns:
        str: Bucket name to use
    """
    # If no country code provided, try to get from session
    if not country_code and 'country_code' in session:
        country_code = session['country_code']
    
    # Get list of EU countries from country_restrictions.py
    from country_restrictions import EU_UK_COUNTRIES
    
    # Use EU bucket for EU users
    if country_code and country_code.upper() in EU_UK_COUNTRIES:
        return EU_BUCKET_NAME
    
    # Default bucket for other users
    return DEFAULT_BUCKET_NAME

def store_transcript(user_id, assessment_id, transcript_data, metadata=None):
    """
    Store a transcript in Google Cloud Storage with proper metadata and retention.
    
    Args:
        user_id (int): User ID
        assessment_id (int): Assessment attempt ID
        transcript_data (dict): Transcript data to store
        metadata (dict, optional): Additional metadata to store
        
    Returns:
        tuple: (success, storage_path or error_message)
    """
    # Get storage client
    client = _get_storage_client()
    if not client:
        logger.warning(f"Using local fallback for transcript storage (user_id: {user_id})")
        return (False, "GCP storage not available - using local fallback")
    
    try:
        # Determine bucket based on user's region
        bucket_name = _get_bucket_name(user_id)
        bucket = client.bucket(bucket_name)
        
        # Create blob path with privacy-focused structure (no PII in path)
        current_date = datetime.datetime.utcnow().strftime("%Y/%m/%d")
        blob_name = f"users/{user_id}/transcripts/{current_date}/{assessment_id}.json"
        blob = bucket.blob(blob_name)
        
        # Set storage class based on data type
        blob.storage_class = TRANSCRIPT_STORAGE_CLASS
        
        # Set content type and encoding
        blob.content_type = "application/json"
        blob.content_encoding = "utf-8"
        
        # Set basic metadata
        default_metadata = {
            "user_id": str(user_id),
            "assessment_id": str(assessment_id),
            "creation_date": datetime.datetime.utcnow().isoformat(),
            "content_type": "transcript",
            "retention_days": str(TRANSCRIPT_RETENTION_DAYS)
        }
        
        # Merge with any additional metadata
        if metadata:
            default_metadata.update(metadata)
        
        # Set metadata
        blob.metadata = default_metadata
        
        # Set retention policy if defined
        if TRANSCRIPT_RETENTION_DAYS:
            expiration = datetime.datetime.utcnow() + datetime.timedelta(days=TRANSCRIPT_RETENTION_DAYS)
            # Note: This requires bucket to have retention policy enabled
            # For GCP, we use object lifecycle configuration at bucket level
            # Add additional metadata for our own programmatic checks
            blob.metadata["expiration_date"] = expiration.isoformat()
        
        # Upload data
        blob.upload_from_string(
            data=json.dumps(transcript_data),
            content_type="application/json"
        )
        
        logger.info(f"Stored transcript in GCP: {blob_name}")
        return (True, blob_name)
    
    except Exception as e:
        error_msg = f"Error storing transcript in GCP: {str(e)}"
        logger.error(error_msg)
        return (False, error_msg)

def store_assessment(user_id, assessment_id, assessment_data, metadata=None):
    """
    Store assessment results in Google Cloud Storage with proper metadata.
    
    Args:
        user_id (int): User ID
        assessment_id (int): Assessment attempt ID
        assessment_data (dict): Assessment data to store
        metadata (dict, optional): Additional metadata to store
        
    Returns:
        tuple: (success, storage_path or error_message)
    """
    # Get storage client
    client = _get_storage_client()
    if not client:
        logger.warning(f"Using local fallback for assessment storage (user_id: {user_id})")
        return (False, "GCP storage not available - using local fallback")
    
    try:
        # Determine bucket based on user's region
        bucket_name = _get_bucket_name(user_id)
        bucket = client.bucket(bucket_name)
        
        # Create blob path with privacy-focused structure
        current_date = datetime.datetime.utcnow().strftime("%Y/%m/%d")
        blob_name = f"users/{user_id}/assessments/{current_date}/{assessment_id}.json"
        blob = bucket.blob(blob_name)
        
        # Set storage class based on data type
        blob.storage_class = ASSESSMENT_STORAGE_CLASS
        
        # Set content type and encoding
        blob.content_type = "application/json"
        blob.content_encoding = "utf-8"
        
        # Set basic metadata
        default_metadata = {
            "user_id": str(user_id),
            "assessment_id": str(assessment_id),
            "creation_date": datetime.datetime.utcnow().isoformat(),
            "content_type": "assessment"
        }
        
        # Add retention if defined
        if ASSESSMENT_RETENTION_DAYS:
            default_metadata["retention_days"] = str(ASSESSMENT_RETENTION_DAYS)
            expiration = datetime.datetime.utcnow() + datetime.timedelta(days=ASSESSMENT_RETENTION_DAYS)
            default_metadata["expiration_date"] = expiration.isoformat()
        
        # Merge with any additional metadata
        if metadata:
            default_metadata.update(metadata)
        
        # Set metadata
        blob.metadata = default_metadata
        
        # Upload data
        blob.upload_from_string(
            data=json.dumps(assessment_data),
            content_type="application/json"
        )
        
        logger.info(f"Stored assessment in GCP: {blob_name}")
        return (True, blob_name)
    
    except Exception as e:
        error_msg = f"Error storing assessment in GCP: {str(e)}"
        logger.error(error_msg)
        return (False, error_msg)

def retrieve_transcript(storage_path, user_id=None):
    """
    Retrieve a transcript from Google Cloud Storage.
    
    Args:
        storage_path (str): Storage path of the transcript
        user_id (int, optional): User ID for verification
        
    Returns:
        tuple: (success, transcript_data or error_message)
    """
    # Get storage client
    client = _get_storage_client()
    if not client:
        logger.warning(f"Using local fallback for transcript retrieval (path: {storage_path})")
        return (False, "GCP storage not available - using local fallback")
    
    try:
        # Extract bucket name from storage path if it's a full GCS URI
        if storage_path.startswith("gs://"):
            bucket_name, blob_name = storage_path[5:].split("/", 1)
        else:
            # Determine bucket based on user's region
            bucket_name = _get_bucket_name(user_id)
            blob_name = storage_path
        
        # Get bucket and blob
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        
        # Check if blob exists
        if not blob.exists():
            return (False, "Transcript not found")
        
        # Check permissions (if user_id provided)
        if user_id and blob.metadata and blob.metadata.get("user_id") != str(user_id):
            logger.warning(f"Unauthorized transcript access attempt: {user_id} tried to access {blob_name}")
            return (False, "Unauthorized access")
        
        # Check if expired
        if blob.metadata and "expiration_date" in blob.metadata:
            try:
                expiration = datetime.datetime.fromisoformat(blob.metadata["expiration_date"])
                if expiration < datetime.datetime.utcnow():
                    logger.info(f"Attempting to access expired transcript: {blob_name}")
                    return (False, "Transcript has expired")
            except ValueError:
                # If date parsing fails, continue (don't block access)
                pass
        
        # Download the blob
        content = blob.download_as_string()
        transcript_data = json.loads(content)
        
        return (True, transcript_data)
    
    except Exception as e:
        error_msg = f"Error retrieving transcript from GCP: {str(e)}"
        logger.error(error_msg)
        return (False, error_msg)

def retrieve_assessment(storage_path, user_id=None):
    """
    Retrieve assessment results from Google Cloud Storage.
    
    Args:
        storage_path (str): Storage path of the assessment
        user_id (int, optional): User ID for verification
        
    Returns:
        tuple: (success, assessment_data or error_message)
    """
    # Get storage client
    client = _get_storage_client()
    if not client:
        logger.warning(f"Using local fallback for assessment retrieval (path: {storage_path})")
        return (False, "GCP storage not available - using local fallback")
    
    try:
        # Extract bucket name from storage path if it's a full GCS URI
        if storage_path.startswith("gs://"):
            bucket_name, blob_name = storage_path[5:].split("/", 1)
        else:
            # Determine bucket based on user's region
            bucket_name = _get_bucket_name(user_id)
            blob_name = storage_path
        
        # Get bucket and blob
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        
        # Check if blob exists
        if not blob.exists():
            return (False, "Assessment not found")
        
        # Check permissions (if user_id provided)
        if user_id and blob.metadata and blob.metadata.get("user_id") != str(user_id):
            logger.warning(f"Unauthorized assessment access attempt: {user_id} tried to access {blob_name}")
            return (False, "Unauthorized access")
        
        # Check if expired
        if blob.metadata and "expiration_date" in blob.metadata:
            try:
                expiration = datetime.datetime.fromisoformat(blob.metadata["expiration_date"])
                if expiration < datetime.datetime.utcnow():
                    logger.info(f"Attempting to access expired assessment: {blob_name}")
                    return (False, "Assessment has expired")
            except ValueError:
                # If date parsing fails, continue (don't block access)
                pass
        
        # Download the blob
        content = blob.download_as_string()
        assessment_data = json.loads(content)
        
        return (True, assessment_data)
    
    except Exception as e:
        error_msg = f"Error retrieving assessment from GCP: {str(e)}"
        logger.error(error_msg)
        return (False, error_msg)

def delete_user_data(user_id):
    """
    Delete all data for a specific user (for GDPR compliance).
    
    Args:
        user_id (int): User ID to delete data for
        
    Returns:
        tuple: (success, message)
    """
    # Get storage client
    client = _get_storage_client()
    if not client:
        logger.warning(f"GCP storage not available for user data deletion (user_id: {user_id})")
        return (False, "GCP storage not available - data may still exist in cloud storage")
    
    try:
        deleted_count = 0
        error_count = 0
        
        # Get buckets
        buckets = [DEFAULT_BUCKET_NAME, EU_BUCKET_NAME]
        
        for bucket_name in buckets:
            bucket = client.bucket(bucket_name)
            
            # List all user's objects (transcripts and assessments)
            # The prefix ensures we only get this user's data
            prefix = f"users/{user_id}/"
            blobs = bucket.list_blobs(prefix=prefix)
            
            # Delete each blob
            for blob in blobs:
                try:
                    blob.delete()
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"Error deleting blob {blob.name}: {str(e)}")
                    error_count += 1
        
        message = f"Deleted {deleted_count} objects for user {user_id}."
        if error_count > 0:
            message += f" Failed to delete {error_count} objects."
        
        logger.info(message)
        return (True, message)
    
    except Exception as e:
        error_msg = f"Error deleting user data from GCP: {str(e)}"
        logger.error(error_msg)
        return (False, error_msg)

def is_available():
    """
    Check if GCP storage is available and properly configured.
    
    Returns:
        bool: True if GCP storage is available
    """
    client = _get_storage_client()
    return client is not None

# Initialize on module load to catch any issues early
logger.info("Initializing GCP Storage module...")
if is_available():
    logger.info("GCP Storage is available and configured")
else:
    logger.warning("GCP Storage is not available - using local fallbacks")