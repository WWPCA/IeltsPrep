"""
Google Cloud Storage Configuration for IELTS AI Prep
This module provides GCP Cloud Storage connectivity and file management.
"""

import os
import logging
from typing import Optional, Tuple, Dict, Any
from google.cloud import storage
from google.cloud.exceptions import NotFound


class CloudStorageClient:
    """Client for interacting with Google Cloud Storage"""
    
    def __init__(self):
        """Initialize the Cloud Storage client"""
        try:
            self.client = storage.Client()
            self.media_bucket_name = os.environ.get("GCP_STORAGE_BUCKET", "ielts-ai-prep-media")
            self.transcripts_bucket_name = os.environ.get("GCP_TRANSCRIPTS_BUCKET", "ielts-ai-prep-transcripts")
            self.initialized = True
            logging.info(f"Cloud Storage initialized with buckets: {self.media_bucket_name}, {self.transcripts_bucket_name}")
        except Exception as e:
            self.initialized = False
            logging.error(f"Failed to initialize Cloud Storage: {e}")
    
    def upload_file(self, source_file_path: str, destination_blob_name: str, 
                    bucket_name: Optional[str] = None, 
                    metadata: Optional[Dict[str, str]] = None) -> Tuple[bool, str]:
        """
        Upload a file to Google Cloud Storage
        
        Args:
            source_file_path: Local file path to upload
            destination_blob_name: Destination path in the bucket
            bucket_name: Name of the bucket (defaults to media bucket)
            metadata: Optional metadata to attach to the file
            
        Returns:
            Tuple of (success status, public URL or error message)
        """
        if not self.initialized:
            return False, "Cloud Storage client not initialized"
        
        bucket_name = bucket_name or self.media_bucket_name
        
        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(destination_blob_name)
            
            # Set metadata if provided
            if metadata:
                blob.metadata = metadata
            
            # Upload the file
            blob.upload_from_filename(source_file_path)
            
            # Return the public URL if it's in the media bucket
            if bucket_name == self.media_bucket_name:
                return True, f"https://storage.googleapis.com/{bucket_name}/{destination_blob_name}"
            else:
                return True, f"File uploaded successfully to {bucket_name}/{destination_blob_name}"
                
        except Exception as e:
            logging.error(f"Error uploading to Cloud Storage: {e}")
            return False, str(e)
    
    def download_file(self, source_blob_name: str, destination_file_path: str,
                      bucket_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        Download a file from Google Cloud Storage
        
        Args:
            source_blob_name: Source path in the bucket
            destination_file_path: Local file path for download
            bucket_name: Name of the bucket (defaults to media bucket)
            
        Returns:
            Tuple of (success status, status message or error message)
        """
        if not self.initialized:
            return False, "Cloud Storage client not initialized"
        
        bucket_name = bucket_name or self.media_bucket_name
        
        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(source_blob_name)
            
            # Download the file
            blob.download_to_filename(destination_file_path)
            
            return True, f"File downloaded successfully to {destination_file_path}"
                
        except NotFound:
            return False, f"File {source_blob_name} not found in bucket {bucket_name}"
        except Exception as e:
            logging.error(f"Error downloading from Cloud Storage: {e}")
            return False, str(e)
    
    def delete_file(self, blob_name: str, bucket_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        Delete a file from Google Cloud Storage
        
        Args:
            blob_name: Path of the file in the bucket
            bucket_name: Name of the bucket (defaults to media bucket)
            
        Returns:
            Tuple of (success status, status message or error message)
        """
        if not self.initialized:
            return False, "Cloud Storage client not initialized"
        
        bucket_name = bucket_name or self.media_bucket_name
        
        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            
            # Delete the file
            blob.delete()
            
            return True, f"File {blob_name} deleted successfully from {bucket_name}"
                
        except NotFound:
            return False, f"File {blob_name} not found in bucket {bucket_name}"
        except Exception as e:
            logging.error(f"Error deleting from Cloud Storage: {e}")
            return False, str(e)
    
    def get_signed_url(self, blob_name: str, bucket_name: Optional[str] = None, 
                      expiration_minutes: int = 60) -> Tuple[bool, str]:
        """
        Generate a signed URL for temporary access to a private file
        
        Args:
            blob_name: Path of the file in the bucket
            bucket_name: Name of the bucket (defaults to transcripts bucket)
            expiration_minutes: URL expiration time in minutes
            
        Returns:
            Tuple of (success status, signed URL or error message)
        """
        if not self.initialized:
            return False, "Cloud Storage client not initialized"
        
        bucket_name = bucket_name or self.transcripts_bucket_name
        
        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            
            # Generate signed URL with expiration
            url = blob.generate_signed_url(
                version="v4",
                expiration=expiration_minutes * 60,  # Convert to seconds
                method="GET"
            )
            
            return True, url
                
        except NotFound:
            return False, f"File {blob_name} not found in bucket {bucket_name}"
        except Exception as e:
            logging.error(f"Error generating signed URL: {e}")
            return False, str(e)


# Global instance for easy import
cloud_storage = CloudStorageClient()