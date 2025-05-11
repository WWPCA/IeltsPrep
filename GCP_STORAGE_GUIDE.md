# GCP Storage Integration Guide

This guide explains how the Google Cloud Platform (GCP) Cloud Storage integration works and how to manage it.

## Overview

Our IELTS platform now uses GCP Cloud Storage to store user transcripts and assessments. This provides:

- **Scalability**: Support for over 1 million users
- **Privacy compliance**: Automatic transcript lifecycle management
- **Cost-efficiency**: Better pricing than AWS S3
- **Reliability**: Automatic fallback to local storage when GCP is unavailable

## Setup Instructions

1. **Create a GCP Service Account**:
   - Navigate to Google Cloud Console
   - Create a new service account with the "Storage Object Admin" role
   - Download the service account credentials JSON file

2. **Set Environment Variables**:
   ```
   # Option 1: Set the JSON content directly
   export GCP_CREDENTIALS='{"type":"service_account","project_id":"your-project-id",...}'
   
   # Option 2: Set path to credentials file
   export GCP_CREDENTIALS_PATH='/path/to/credentials.json'
   ```

3. **Create GCP Storage Buckets**:
   - Create a default bucket named `ielts-assessments-default`
   - Create an EU bucket named `ielts-assessments-eu` in an EU region
   - Set lifecycle rules on both buckets:
     - Delete objects with prefix `users/*/transcripts` after 180 days
     - Retain objects with prefix `users/*/assessments` indefinitely

4. **Run the Database Migration**:
   ```
   python run_gcp_migration.py
   ```

## Data Lifecycle Management

### Transcript Retention (6 months)

Transcripts are stored for 6 months and then automatically deleted:

1. **Automatic Deletion**:
   - Set up a cron job to run `cleanup_expired_transcripts.py` daily
   - Example: `0 0 * * * python /path/to/cleanup_expired_transcripts.py`

2. **Manual Cleanup**:
   ```
   python cleanup_expired_transcripts.py
   ```

### User Data Deletion (GDPR)

When a user requests account deletion (right to be forgotten):

```
# Delete only cloud data
python delete_user_data.py USER_ID

# Complete deletion (including database records)
python delete_user_data.py USER_ID --delete-user
```

## Fallback Mechanism

If GCP is unavailable, the system automatically falls back to storing data in the database:

1. Transcripts and assessments are stored in the database columns
2. When GCP becomes available again, new data will use cloud storage
3. No migration of existing data is performed automatically

## Monitoring

Logs from GCP storage operations are written to:
- `transcript_cleanup.log`: For transcript lifecycle operations
- `user_data_deletion.log`: For user data deletion operations

Standard application logs also include GCP operation results.

## Privacy and Consent

The system includes:

1. **Privacy Notice**: Displayed before speaking tests
2. **Consent Checkbox**: Required before recording
3. **Expiry Information**: Shows when transcripts will be deleted
4. **No Audio Storage**: Audio recordings are only used for immediate assessment

## Troubleshooting

1. **GCP Credentials Issue**:
   - Verify environment variables are set
   - Check service account permissions

2. **Storage Access Errors**:
   - Ensure buckets exist with correct names
   - Check object permissions

3. **Missing Transcripts**:
   - Check if the transcript has expired (after 6 months)
   - Verify GCP credentials and bucket access