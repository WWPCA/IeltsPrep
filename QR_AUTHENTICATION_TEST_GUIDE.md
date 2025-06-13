# QR Code Authentication System - .replit Test Guide

## Overview
This document outlines the QR code authentication system implemented for the IELTS GenAI Prep application. The system restricts website access and requires mobile app authentication via QR codes before users can view their assessments.

## Architecture
- **Frontend**: Static HTML/CSS/JS files served by Flask
- **Backend**: Local test endpoints that simulate AWS Lambda functionality
- **Storage**: In-memory storage for tokens and sessions (simulates DynamoDB/ElastiCache)
- **Authentication**: QR token-based with 10-minute expiration and single-use tokens

## Test Flow

### 1. Mobile App Purchase Simulation
Navigate to `/test-mobile` to simulate the mobile app purchase flow:

1. **Purchase Process**:
   - Select any assessment module ($36 each)
   - Click "Purchase Assessment"
   - System simulates Apple/Google purchase verification
   - QR token is automatically generated after successful purchase

2. **QR Token Generation**:
   - Token expires in 10 minutes
   - Single-use token (cannot be reused)
   - Token is displayed for manual copy/paste testing

### 2. Website Authentication
Navigate to `/` (root) to access the QR login page:

1. **QR Scanner Method**:
   - Allow camera permissions
   - Scan QR code from mobile app (not available in .replit environment)

2. **Manual Token Entry** (for .replit testing):
   - Copy token from mobile simulator
   - Paste into "Manual Token Entry" field
   - Click "Verify Token"

### 3. Assessment Access
After successful authentication:
- Automatic redirect to `/assessments`
- Display sample assessment data for `test@ieltsaiprep.com`
- Session stored in localStorage for 1 hour
- Text-only assessments displayed (no audio data)

## API Endpoints

### `/api/auth/generate-qr` (POST)
Generates QR authentication token after purchase verification.

**Request Body**:
```json
{
  "user_email": "test@ieltsaiprep.com",
  "purchase_verified": true,
  "assessment_type": "academic_speaking"
}
```

**Response**:
```json
{
  "success": true,
  "token_id": "uuid-string",
  "qr_data": "{\"token\":\"uuid\",\"domain\":\"ieltsaiprep.com\",\"timestamp\":1234567890}",
  "expires_in_minutes": 10,
  "expires_at": "2024-12-01T10:10:00Z"
}
```

### `/auth/verify-qr` (POST)
Verifies QR token and creates website session.

**Request Body**:
```json
{
  "token": "uuid-string"
}
```

**Response**:
```json
{
  "success": true,
  "user_email": "test@ieltsaiprep.com",
  "session_id": "session_1234567890_uuid",
  "message": "Authentication successful",
  "redirect_url": "/assessments"
}
```

### `/api/assessment/<user_email>` (GET)
Retrieves user assessments (requires valid session).

**Headers**:
```
Authorization: Bearer session_1234567890_uuid
```

**Response**:
```json
{
  "success": true,
  "assessments": [
    {
      "assessment_id": "test_speaking_1",
      "assessment_type": "academic_speaking",
      "created_at": "2024-12-01T10:00:00Z",
      "transcript": "User discussed education systems...",
      "feedback": "Excellent pronunciation...",
      "score": 7.5
    }
  ],
  "total_count": 1
}
```

## Security Features

### Token Security
- **Expiration**: 10-minute lifetime
- **Single-use**: Tokens marked as used after verification
- **Domain validation**: Tokens tied to 'ieltsaiprep.com'
- **Timestamp validation**: Prevents replay attacks

### Session Management
- **Duration**: 1-hour session lifetime
- **Storage**: localStorage for frontend persistence
- **Validation**: Session verified on each API call
- **Auto-cleanup**: Expired sessions automatically removed

## Testing Instructions

### Complete Test Flow
1. **Start**: Navigate to `/test-mobile`
2. **Purchase**: Click any "Purchase Assessment" button
3. **Copy Token**: Copy the generated QR token
4. **Login**: Navigate to `/` and paste token in manual entry field
5. **Verify**: Click "Verify Token"
6. **Access**: Automatically redirected to `/assessments`
7. **View Data**: Sample assessments displayed for test user

### Expected Results
- ✅ Purchase simulation completes successfully
- ✅ QR token generated with 10-minute expiration
- ✅ Token verification succeeds on first use
- ✅ Token rejection on second use attempt
- ✅ Session creation and persistence
- ✅ Assessment data retrieval and display
- ✅ Session expiration after 1 hour

### Error Scenarios
- ❌ Invalid token: "Invalid token" error
- ❌ Expired token: "Token expired" error
- ❌ Used token: "Token already used" error
- ❌ No session: Redirect to login page
- ❌ Expired session: "Session expired" error

## Production Deployment Notes

When deploying to AWS:
1. Replace test endpoints with actual Lambda functions
2. Use real DynamoDB tables instead of in-memory storage
3. Use ElastiCache/Redis for session management
4. Update frontend URLs to point to API Gateway endpoints
5. Implement proper error handling and logging to CloudWatch

## Lambda Integration

The `lambda_handler.py` file contains the production-ready Lambda functions:
- `_handle_qr_generation()`: QR token generation
- `_handle_qr_verification()`: QR token verification
- `_handle_assessment_access()`: Assessment retrieval with session validation
- `_create_qr_session()`: Session creation
- `_verify_qr_session()`: Session validation

## Mobile App Integration

The mobile app (`mobile_purchase_integration.js`) includes:
- `generateQRCodeForWebsite()`: QR generation after purchase
- `showQRCodeModal()`: QR code display to user
- Purchase verification with Apple/Google app stores
- Toast notifications for user feedback

## Files Modified/Created

### Core System Files
- `lambda_handler.py`: Added QR authentication endpoints
- `main.py`: Local test server with QR endpoints
- `mobile_purchase_integration.js`: Added QR generation to purchase flow

### Frontend Templates
- `templates/qr_login.html`: QR scanner and manual token entry
- `templates/assessments.html`: Protected assessments page
- `templates/test_mobile.html`: Mobile purchase simulator

### Documentation
- `QR_AUTHENTICATION_TEST_GUIDE.md`: This comprehensive guide

The system is now ready for testing in the .replit environment before AWS deployment.