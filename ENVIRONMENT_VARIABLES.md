# Complete Environment Variables Configuration

## Production Lambda Environment Variables

### Required for Core Functionality
```bash
DYNAMODB_TABLE_PREFIX=ielts-genai-prep
ENVIRONMENT=production
AWS_DEFAULT_REGION=us-east-1
```

### AI Services Configuration
```bash
BEDROCK_REGION=us-east-1
NOVA_SONIC_MODEL_ID=amazon.nova-sonic-v1:0
NOVA_MICRO_MODEL_ID=amazon.nova-micro-v1:0
BEDROCK_MAX_TOKENS=4096
BEDROCK_TEMPERATURE=0.7
```

### Authentication & Security
```bash
RECAPTCHA_V2_SITE_KEY=6LcXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
RECAPTCHA_V2_SECRET_KEY=6LcXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
SESSION_SECRET_KEY=your-64-character-random-string-for-session-encryption
JWT_SECRET_KEY=your-jwt-signing-key-for-mobile-tokens
PASSWORD_SALT_ROUNDS=12
```

### Email Services (AWS SES)
```bash
SES_REGION=us-east-1
SES_FROM_EMAIL=noreply@ieltsaiprep.com
SES_REPLY_TO_EMAIL=support@ieltsaiprep.com
WELCOME_EMAIL_TEMPLATE=WelcomeEmail
DELETION_EMAIL_TEMPLATE=AccountDeletionConfirmation
```

### Mobile App Purchase Validation
```bash
# iOS App Store
APPLE_SHARED_SECRET=your-apple-app-store-shared-secret
APPLE_BUNDLE_ID=com.ieltsaiprep.app
APPLE_VERIFICATION_URL=https://buy.itunes.apple.com/verifyReceipt
APPLE_SANDBOX_URL=https://sandbox.itunes.apple.com/verifyReceipt

# Google Play Store
GOOGLE_PLAY_SERVICE_ACCOUNT=base64-encoded-service-account-json
GOOGLE_PLAY_PACKAGE_NAME=com.ieltsaiprep.app
```

### Database Configuration
```bash
DYNAMODB_READ_CAPACITY=5
DYNAMODB_WRITE_CAPACITY=5
DYNAMODB_TTL_SESSIONS=86400
DYNAMODB_TTL_QR_AUTH=300
DYNAMODB_TTL_GDPR_REQUESTS=604800
```

### Assessment Configuration
```bash
DEFAULT_ASSESSMENT_ATTEMPTS=4
ASSESSMENT_TIME_LIMIT_WRITING=3600
ASSESSMENT_TIME_LIMIT_SPEAKING=900
SPEAKING_RESPONSE_TIME_LIMIT=180
WRITING_WORD_COUNT_MIN=250
WRITING_WORD_COUNT_MAX=500
```

### GDPR & Privacy
```bash
DATA_RETENTION_DAYS=2555
GDPR_VERIFICATION_CODE_LENGTH=6
GDPR_REQUEST_EXPIRY_HOURS=168
VOICE_RECORDING_RETENTION_HOURS=24
ASSESSMENT_HISTORY_RETENTION_DAYS=365
```

### Content Safety & Moderation
```bash
CONTENT_SAFETY_ENABLED=true
PROFANITY_FILTER_ENABLED=true
CONTENT_MODERATION_THRESHOLD=0.8
INAPPROPRIATE_CONTENT_WEBHOOK=https://webhook-url-for-flagged-content
```

### Rate Limiting
```bash
RATE_LIMIT_LOGIN_ATTEMPTS=5
RATE_LIMIT_LOGIN_WINDOW=3600
RATE_LIMIT_QR_GENERATION=10
RATE_LIMIT_ASSESSMENT_ATTEMPTS=4
RATE_LIMIT_PASSWORD_RESET=3
```

### Monitoring & Logging
```bash
CLOUDWATCH_LOG_GROUP=/aws/lambda/ielts-genai-prep-api
CLOUDWATCH_LOG_LEVEL=INFO
SENTRY_DSN=your-sentry-dsn-for-error-tracking
APPLICATION_INSIGHTS_KEY=your-application-insights-key
```

### Feature Flags
```bash
FEATURE_SPEAKING_ASSESSMENT=true
FEATURE_WRITING_ASSESSMENT=true
FEATURE_QR_AUTHENTICATION=true
FEATURE_MOBILE_APP_INTEGRATION=true
FEATURE_GDPR_TOOLS=true
FEATURE_ADMIN_PANEL=false
FEATURE_BETA_FEATURES=false
```

### API Configuration
```bash
API_GATEWAY_DOMAIN=api.ieltsaiprep.com
CLOUDFRONT_DOMAIN=www.ieltsaiprep.com
WEBSOCKET_API_GATEWAY_URL=wss://websocket-api-id.execute-api.us-east-1.amazonaws.com/production
CORS_ALLOWED_ORIGINS=https://www.ieltsaiprep.com,https://ieltsaiprep.com
```

### Third-Party Integrations
```bash
STRIPE_SECRET_KEY=sk_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
INTERCOM_ACCESS_TOKEN=your-intercom-access-token
ANALYTICS_TRACKING_ID=UA-XXXXXXXX-X
```

## Development Environment Variables

### Local Development (.env file)
```bash
ENVIRONMENT=development
DYNAMODB_TABLE_PREFIX=ielts-genai-prep-dev
AWS_DEFAULT_REGION=us-east-1
RECAPTCHA_V2_SITE_KEY=development-site-key
RECAPTCHA_V2_SECRET_KEY=development-secret-key
SESSION_SECRET_KEY=development-session-secret-key-64-chars-long-random-string
SES_FROM_EMAIL=test@ieltsaiprep.com
BEDROCK_REGION=us-east-1
```

### Testing Environment
```bash
ENVIRONMENT=testing
DYNAMODB_TABLE_PREFIX=ielts-genai-prep-test
USE_MOCK_SERVICES=true
MOCK_BEDROCK_RESPONSES=true
MOCK_PURCHASE_VALIDATION=true
DISABLE_RATE_LIMITING=true
```

## AWS Systems Manager Parameter Store

### Secure Parameter Storage
```bash
# Store sensitive values in Parameter Store
aws ssm put-parameter \
  --name "/ielts-genai-prep/production/recaptcha-secret" \
  --value "your-secret-key" \
  --type "SecureString" \
  --key-id "alias/aws/ssm"

aws ssm put-parameter \
  --name "/ielts-genai-prep/production/apple-shared-secret" \
  --value "your-apple-secret" \
  --type "SecureString"

aws ssm put-parameter \
  --name "/ielts-genai-prep/production/google-play-service-account" \
  --value "base64-encoded-json" \
  --type "SecureString"
```

### Lambda Function Access
```python
import boto3

ssm = boto3.client('ssm')

def get_secure_parameter(parameter_name):
    response = ssm.get_parameter(
        Name=f"/ielts-genai-prep/production/{parameter_name}",
        WithDecryption=True
    )
    return response['Parameter']['Value']

# Usage in Lambda
RECAPTCHA_SECRET = get_secure_parameter('recaptcha-secret')
APPLE_SECRET = get_secure_parameter('apple-shared-secret')
```

## Environment-Specific Configurations

### Production
- All rate limiting enabled
- Full content safety measures
- Real purchase validation
- Production Bedrock models
- CloudWatch detailed monitoring
- Error tracking enabled

### Staging
- Reduced rate limiting
- Test purchase validation
- Same Bedrock models as production
- Enhanced logging for debugging
- Feature flag testing enabled

### Development
- No rate limiting
- Mock services for external APIs
- Local DynamoDB or mock data
- Verbose logging enabled
- All feature flags enabled for testing

## Security Best Practices

### Never Include in Code
- API keys or secrets
- Database credentials
- Third-party service tokens
- Encryption keys
- Personal data

### Always Use
- Environment variables for configuration
- AWS Systems Manager for sensitive data
- IAM roles for AWS service access
- Encrypted storage for secrets
- Regular credential rotation

## Validation Scripts

### Check Required Variables
```python
def validate_environment():
    required_vars = [
        'DYNAMODB_TABLE_PREFIX',
        'ENVIRONMENT',
        'RECAPTCHA_V2_SECRET_KEY',
        'SES_FROM_EMAIL',
        'BEDROCK_REGION'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {missing_vars}")
    
    return True
```

### Test Configuration
```python
def test_services():
    # Test DynamoDB connection
    # Test Bedrock access
    # Test SES configuration
    # Test reCAPTCHA validation
    # Test mobile purchase validation
    pass
```