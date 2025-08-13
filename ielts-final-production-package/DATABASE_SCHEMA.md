# DynamoDB Database Schema Documentation

## Production Tables

### 1. ielts-genai-prep-users
**Primary Table for User Management**
```json
{
  "email": "user@example.com",  // Primary Key
  "user_id": "uuid-string",
  "password_hash": "bcrypt-hash",
  "first_name": "John",
  "last_name": "Doe", 
  "registration_date": "2025-08-13T14:00:00Z",
  "is_verified": true,
  "profile_image_url": "https://...",
  "assessment_attempts": {
    "academic_writing": 4,
    "general_writing": 4,
    "academic_speaking": 4,
    "general_speaking": 4
  },
  "purchased_assessments": ["academic_writing", "general_writing"],
  "last_login": "2025-08-13T14:00:00Z",
  "account_status": "active",
  "mobile_app_user_id": "app-specific-id",
  "subscription_status": "active",
  "gdpr_consent": true,
  "data_export_requests": [],
  "account_deletion_requested": false
}
```

### 2. ielts-genai-prep-sessions
**Session Management with TTL**
```json
{
  "session_id": "session-uuid",  // Primary Key
  "user_id": "user-uuid",
  "email": "user@example.com",
  "created_at": 1723556417,
  "expires_at": 1723642817,  // TTL field
  "device_info": "Mobile App",
  "ip_address": "192.168.1.1",
  "is_mobile_session": true,
  "qr_code_session": false
}
```

### 3. ielts-genai-prep-assessments
**Assessment Results and History**
```json
{
  "assessment_id": "assessment-uuid",  // Primary Key
  "user_id": "user-uuid",
  "assessment_type": "academic_writing",
  "status": "completed",
  "started_at": "2025-08-13T14:00:00Z",
  "completed_at": "2025-08-13T14:30:00Z",
  "question_data": {
    "prompt": "Some people think...",
    "type": "essay",
    "difficulty": "band_7"
  },
  "user_response": "User's essay text...",
  "ai_feedback": {
    "overall_band": 7.0,
    "task_achievement": 7,
    "coherence_cohesion": 7,
    "lexical_resource": 6,
    "grammatical_range": 7,
    "feedback_text": "Detailed feedback...",
    "improvement_suggestions": ["suggestion1", "suggestion2"]
  },
  "voice_recording_processed": true,  // For speaking assessments
  "nova_sonic_conversation_id": "conversation-id"  // For speaking assessments
}
```

### 4. ielts-genai-prep-questions
**Question Bank for Assessments**
```json
{
  "question_id": "question-uuid",  // Primary Key
  "question_type": "academic_writing_task2",
  "difficulty_level": "band_7",
  "prompt": "Some people believe that...",
  "sample_response": "High-band sample answer...",
  "assessment_criteria": {
    "task_achievement": "Criteria description",
    "coherence_cohesion": "Criteria description",
    "lexical_resource": "Criteria description", 
    "grammatical_range": "Criteria description"
  },
  "created_date": "2025-08-13",
  "is_active": true,
  "usage_count": 1250,
  "region": "us-east-1"
}
```

### 5. ielts-genai-prep-purchases
**In-App Purchase Validation**
```json
{
  "purchase_id": "purchase-uuid",  // Primary Key
  "user_id": "user-uuid",
  "product_id": "academic_writing_assessment",
  "platform": "ios",  // ios, android
  "transaction_id": "platform-transaction-id",
  "receipt_data": "base64-encoded-receipt",
  "purchase_date": "2025-08-13T14:00:00Z",
  "validation_status": "verified",
  "attempts_granted": 4,
  "attempts_used": 0,
  "expires_at": null,  // null for non-consumable
  "refund_status": "none"
}
```

### 6. ielts-genai-prep-qr-auth
**QR Code Authentication**
```json
{
  "qr_code_id": "qr-uuid",  // Primary Key
  "user_id": "user-uuid",
  "device_fingerprint": "device-hash",
  "created_at": 1723556417,
  "expires_at": 1723556717,  // TTL: 5 minutes
  "status": "pending",  // pending, verified, expired
  "mobile_session_id": "mobile-session-uuid",
  "web_session_id": "web-session-uuid",
  "ip_address": "192.168.1.1"
}
```

### 7. ielts-genai-prep-gdpr
**GDPR Compliance Data**
```json
{
  "request_id": "gdpr-uuid",  // Primary Key
  "user_id": "user-uuid",
  "request_type": "data_export",  // data_export, data_deletion
  "status": "pending",  // pending, processing, completed
  "requested_at": "2025-08-13T14:00:00Z",
  "completed_at": null,
  "data_location": "s3://bucket/export-file.json",
  "verification_code": "6-digit-code",
  "expires_at": 1723642817  // TTL field
}
```

## Global Secondary Indexes (GSI)

### User Lookup by User ID
- **Index Name**: user-id-index
- **Partition Key**: user_id
- **Projection**: ALL

### Assessment History by User
- **Index Name**: user-assessments-index  
- **Partition Key**: user_id
- **Sort Key**: completed_at
- **Projection**: ALL

### Purchase History by User
- **Index Name**: user-purchases-index
- **Partition Key**: user_id
- **Sort Key**: purchase_date
- **Projection**: ALL

## AWS Mock Configuration

The `aws_mock_config.py` provides local development simulation of:
- **DynamoDB Operations**: PUT, GET, DELETE, UPDATE, SCAN
- **TTL Management**: Automatic cleanup of expired items
- **Cross-Table Relationships**: User sessions, assessments, purchases
- **IELTS Assessment Rubrics**: Pre-loaded question banks
- **GDPR Compliance**: Data export/deletion workflows

## Production Environment Variables

Required for Lambda function:
```
DYNAMODB_TABLE_PREFIX=ielts-genai-prep
ENVIRONMENT=production
RECAPTCHA_V2_SITE_KEY=your-site-key
RECAPTCHA_V2_SECRET_KEY=your-secret-key
BEDROCK_REGION=us-east-1
SES_REGION=us-east-1
```

## Data Flow Architecture

1. **Mobile Registration** → DynamoDB Users Table
2. **Purchase Validation** → DynamoDB Purchases Table  
3. **QR Authentication** → DynamoDB QR-Auth Table
4. **Assessment Execution** → DynamoDB Assessments Table
5. **GDPR Requests** → DynamoDB GDPR Table
6. **Session Management** → DynamoDB Sessions Table (TTL enabled)

## Backup and Recovery

- **Point-in-Time Recovery**: Enabled for all production tables
- **Global Tables**: Multi-region replication (us-east-1, eu-west-1, ap-southeast-1)
- **DynamoDB Streams**: Enabled for audit logging
- **CloudWatch Monitoring**: Automated alerts for capacity and errors