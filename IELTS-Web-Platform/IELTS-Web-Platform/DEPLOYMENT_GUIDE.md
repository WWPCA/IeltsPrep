# IELTS GenAI Prep Backend Deployment Guide

## Prerequisites

### 1. AWS CLI Configuration
```bash
aws configure
# Enter your WWP user credentials
# Access Key ID: [Your Access Key]
# Secret Access Key: [Your Secret Key]
# Default region: us-east-1
# Default output format: json
```

### 2. Install Serverless Framework
```bash
npm install -g serverless
npm install -g serverless-python-requirements
npm install -g serverless-domain-manager
```

### 3. Python Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Deployment Steps

### 1. Configure Environment Variables
Create `.env` file:
```bash
JWT_SECRET=your-super-secure-jwt-secret-key-here
GOOGLE_PLAY_SERVICE_ACCOUNT_KEY=/path/to/google-service-account.json
APPLE_SHARED_SECRET=your-apple-shared-secret
```

### 2. Verify DynamoDB Tables
Your existing tables should match these schemas:

#### ielts-genai-prep-users
- Primary Key: `email` (String)
- Attributes: `user_id`, `password_hash`, `created_at`, `last_login`, `subscription_status`, `assessments_remaining`

#### ielts-genai-prep-assessments  
- Primary Key: `assessment_id` (String)
- GSI: `user_id-index` (user_id as partition key)
- Attributes: `user_id`, `assessment_type`, `submission_data`, `ai_feedback`, `created_at`

#### ielts-genai-prep-auth-tokens
- Primary Key: `user_id` (String)
- TTL: `expires_at`
- Attributes: `access_token`, `refresh_token`, `created_at`

### 3. Deploy Backend Services

#### Development Deployment
```bash
cd backend/deployment
serverless deploy --stage dev
```

#### Production Deployment
```bash
serverless deploy --stage prod
```

### 4. Configure Custom Domain (Optional)
```bash
serverless create_domain --stage prod
serverless deploy --stage prod
```

### 5. Test Deployment
```bash
# Test health endpoint
curl https://api.ieltsaiprep.com/api/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "services": {
    "dynamodb": "active",
    "lambda": "active"
  }
}
```

## API Endpoints

### Authentication
- `POST /api/register` - User registration
- `POST /api/login` - User login
- `POST /api/mobile-login` - Mobile-specific login
- `POST /api/validate-token` - Token validation
- `POST /api/account-deletion` - GDPR account deletion
- `GET /api/health` - Health check

### Purchase Verification
- `POST /purchase/verify/google` - Google Play purchase verification
- `POST /purchase/verify/apple` - Apple App Store purchase verification
- `POST /api/verify-purchase` - General purchase verification

### Nova AI Services
- `POST /api/nova-sonic-connect` - Test Nova Sonic connection
- `POST /api/nova-sonic-stream` - Real-time speech processing
- `POST /api/nova-micro/writing` - Writing assessment
- `POST /api/nova-micro-assessment` - Alternative writing endpoint
- `POST /api/maya/introduction` - Maya AI introduction
- `POST /api/maya/conversation` - Maya conversation management

### Assessment Management
- `GET /assessment/academic-writing` - Get writing questions
- `GET /assessment/general-writing` - Get writing questions
- `GET /assessment/academic-speaking` - Get speaking questions
- `GET /assessment/general-speaking` - Get speaking questions
- `POST /api/submit-speaking-response` - Submit speaking assessment
- `GET /api/get-assessment-result` - Get assessment results

### User Management
- `GET /dashboard` - User dashboard
- `GET /my-profile` - User profile
- `GET /api/user-profile` - API user profile

### QR Authentication
- `POST /api/auth/generate-qr` - Generate QR code
- `POST /api/auth/verify-qr` - Verify QR scan
- `POST /api/website/request-qr` - Website QR request
- `POST /api/website/check-auth` - Check QR auth status
- `POST /api/mobile/scan-qr` - Mobile QR scan

## Security Configuration

### 1. CloudFront Security Headers
The deployment automatically configures:
- `CF-Secret-3140348d` header validation
- HTTPS-only traffic
- CORS for mobile app origins

### 2. IAM Permissions
Your WWP user already has the required permissions:
- DynamoDB access to your tables
- Bedrock access for Nova AI models
- API Gateway management
- Lambda execution

### 3. JWT Token Security
- Tokens expire after 24 hours
- Refresh tokens for seamless renewal
- Secure token storage in DynamoDB

## Monitoring and Logging

### CloudWatch Integration
- Lambda function metrics
- API Gateway request/response logs
- DynamoDB operation metrics
- Custom application metrics

### Error Handling
- Structured error responses
- Comprehensive logging
- Graceful failure modes

## Testing

### Unit Tests
```bash
cd backend
python -m pytest tests/
```

### Integration Tests
```bash
# Test authentication flow
python tests/test_auth_integration.py

# Test purchase verification
python tests/test_purchase_integration.py

# Test Nova AI integration
python tests/test_nova_ai_integration.py
```

### Load Testing
```bash
# Install artillery
npm install -g artillery

# Run load tests
artillery run tests/load-test.yml
```

## Troubleshooting

### Common Issues

1. **DynamoDB Access Denied**
   - Verify WWP user has DynamoDB permissions
   - Check table names match exactly

2. **Bedrock Access Denied**
   - Ensure Nova models are available in us-east-1
   - Verify Bedrock permissions in WWP user

3. **CORS Issues**
   - Check API Gateway CORS configuration
   - Verify mobile app origins are allowed

4. **Lambda Timeout**
   - Increase timeout for Nova AI functions
   - Optimize code for better performance

### Debug Commands
```bash
# View Lambda logs
serverless logs -f authHandler --tail

# Check DynamoDB table status
aws dynamodb describe-table --table-name ielts-genai-prep-users

# Test Bedrock access
aws bedrock list-foundation-models --region us-east-1
```

## Production Checklist

- [ ] Environment variables configured
- [ ] Custom domain SSL certificate
- [ ] CloudFront distribution active
- [ ] DynamoDB backup enabled
- [ ] CloudWatch alarms configured
- [ ] Error monitoring setup
- [ ] Load testing completed
- [ ] Security audit passed
- [ ] Mobile app integration tested

## Support

For deployment issues:
1. Check CloudWatch logs
2. Verify AWS permissions
3. Test individual Lambda functions
4. Validate DynamoDB table schemas
5. Confirm Nova AI model access