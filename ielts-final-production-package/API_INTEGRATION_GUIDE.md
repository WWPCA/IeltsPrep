# API Integration Guide

## AWS Bedrock Integration

### Nova Sonic (Speaking Assessments)
```python
# Real-time conversation with Maya AI examiner
import boto3

bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')

response = bedrock_client.converse_stream(
    modelId='amazon.nova-micro-v1:0',
    messages=[{
        'role': 'user',
        'content': [{'text': user_message}]
    }],
    inferenceConfig={
        'temperature': 0.7,
        'topP': 0.9
    }
)
```

### Nova Micro (Writing Assessments)
```python
# AI-powered writing evaluation
def evaluate_writing(essay_text, assessment_type):
    prompt = f"""
    Evaluate this IELTS {assessment_type} essay using official band descriptors:
    
    Essay: {essay_text}
    
    Provide scores for:
    - Task Achievement (0-9)
    - Coherence and Cohesion (0-9)  
    - Lexical Resource (0-9)
    - Grammatical Range and Accuracy (0-9)
    - Overall Band Score
    """
    
    response = bedrock_client.converse(
        modelId='amazon.nova-micro-v1:0',
        messages=[{'role': 'user', 'content': [{'text': prompt}]}]
    )
    return response
```

## DynamoDB Operations

### User Authentication
```python
def authenticate_user(email, password):
    # Get user from DynamoDB
    response = dynamodb.get_item(
        TableName='ielts-genai-prep-users',
        Key={'email': {'S': email}}
    )
    
    if response.get('Item'):
        stored_hash = response['Item']['password_hash']['S']
        if bcrypt.checkpw(password.encode(), stored_hash.encode()):
            return create_session(response['Item'])
    return None
```

### Assessment Storage
```python
def save_assessment_result(user_id, assessment_data):
    assessment_id = str(uuid.uuid4())
    
    dynamodb.put_item(
        TableName='ielts-genai-prep-assessments',
        Item={
            'assessment_id': {'S': assessment_id},
            'user_id': {'S': user_id},
            'assessment_type': {'S': assessment_data['type']},
            'ai_feedback': {'S': json.dumps(assessment_data['feedback'])},
            'completed_at': {'S': datetime.utcnow().isoformat()}
        }
    )
```

## Mobile App Integration

### Purchase Validation (iOS)
```python
def validate_ios_purchase(receipt_data, user_id):
    # Validate with Apple App Store
    url = "https://buy.itunes.apple.com/verifyReceipt"
    payload = {
        "receipt-data": receipt_data,
        "password": APPLE_SHARED_SECRET
    }
    
    response = requests.post(url, json=payload)
    if response.json().get('status') == 0:
        # Grant assessment attempts
        grant_assessment_attempts(user_id, product_id)
        return True
    return False
```

### Purchase Validation (Android)
```python
def validate_android_purchase(purchase_token, product_id):
    # Validate with Google Play Billing
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    
    service = build('androidpublisher', 'v3', credentials=credentials)
    result = service.purchases().products().get(
        packageName=PACKAGE_NAME,
        productId=product_id,
        token=purchase_token
    ).execute()
    
    return result.get('purchaseState') == 0
```

## QR Code Authentication

### Generate QR Code
```python
def generate_qr_auth_code(user_id):
    qr_code_id = str(uuid.uuid4())
    
    # Store in DynamoDB with 5-minute TTL
    dynamodb.put_item(
        TableName='ielts-genai-prep-qr-auth',
        Item={
            'qr_code_id': {'S': qr_code_id},
            'user_id': {'S': user_id},
            'status': {'S': 'pending'},
            'expires_at': {'N': str(int(time.time()) + 300)}
        }
    )
    
    return qr_code_id
```

### Verify QR Code
```python
def verify_qr_code(qr_code_id, device_fingerprint):
    response = dynamodb.get_item(
        TableName='ielts-genai-prep-qr-auth',
        Key={'qr_code_id': {'S': qr_code_id}}
    )
    
    if response.get('Item') and response['Item']['status']['S'] == 'pending':
        # Update status and create web session
        update_qr_status(qr_code_id, 'verified')
        return create_web_session(response['Item']['user_id']['S'])
    
    return None
```

## Email Integration (AWS SES)

### Welcome Email
```python
def send_welcome_email(email, first_name):
    ses_client.send_email(
        Source='noreply@ieltsaiprep.com',
        Destination={'ToAddresses': [email]},
        Message={
            'Subject': {'Data': 'Welcome to IELTS GenAI Prep'},
            'Body': {
                'Html': {'Data': welcome_email_template.format(first_name=first_name)}
            }
        }
    )
```

### Account Deletion Confirmation
```python
def send_deletion_confirmation(email):
    ses_client.send_email(
        Source='noreply@ieltsaiprep.com',
        Destination={'ToAddresses': [email]},
        Message={
            'Subject': {'Data': 'Account Deletion Confirmed'},
            'Body': {
                'Html': {'Data': deletion_confirmation_template}
            }
        }
    )
```

## Error Handling and Logging

### Comprehensive Error Handling
```python
def handle_api_error(error, context):
    error_id = str(uuid.uuid4())
    
    # Log to CloudWatch
    logger.error(f"API Error {error_id}: {str(error)}", extra={
        'error_id': error_id,
        'context': context,
        'timestamp': datetime.utcnow().isoformat()
    })
    
    return {
        'statusCode': 500,
        'body': json.dumps({
            'error': 'Internal server error',
            'error_id': error_id
        })
    }
```

## Security Headers

### CloudFront Security
```python
def add_security_headers(response):
    response['headers'] = {
        'Content-Security-Policy': "default-src 'self'",
        'X-Frame-Options': 'DENY',
        'X-Content-Type-Options': 'nosniff',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'microphone=(self)',
        'Cache-Control': 'no-cache, no-store, must-revalidate'
    }
    return response
```

## Testing Integration

### Mock Services for Development
```python
# Use aws_mock_config.py for local testing
from aws_mock_config import MockAWSServices

if os.environ.get('ENVIRONMENT') != 'production':
    aws_services = MockAWSServices()
    dynamodb = aws_services.dynamodb
    bedrock = aws_services.bedrock
else:
    dynamodb = boto3.client('dynamodb')
    bedrock = boto3.client('bedrock-runtime')
```

## Rate Limiting and Throttling

### API Rate Limits
- Assessment attempts: 4 per purchased module
- QR code generation: 10 per hour per user
- Password reset: 3 per hour per email
- Account creation: 5 per hour per IP

### Bedrock Throttling
- Nova Sonic: 10 concurrent conversations
- Nova Micro: 100 requests per minute
- Automatic retry with exponential backoff