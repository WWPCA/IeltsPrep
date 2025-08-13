# Secrets and API Keys Configuration Guide

## Required External Service Accounts

### 1. Google reCAPTCHA v2
**Purpose:** Prevent automated registrations and spam
**Setup:**
1. Go to https://www.google.com/recaptcha/admin
2. Create new site for domain: ieltsaiprep.com
3. Select reCAPTCHA v2 "I'm not a robot" checkbox
4. Add domains: ieltsaiprep.com, www.ieltsaiprep.com
5. Get Site Key and Secret Key

**Environment Variables:**
```
RECAPTCHA_V2_SITE_KEY=6LcXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
RECAPTCHA_V2_SECRET_KEY=6LcXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### 2. Apple App Store Connect
**Purpose:** iOS in-app purchase validation
**Setup:**
1. Create Apple Developer Account ($99/year)
2. Register app with Bundle ID: com.ieltsaiprep.app
3. Create in-app purchases for each assessment type
4. Generate Shared Secret in App Store Connect

**Required Information:**
```
APPLE_SHARED_SECRET=your-apple-shared-secret-from-app-store-connect
APPLE_BUNDLE_ID=com.ieltsaiprep.app
```

**In-App Purchase Product IDs:**
- academic_writing_assessment
- general_writing_assessment  
- academic_speaking_assessment
- general_speaking_assessment

### 3. Google Play Console
**Purpose:** Android in-app purchase validation
**Setup:**
1. Create Google Play Developer Account ($25 one-time)
2. Upload app with package name: com.ieltsaiprep.app
3. Create managed products for each assessment
4. Create service account for Play Developer API
5. Download service account JSON key

**Service Account Setup:**
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "service-account@project.iam.gserviceaccount.com",
  "client_id": "client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token"
}
```

**Environment Variable:**
```
GOOGLE_PLAY_SERVICE_ACCOUNT=base64-encoded-service-account-json
```

### 4. AWS Account Setup
**Purpose:** Core platform infrastructure
**Required Services:**
- Lambda (serverless compute)
- DynamoDB (database)
- Bedrock (AI models)
- SES (email)
- CloudFront (CDN)
- Route 53 (DNS)
- Certificate Manager (SSL)

**Bedrock Model Access:**
1. Go to AWS Bedrock console
2. Request access to models:
   - amazon.nova-micro-v1:0
   - amazon.nova-sonic-v1:0
3. Wait for approval (usually instant)

**SES Domain Verification:**
1. Add ieltsaiprep.com to SES
2. Verify domain ownership
3. Move out of sandbox mode

### 5. Domain Registration
**Purpose:** Custom domain for production website
**Setup:**
1. Register ieltsaiprep.com domain
2. Configure nameservers to point to Route 53
3. Create hosted zone in Route 53
4. Request SSL certificate in ACM

## Security Implementation

### AWS Systems Manager Parameter Store
```bash
# Store all secrets securely
aws ssm put-parameter \
  --name "/ielts-genai-prep/production/recaptcha-secret" \
  --value "6LcXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" \
  --type "SecureString"

aws ssm put-parameter \
  --name "/ielts-genai-prep/production/apple-shared-secret" \
  --value "your-apple-shared-secret" \
  --type "SecureString"

aws ssm put-parameter \
  --name "/ielts-genai-prep/production/google-play-service-account" \
  --value "base64-encoded-service-account-json" \
  --type "SecureString"
```

### Lambda Function Access
```python
import boto3
import base64
import json

ssm = boto3.client('ssm')

def get_secret(parameter_name):
    """Retrieve encrypted parameter from Systems Manager"""
    try:
        response = ssm.get_parameter(
            Name=f"/ielts-genai-prep/production/{parameter_name}",
            WithDecryption=True
        )
        return response['Parameter']['Value']
    except Exception as e:
        print(f"Error retrieving secret {parameter_name}: {str(e)}")
        return None

# Usage examples
RECAPTCHA_SECRET = get_secret('recaptcha-secret')
APPLE_SECRET = get_secret('apple-shared-secret')
GOOGLE_PLAY_ACCOUNT = json.loads(base64.b64decode(get_secret('google-play-service-account')))
```

## API Integration Code Examples

### reCAPTCHA Validation
```python
import requests

def verify_recaptcha(response_token, user_ip):
    """Verify reCAPTCHA response"""
    url = 'https://www.google.com/recaptcha/api/siteverify'
    data = {
        'secret': RECAPTCHA_SECRET,
        'response': response_token,
        'remoteip': user_ip
    }
    
    response = requests.post(url, data=data)
    result = response.json()
    
    return result.get('success', False)
```

### Apple App Store Receipt Validation
```python
import requests
import base64

def validate_ios_receipt(receipt_data, is_sandbox=False):
    """Validate iOS App Store receipt"""
    url = 'https://sandbox.itunes.apple.com/verifyReceipt' if is_sandbox else 'https://buy.itunes.apple.com/verifyReceipt'
    
    payload = {
        'receipt-data': receipt_data,
        'password': APPLE_SECRET,
        'exclude-old-transactions': True
    }
    
    response = requests.post(url, json=payload)
    result = response.json()
    
    if result.get('status') == 21007:  # Sandbox receipt sent to production
        return validate_ios_receipt(receipt_data, is_sandbox=True)
    
    return result.get('status') == 0, result
```

### Google Play Purchase Validation
```python
from google.oauth2 import service_account
from googleapiclient.discovery import build

def validate_android_purchase(purchase_token, product_id):
    """Validate Google Play purchase"""
    credentials = service_account.Credentials.from_service_account_info(
        GOOGLE_PLAY_ACCOUNT,
        scopes=['https://www.googleapis.com/auth/androidpublisher']
    )
    
    service = build('androidpublisher', 'v3', credentials=credentials)
    
    try:
        result = service.purchases().products().get(
            packageName='com.ieltsaiprep.app',
            productId=product_id,
            token=purchase_token
        ).execute()
        
        return result.get('purchaseState') == 0, result
    except Exception as e:
        print(f"Error validating Android purchase: {str(e)}")
        return False, None
```

## Development vs Production Secrets

### Development Environment
```bash
# Use test/development keys
RECAPTCHA_V2_SITE_KEY=6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI  # Test key
RECAPTCHA_V2_SECRET_KEY=6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe  # Test key
ENVIRONMENT=development
USE_MOCK_SERVICES=true
```

### Production Environment
```bash
# Use real production keys
RECAPTCHA_V2_SITE_KEY=your-real-production-site-key
RECAPTCHA_V2_SECRET_KEY=your-real-production-secret-key
ENVIRONMENT=production
USE_MOCK_SERVICES=false
```

## Cost Estimates

### Apple Developer Program
- **Cost:** $99/year
- **Purpose:** iOS app distribution and in-app purchases

### Google Play Developer
- **Cost:** $25 one-time registration
- **Purpose:** Android app distribution and in-app purchases

### AWS Services (Monthly estimates for moderate usage)
- **Lambda:** $10-20
- **DynamoDB:** $25-50
- **Bedrock:** $100-200 (based on AI usage)
- **SES:** $5-10
- **CloudFront:** $10-25
- **Route 53:** $2-5
- **Total AWS:** ~$150-300/month

### Domain Registration
- **Cost:** $12-15/year for .com domain

## Security Best Practices

### Never Commit to Code
- API keys or secrets
- Service account JSON files
- Database credentials
- Third-party tokens

### Always Use
- Environment variables for all configuration
- AWS Systems Manager for sensitive data
- IAM roles for AWS service access
- HTTPS for all external API calls
- Input validation and sanitization

### Regular Maintenance
- Rotate secrets every 90 days
- Monitor API usage and costs
- Review access logs monthly
- Update dependencies regularly
- Test backup and recovery procedures

## Troubleshooting Common Issues

### reCAPTCHA Fails
- Verify domain is added to reCAPTCHA console
- Check site key matches environment
- Ensure HTTPS is used (required for production)

### iOS Purchase Validation Fails
- Verify Bundle ID matches exactly
- Check Shared Secret is current
- Test with sandbox environment first
- Ensure products are approved in App Store Connect

### Android Purchase Validation Fails
- Verify package name matches exactly
- Check service account has proper permissions
- Ensure app is published (at least internal testing)
- Test with real purchase tokens

### AWS Bedrock Access Denied
- Request model access in Bedrock console
- Verify IAM permissions include bedrock:InvokeModel
- Check region availability (Nova models in us-east-1)

This configuration guide provides everything needed to set up all external services and secrets required for the complete IELTS GenAI Prep platform.