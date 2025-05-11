"""
Delete User Data

This script provides a utility to delete all data for a specific user,
supporting GDPR compliance and user's right to be forgotten.

It removes:
1. All GCP stored transcripts and assessments
2. Transcript data from database records
3. Optionally, can completely delete user records
"""

import os
import logging
import sys
import json
import argparse
from datetime import datetime
from app import app, db
from models import User, UserTestAttempt
import gcp_storage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('user_data_deletion.log')
    ]
)
logger = logging.getLogger(__name__)

def delete_user_cloud_data(user_id):
    """
    Delete all cloud storage data for a user
    
    Args:
        user_id (int): The user ID
    
    Returns:
        bool: True if deletion was successful
    """
    try:
        if gcp_storage.is_available():
            success, message = gcp_storage.delete_user_data(user_id)
            if success:
                logger.info(f"GCP data deletion successful for user {user_id}: {message}")
                return True
            else:
                logger.error(f"GCP data deletion failed for user {user_id}: {message}")
                return False
        else:
            logger.warning(f"GCP storage not available, skipping cloud data deletion for user {user_id}")
            return True  # Consider it successful if GCP is not in use
    except Exception as e:
        logger.error(f"Error deleting user cloud data: {str(e)}")
        return False

def delete_transcript_data(user_id):
    """
    Delete transcript data from the database for a user
    
    Args:
        user_id (int): The user ID
    
    Returns:
        bool: True if deletion was successful
    """
    try:
        with app.app_context():
            # Get all attempts for this user
            attempts = UserTestAttempt.query.filter_by(user_id=user_id).all()
            
            if not attempts:
                logger.info(f"No test attempts found for user {user_id}")
                return True
            
            logger.info(f"Removing transcript data from {len(attempts)} test attempts for user {user_id}")
            
            for attempt in attempts:
                # Update user_answers to remove transcription
                user_answers = attempt.user_answers
                
                # Remove transcription from user_answers if present
                if 'transcription' in user_answers:
                    user_answers.pop('transcription')
                    attempt.user_answers = user_answers
                
                # Clear GCP paths and expiry date
                attempt.gcp_transcript_path = None
                attempt.gcp_assessment_path = None
                attempt.transcript_expiry_date = None
            
            # Commit all changes
            db.session.commit()
            
            logger.info(f"Successfully removed transcript data for user {user_id}")
            return True
    
    except Exception as e:
        logger.error(f"Error deleting transcript data: {str(e)}")
        return False

def fully_delete_user_data(user_id, confirm=False):
    """
    Completely delete a user and all associated records
    
    Args:
        user_id (int): The user ID
        confirm (bool): Confirmation flag to prevent accidental deletion
    
    Returns:
        bool: True if deletion was successful
    """
    if not confirm:
        logger.warning(f"Full user deletion requires confirmation. Set confirm=True to proceed.")
        return False
    
    try:
        with app.app_context():
            # Get the user
            user = User.query.get(user_id)
            
            if not user:
                logger.error(f"User {user_id} not found")
                return False
            
            # First, delete from GCP
            delete_user_cloud_data(user_id)
            
            # Now delete all related records and the user
            # This assumes cascade deletion is set up in the database
            # If not, you would need to manually delete all related records
            
            # Delete user test attempts
            attempts = UserTestAttempt.query.filter_by(user_id=user_id).all()
            for attempt in attempts:
                db.session.delete(attempt)
            
            # Delete the user
            db.session.delete(user)
            
            # Commit the changes
            db.session.commit()
            
            logger.info(f"User {user_id} and all associated data successfully deleted")
            return True
    
    except Exception as e:
        logger.error(f"Error during full user deletion: {str(e)}")
        return False

def run_user_data_deletion(user_id, delete_cloud=True, delete_transcripts=True, delete_user=False):
    """
    Run the user data deletion process
    
    Args:
        user_id (int): The user ID
        delete_cloud (bool): Whether to delete cloud data
        delete_transcripts (bool): Whether to delete transcript data from DB
        delete_user (bool): Whether to completely delete the user
    
    Returns:
        bool: True if all requested operations were successful
    """
    logger.info(f"Starting data deletion for user {user_id}")
    success = True
    
    # Check if user exists
    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            logger.error(f"User {user_id} not found")
            return False
    
    # Delete cloud data if requested
    if delete_cloud:
        cloud_success = delete_user_cloud_data(user_id)
        success = success and cloud_success
    
    # Delete transcript data if requested
    if delete_transcripts:
        transcript_success = delete_transcript_data(user_id)
        success = success and transcript_success
    
    # Fully delete user if requested
    if delete_user:
        user_success = fully_delete_user_data(user_id, confirm=True)
        success = success and user_success
    
    if success:
        logger.info(f"All requested data deletion operations completed successfully for user {user_id}")
    else:
        logger.warning(f"Some data deletion operations failed for user {user_id}")
    
    return success

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Delete user data for GDPR compliance')
    parser.add_argument('user_id', type=int, help='The ID of the user')
    parser.add_argument('--skip-cloud', action='store_true', help='Skip cloud data deletion')
    parser.add_argument('--skip-transcripts', action='store_true', help='Skip transcript data deletion')
    parser.add_argument('--delete-user', action='store_true', help='Completely delete the user (use with caution)')
    
    args = parser.parse_args()
    
    run_user_data_deletion(
        args.user_id,
        delete_cloud=not args.skip_cloud,
        delete_transcripts=not args.skip_transcripts,
        delete_user=args.delete_user
    )