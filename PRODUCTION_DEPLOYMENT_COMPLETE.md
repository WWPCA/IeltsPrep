# Complete Production Deployment Guide

This guide walks you through deploying the IELTS GenAI Prep mobile-first authentication system to AWS with full mobile app integration.

## Quick Start (5 Commands)

```bash
# 1. Deploy AWS infrastructure
./deploy-aws-infrastructure.sh

# 2. Deploy Lambda functions
sam build && sam deploy --guided

# 3. Populate assessment data
python3 populate-assessment-data.py

# 4. Configure all endpoints automatically
./configure-production-endpoints.sh

# 5. Test production setup
./production-config.sh
```

## What Gets Deployed

### AWS Infrastructure
- **DynamoDB Tables**: Users, sessions, assessments, rubrics with proper TTL
- **Lambda Functions**: Mobile-first authentication with Nova AI integration  
- **API Gateway**: RESTful endpoints for mobile and web access
- **WebSocket API**: Real-time Nova Sonic speech streaming
- **ElastiCache Redis**: Session storage with 1-hour expiration
- **IAM Roles**: Bedrock, DynamoDB, and CloudWatch permissions

### Mobile App Configuration
- **iOS/Android**: Capacitor-based native apps with in-app purchases
- **Purchase Integration**: Apple App Store and Google Play Store verification
- **API Client**: Production-ready HTTP client with session management
- **WebSocket Client**: Nova Sonic real-time audio streaming

### Website Configuration  
- **Production Endpoints**: Automatic API Gateway URL configuration
- **Session Management**: Secure cookie-based authentication
- **Nova Integration**: Writing assessment with Nova Micro, speaking with Nova Sonic

## File Structure

```
Production Configuration Files:
├── deploy-aws-infrastructure.sh     # Creates all AWS resources
├── template.yaml                    # SAM template for Lambda deployment
├── populate-assessment-data.py      # IELTS rubrics and Nova prompts
├── configure-production-endpoints.sh # Auto-configures all endpoints
├── production-config.sh             # Tests and validates deployment

Mobile App Files:
├── mobile-app-config.js            # Environment and API configuration
├── mobile-api-client.js            # HTTP client with authentication
├── mobile-purchase-integration.js  # Apple/Google purchase handling
├── capacitor.config.json           # Native app configuration

Website Files:
├── website-config.js               # Frontend JavaScript configuration
├── app.py                         # Lambda handler with mobile-first auth
├── aws_mock_config.py             # Development environment simulation
```

## Step-by-Step Deployment

### 1. AWS Account Setup
```bash
# Configure AWS CLI with your credentials
aws configure
# Enter: Access Key ID, Secret Access Key, us-east-1, json
```

### 2. Deploy Infrastructure
```bash
# Creates DynamoDB, ElastiCache, IAM roles, CloudWatch
./deploy-aws-infrastructure.sh
```

### 3. Deploy Lambda Functions
```bash
# Build and deploy serverless application
sam build
sam deploy --guided

# Follow prompts:
# Stack name: ielts-genai-prep
# AWS Region: us-east-1  
# Confirm changes: Y
# Allow IAM role creation: Y
# Save parameters: Y
```

### 4. Populate Assessment Data
```bash
# Load IELTS rubrics and Nova AI system prompts
export AWS_REGION=us-east-1
export STACK_NAME=ielts-genai-prep
python3 populate-assessment-data.py
```

### 5. Configure All Endpoints
```bash
# Automatically updates mobile app, website, and Capacitor config
./configure-production-endpoints.sh
```

## Mobile App Deployment

### iOS App Store
```bash
# Build iOS app
npx cap build ios

# Open in Xcode
npx cap open ios

# Configure in Xcode:
# 1. Set bundle identifier: com.ieltsgenaiprep.app
# 2. Configure App Store Connect
# 3. Add in-app purchase products:
#    - com.ieltsgenaiprep.academic.writing ($36.00)
#    - com.ieltsgenaiprep.general.writing ($36.00)  
#    - com.ieltsgenaiprep.academic.speaking ($36.00)
#    - com.ieltsgenaiprep.general.speaking ($36.00)
# 4. Submit for review
```

### Google Play Store
```bash
# Build Android app
npx cap build android

# Open in Android Studio
npx cap open android

# Configure in Android Studio:
# 1. Set application ID: com.ieltsgenaiprep.app
# 2. Configure Google Play Console
# 3. Add in-app products:
#    - academic_writing_assessment ($36.00)
#    - general_writing_assessment ($36.00)
#    - academic_speaking_assessment ($36.00)  
#    - general_speaking_assessment ($36.00)
# 4. Upload to Play Store
```

## Website Deployment

The Lambda function serves both API endpoints and website pages. Your API Gateway URL is your website URL.

### Custom Domain (Optional)
```bash
# 1. Register domain in Route 53
# 2. Create SSL certificate in ACM
# 3. Configure API Gateway custom domain
# 4. Update DNS CNAME record
```

## Environment Variables

Production automatically uses these settings:
```bash
# AWS Services
AWS_REGION=us-east-1
DYNAMODB_USERS_TABLE=ielts-genai-prep-users
DYNAMODB_SESSIONS_TABLE=ielts-genai-prep-sessions
DYNAMODB_ASSESSMENTS_TABLE=ielts-genai-prep-assessments
DYNAMODB_RUBRICS_TABLE=ielts-genai-prep-rubrics

# APIs
API_GATEWAY_URL=https://your-id.execute-api.us-east-1.amazonaws.com/Prod
WEBSOCKET_URL=wss://your-ws-id.execute-api.us-east-1.amazonaws.com/Prod

# Nova AI
# Requires Bedrock model access for Nova Sonic and Nova Micro
```

## Testing Production

### Health Check
```bash
curl https://your-api-gateway-url/api/health
# Expected: {"success": true, "status": "healthy"}
```

### User Registration
```bash
curl -X POST https://your-api-gateway-url/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123",
    "confirm_password": "TestPassword123", 
    "terms_accepted": true,
    "privacy_accepted": true
  }'
```

### User Login
```bash
curl -X POST https://your-api-gateway-url/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123"
  }'
```

## Nova AI Setup

### Enable Bedrock Models
1. Go to AWS Bedrock Console (us-east-1)
2. Request access to:
   - Amazon Nova Sonic v1.0 (speaking assessments)
   - Amazon Nova Micro v1.0 (writing assessments)
3. Wait for approval (usually immediate)

### Test Nova Integration
- Writing assessments use Nova Micro for evaluation
- Speaking assessments use Nova Sonic for Maya examiner conversations
- WebSocket streaming enables real-time speech interaction

## User Flow

### Mobile App Users
1. Download iOS/Android app from stores
2. Create account with email/password
3. Purchase assessment products ($36 each)
4. Complete assessments in app OR login to website

### Website Users  
1. Visit website login page
2. Guided to download mobile app first
3. Register and purchase in mobile app
4. Return to website and login with same credentials
5. Access assessments on desktop/laptop

## Monitoring and Maintenance

### CloudWatch Dashboards
Monitor key metrics:
- Lambda function duration and errors
- DynamoDB read/write capacity
- API Gateway request count and latency
- ElastiCache connection count

### Cost Management
- DynamoDB: Pay-per-request billing scales with usage
- Lambda: Charged per invocation and duration
- ElastiCache: Fixed hourly cost for t3.micro instance
- API Gateway: Charges per API call

### Security
- All API endpoints require authentication
- Sessions expire after 1 hour
- bcrypt password hashing
- Secure mobile app storage

## Troubleshooting

### Common Issues
- **Lambda timeout**: Increase timeout in template.yaml
- **DynamoDB throttling**: Enable auto-scaling  
- **ElastiCache connection**: Check VPC security groups
- **Nova AI access denied**: Enable Bedrock model access

### Log Analysis
```bash
# View Lambda logs
aws logs tail /aws/lambda/ielts-genai-prep --follow --region us-east-1

# Check DynamoDB metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name ConsumedReadCapacityUnits \
  --dimensions Name=TableName,Value=ielts-genai-prep-users \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 --statistics Sum
```

This deployment creates a complete production-ready system supporting millions of global users with mobile-first authentication and Nova AI-powered assessments.