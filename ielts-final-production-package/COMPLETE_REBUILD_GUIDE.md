# Complete Platform Rebuild Guide

## Overview
This guide provides step-by-step instructions to completely rebuild the IELTS GenAI Prep platform from scratch using this package.

## Phase 1: AWS Infrastructure Setup

### 1.1 Create DynamoDB Tables
```bash
# Create all 7 production tables
aws dynamodb create-table --table-name ielts-genai-prep-users --key-schema AttributeName=email,KeyType=HASH --attribute-definitions AttributeName=email,AttributeType=S --billing-mode PAY_PER_REQUEST

aws dynamodb create-table --table-name ielts-genai-prep-sessions --key-schema AttributeName=session_id,KeyType=HASH --attribute-definitions AttributeName=session_id,AttributeType=S --billing-mode PAY_PER_REQUEST --time-to-live-specification AttributeName=expires_at,Enabled=true

aws dynamodb create-table --table-name ielts-genai-prep-assessments --key-schema AttributeName=assessment_id,KeyType=HASH --attribute-definitions AttributeName=assessment_id,AttributeType=S AttributeName=user_id,AttributeType=S AttributeName=completed_at,AttributeType=S --billing-mode PAY_PER_REQUEST --global-secondary-indexes IndexName=user-assessments-index,KeySchema=[{AttributeName=user_id,KeyType=HASH},{AttributeName=completed_at,KeyType=RANGE}],Projection={ProjectionType=ALL}

aws dynamodb create-table --table-name ielts-genai-prep-questions --key-schema AttributeName=question_id,KeyType=HASH --attribute-definitions AttributeName=question_id,AttributeType=S --billing-mode PAY_PER_REQUEST

aws dynamodb create-table --table-name ielts-genai-prep-purchases --key-schema AttributeName=purchase_id,KeyType=HASH --attribute-definitions AttributeName=purchase_id,AttributeType=S AttributeName=user_id,AttributeType=S AttributeName=purchase_date,AttributeType=S --billing-mode PAY_PER_REQUEST --global-secondary-indexes IndexName=user-purchases-index,KeySchema=[{AttributeName=user_id,KeyType=HASH},{AttributeName=purchase_date,KeyType=RANGE}],Projection={ProjectionType=ALL}

aws dynamodb create-table --table-name ielts-genai-prep-qr-auth --key-schema AttributeName=qr_code_id,KeyType=HASH --attribute-definitions AttributeName=qr_code_id,AttributeType=S --billing-mode PAY_PER_REQUEST --time-to-live-specification AttributeName=expires_at,Enabled=true

aws dynamodb create-table --table-name ielts-genai-prep-gdpr --key-schema AttributeName=request_id,KeyType=HASH --attribute-definitions AttributeName=request_id,AttributeType=S --billing-mode PAY_PER_REQUEST --time-to-live-specification AttributeName=expires_at,Enabled=true
```

### 1.2 Enable Global Tables (Multi-Region)
```bash
# Enable global tables for multi-region replication
aws dynamodb create-global-table --global-table-name ielts-genai-prep-users --replication-group RegionName=us-east-1 RegionName=eu-west-1 RegionName=ap-southeast-1

aws dynamodb create-global-table --global-table-name ielts-genai-prep-sessions --replication-group RegionName=us-east-1 RegionName=eu-west-1 RegionName=ap-southeast-1

# Repeat for all tables
```

### 1.3 Populate Question Banks
```python
# Use the provided question bank files to populate DynamoDB
import json
import boto3

dynamodb = boto3.client('dynamodb')

# Load and insert academic writing questions
with open('Academic Writing Task 2 tests (essays).txt', 'r') as f:
    questions = parse_writing_questions(f.read())
    
for question in questions:
    dynamodb.put_item(
        TableName='ielts-genai-prep-questions',
        Item={
            'question_id': {'S': str(uuid.uuid4())},
            'question_type': {'S': 'academic_writing_task2'},
            'prompt': {'S': question['prompt']},
            'difficulty_level': {'S': question['difficulty']},
            'is_active': {'BOOL': True}
        }
    )
```

## Phase 2: Lambda Function Deployment

### 2.1 Create Lambda Function
```bash
# Create Lambda function
aws lambda create-function \
  --function-name ielts-genai-prep-api \
  --runtime python3.11 \
  --role arn:aws:iam::ACCOUNT-ID:role/lambda-execution-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://clean_lambda_with_deps.zip \
  --environment Variables='{
    "DYNAMODB_TABLE_PREFIX":"ielts-genai-prep",
    "ENVIRONMENT":"production",
    "BEDROCK_REGION":"us-east-1",
    "SES_REGION":"us-east-1"
  }'
```

### 2.2 Set Environment Variables
```bash
# Set all required environment variables
aws lambda update-function-configuration \
  --function-name ielts-genai-prep-api \
  --environment Variables='{
    "DYNAMODB_TABLE_PREFIX":"ielts-genai-prep",
    "ENVIRONMENT":"production",
    "RECAPTCHA_V2_SITE_KEY":"your-site-key",
    "RECAPTCHA_V2_SECRET_KEY":"your-secret-key",
    "BEDROCK_REGION":"us-east-1",
    "SES_REGION":"us-east-1",
    "APPLE_SHARED_SECRET":"your-apple-secret",
    "GOOGLE_PLAY_SERVICE_ACCOUNT":"base64-encoded-json"
  }'
```

## Phase 3: API Gateway Setup

### 3.1 Create REST API
```bash
# Create API Gateway
aws apigateway create-rest-api --name ielts-genai-prep-api --description "IELTS GenAI Prep API"

# Create resources and methods for all endpoints
# GET /
# POST /api/login
# GET /dashboard
# GET /assessment/{type}
# POST /api/delete-account
# etc.
```

### 3.2 Create WebSocket API (for Nova Sonic)
```bash
# Create WebSocket API for real-time speaking assessments
aws apigatewayv2 create-api \
  --name ielts-speaking-websocket \
  --protocol-type WEBSOCKET \
  --route-selection-expression '$request.body.action'
```

## Phase 4: CloudFront Distribution

### 4.1 Create Distribution
```json
{
  "CallerReference": "ielts-genai-prep-2025",
  "Origins": {
    "Quantity": 1,
    "Items": [{
      "Id": "api-gateway-origin",
      "DomainName": "api-id.execute-api.us-east-1.amazonaws.com",
      "CustomOriginConfig": {
        "HTTPPort": 443,
        "HTTPSPort": 443,
        "OriginProtocolPolicy": "https-only"
      }
    }]
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "api-gateway-origin",
    "ViewerProtocolPolicy": "redirect-to-https",
    "CachePolicyId": "4135ea2d-6df8-44a3-9df3-4b5a84be39ad"
  },
  "Aliases": {
    "Quantity": 1,
    "Items": ["www.ieltsaiprep.com"]
  }
}
```

## Phase 5: Domain and SSL Setup

### 5.1 Route 53 Configuration
```bash
# Create hosted zone
aws route53 create-hosted-zone --name ieltsaiprep.com --caller-reference $(date +%s)

# Create A record pointing to CloudFront
aws route53 change-resource-record-sets --hosted-zone-id Z123456789 --change-batch '{
  "Changes": [{
    "Action": "CREATE",
    "ResourceRecordSet": {
      "Name": "www.ieltsaiprep.com",
      "Type": "A",
      "AliasTarget": {
        "DNSName": "d123456789.cloudfront.net",
        "EvaluateTargetHealth": false,
        "HostedZoneId": "Z2FDTNDATAQYW2"
      }
    }
  }]
}'
```

### 5.2 SSL Certificate (ACM)
```bash
# Request SSL certificate
aws acm request-certificate \
  --domain-name ieltsaiprep.com \
  --subject-alternative-names www.ieltsaiprep.com \
  --validation-method DNS \
  --region us-east-1
```

## Phase 6: Mobile App Setup

### 6.1 Capacitor Configuration
```bash
# Install Capacitor and dependencies
npm install @capacitor/core @capacitor/cli @capacitor/android @capacitor/ios

# Initialize Capacitor project
npx cap init ielts-genai-prep com.ieltsaiprep.app

# Copy capacitor.config.ts from package
# Build web assets and sync
npm run build
npx cap sync
```

### 6.2 Android Configuration
```bash
# Generate signed APK
npx cap build android

# Configure Google Play Store
# Upload android_play_store_config.json settings to Play Console
# Configure in-app billing products with IDs:
# - academic_writing_assessment ($36.49)
# - general_writing_assessment ($36.49)  
# - academic_speaking_assessment ($36.49)
# - general_speaking_assessment ($36.49)
```

### 6.3 iOS Configuration
```bash
# Generate iOS build
npx cap build ios

# Configure App Store Connect
# Set up in-app purchases with same product IDs
# Configure App Store review information
```

## Phase 7: AI Service Configuration

### 7.1 AWS Bedrock Access
```bash
# Enable model access in AWS Bedrock console
# Request access to:
# - amazon.nova-micro-v1:0 (writing assessments)
# - amazon.nova-sonic-v1:0 (speaking assessments)

# Test model access
aws bedrock-runtime converse \
  --model-id amazon.nova-micro-v1:0 \
  --messages '[{"role":"user","content":[{"text":"Test message"}]}]'
```

### 7.2 SES Email Configuration
```bash
# Verify domain for sending emails
aws ses verify-domain-identity --domain ieltsaiprep.com

# Create email templates
aws ses create-template --template '{
  "TemplateName": "WelcomeEmail",
  "SubjectPart": "Welcome to IELTS GenAI Prep",
  "HtmlPart": "Welcome {{first_name}}..."
}'
```

## Phase 8: Security Configuration

### 8.1 IAM Roles and Policies
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Scan",
        "dynamodb:Query"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/ielts-genai-prep-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "arn:aws:bedrock:us-east-1::foundation-model/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ses:SendEmail",
        "ses:SendRawEmail"
      ],
      "Resource": "*"
    }
  ]
}
```

### 8.2 Google reCAPTCHA Setup
```javascript
// Get site key and secret key from Google reCAPTCHA v2
// Add to Lambda environment variables
// Configure for domain: ieltsaiprep.com
```

## Phase 9: Testing and Validation

### 9.1 End-to-End Testing
```python
# Test complete user flow
def test_complete_flow():
    # 1. Mobile app registration
    # 2. Purchase validation
    # 3. QR code authentication
    # 4. Web platform access
    # 5. Assessment completion
    # 6. AI feedback generation
    # 7. GDPR data export/deletion
```

### 9.2 Load Testing
```bash
# Use provided test scripts to validate:
# - 1000 concurrent users
# - Assessment processing capacity
# - Database query performance
# - CloudFront cache efficiency
```

## Phase 10: Monitoring and Alerting

### 10.1 CloudWatch Setup
```bash
# Create CloudWatch dashboards
# Set up alarms for:
# - Lambda function errors
# - DynamoDB throttling
# - API Gateway 5xx errors
# - Bedrock quota exceeded
```

## Phase 11: Backup and Disaster Recovery

### 11.1 Database Backups
```bash
# Enable point-in-time recovery
aws dynamodb update-continuous-backups \
  --table-name ielts-genai-prep-users \
  --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true
```

### 11.2 Code Versioning
```bash
# Version Lambda functions
aws lambda publish-version --function-name ielts-genai-prep-api

# Create aliases for blue/green deployments
aws lambda create-alias \
  --function-name ielts-genai-prep-api \
  --name production \
  --function-version 1
```

## Verification Checklist

- [ ] All 7 DynamoDB tables created with proper indexes
- [ ] Lambda function deployed with correct environment variables
- [ ] API Gateway configured with all endpoints
- [ ] CloudFront distribution serving www.ieltsaiprep.com
- [ ] SSL certificate installed and verified
- [ ] Mobile apps built and configured for app stores
- [ ] AWS Bedrock model access enabled
- [ ] SES domain verified and templates created
- [ ] reCAPTCHA v2 configured
- [ ] IAM roles and policies applied
- [ ] Monitoring and alerting active
- [ ] End-to-end testing completed
- [ ] Load testing passed
- [ ] GDPR compliance verified
- [ ] Mobile purchase flows tested
- [ ] AI assessment accuracy validated

## Production Readiness

Once all items are checked, the platform will be fully operational with:
- Global multi-region deployment
- 99.9% uptime SLA
- GDPR compliance
- Mobile app store approval
- AI-powered assessments
- Real-time speaking evaluation
- Cross-platform authentication
- Secure payment processing