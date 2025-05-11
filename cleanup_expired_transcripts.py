"""
Cleanup Expired Transcripts

This script automatically cleans up expired transcripts from both
GCP storage and database. It follows the 6-month retention policy
for speaking test transcripts.

This script should be run regularly as a cron job to ensure proper
privacy compliance and storage efficiency.
"""

import os
import logging
import sys
from datetime import datetime, timedelta
from app import app, db
from models import UserTestAttempt
import gcp_storage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('transcript_cleanup.log')
    ]
)
logger = logging.getLogger(__name__)

def find_expired_transcripts():
    """
    Find all transcripts that have expired (older than 6 months)
    
    Returns:
        list: List of UserTestAttempt objects with expired transcripts
    """
    try:
        with app.app_context():
            # Find records with transcript_expiry_date in the past
            current_time = datetime.utcnow()
            expired_attempts = UserTestAttempt.query.filter(
                UserTestAttempt.transcript_expiry_date.isnot(None),
                UserTestAttempt.transcript_expiry_date < current_time,
                UserTestAttempt.gcp_transcript_path.isnot(None)
            ).all()
            
            logger.info(f"Found {len(expired_attempts)} expired transcripts")
            return expired_attempts
    except Exception as e:
        logger.error(f"Error finding expired transcripts: {str(e)}")
        return []

def cleanup_transcript(attempt):
    """
    Clean up a single expired transcript
    
    Args:
        attempt (UserTestAttempt): The attempt with the expired transcript
    
    Returns:
        bool: True if cleanup was successful
    """
    try:
        # First, try to delete from GCP storage if available
        if gcp_storage.is_available():
            # Get the GCP path
            gcp_path = attempt.gcp_transcript_path
            
            if gcp_path:
                # The delete_user_data function deletes all data for a user
                # We need to delete just this specific transcript
                # Extract bucket and blob name from the path
                try:
                    from google.cloud import storage
                    client = gcp_storage._get_storage_client()
                    
                    if client:
                        # If it's a full GCS URI, parse accordingly
                        if gcp_path.startswith("gs://"):
                            bucket_name, blob_name = gcp_path[5:].split("/", 1)
                        else:
                            # Use default bucket and path as is
                            bucket_name = gcp_storage._get_bucket_name(attempt.user_id)
                            blob_name = gcp_path
                        
                        # Get bucket and blob
                        bucket = client.bucket(bucket_name)
                        blob = bucket.blob(blob_name)
                        
                        # Delete the blob if it exists
                        if blob.exists():
                            blob.delete()
                            logger.info(f"Deleted GCP transcript: {gcp_path}")
                        else:
                            logger.warning(f"GCP transcript not found: {gcp_path}")
                except Exception as gcp_error:
                    logger.error(f"Error deleting GCP transcript: {str(gcp_error)}")
        
        # Now update the database record
        with app.app_context():
            # Update user_answers to remove transcription
            user_answers = attempt.user_answers
            
            # Remove transcription from user_answers if present
            if 'transcription' in user_answers:
                user_answers.pop('transcription')
                attempt.user_answers = user_answers
            
            # Clear GCP transcript path and expiry date
            attempt.gcp_transcript_path = None
            attempt.transcript_expiry_date = None
            
            # Commit changes
            db.session.commit()
            
            logger.info(f"Cleaned up transcript for attempt ID {attempt.id} (User ID: {attempt.user_id})")
            return True
    
    except Exception as e:
        logger.error(f"Error cleaning up transcript for attempt ID {attempt.id}: {str(e)}")
        return False

def run_cleanup():
    """Run the transcript cleanup process"""
    logger.info("Starting transcript cleanup process...")
    
    # Find expired transcripts
    expired_attempts = find_expired_transcripts()
    
    if not expired_attempts:
        logger.info("No expired transcripts found.")
        return
    
    success_count = 0
    failure_count = 0
    
    # Process each expired transcript
    for attempt in expired_attempts:
        try:
            success = cleanup_transcript(attempt)
            if success:
                success_count += 1
            else:
                failure_count += 1
        except Exception as e:
            logger.error(f"Unexpected error cleaning up transcript for attempt ID {attempt.id}: {str(e)}")
            failure_count += 1
    
    logger.info(f"Transcript cleanup complete. Successes: {success_count}, Failures: {failure_count}")

if __name__ == "__main__":
    run_cleanup()