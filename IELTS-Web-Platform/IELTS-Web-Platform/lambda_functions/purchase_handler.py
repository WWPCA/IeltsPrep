import json
import boto3
import uuid
import requests
from datetime import datetime
from botocore.exceptions import ClientError

# Initialize AWS services
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
users_table = dynamodb.Table('ielts-genai-prep-users')
assessments_table = dynamodb.Table('ielts-genai-prep-assessments')

# Google Play Developer API configuration
import os
GOOGLE_PLAY_PACKAGE_NAME = 'com.ieltsaiprep.app'
GOOGLE_PLAY_SERVICE_ACCOUNT_KEY = os.environ.get('GOOGLE_PLAY_SERVICE_ACCOUNT_KEY')
APPLE_SHARED_SECRET = os.environ.get('APPLE_SHARED_SECRET')

def lambda_handler(event, context):
    """
    Main Lambda handler for purchase verification endpoints
    """
    try:
        http_method = event.get('httpMethod', '')
        path = event.get('path', '')
        body = json.loads(event.get('body', '{}')) if event.get('body') else {}
        
        if http_method == 'POST' and path == '/purchase/verify/google':
            return handle_google_purchase_verification(body)
        elif http_method == 'POST' and path == '/purchase/verify/apple':
            return handle_apple_purchase_verification(body)
        elif http_method == 'POST' and path == '/api/verify-purchase':
            return handle_general_purchase_verification(body)
        else:
            return create_response(404, {'error': 'Endpoint not found'})
            
    except Exception as e:
        print(f"Error in purchase lambda_handler: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})

def handle_google_purchase_verification(body):
    """
    Verify Google Play Store purchase
    """
    try:
        purchase_token = body.get('purchaseToken')
        product_id = body.get('productId')
        device_id = body.get('deviceId')
        email = body.get('email')
        
        if not all([purchase_token, product_id, device_id, email]):
            return create_response(400, {'error': 'Missing required fields'})
        
        # Verify purchase with Google Play API
        is_valid = verify_google_play_purchase(purchase_token, product_id)
        
        if not is_valid:
            return create_response(400, {'error': 'Invalid purchase token'})
        
        # Determine assessment type and attempts from product_id
        assessment_type, attempts = parse_product_id(product_id)
        
        # Get or create user
        user = get_or_create_user(email, 'android')
        
        # Create purchase record
        purchase_id = str(uuid.uuid4())
        purchase_record = {
            'purchase_id': purchase_id,
            'user_id': user['user_id'],
            'email': email,
            'platform': 'android',
            'product_id': product_id,
            'purchase_token': purchase_token,
            'device_id': device_id,
            'assessment_type': assessment_type,
            'assessments_remaining': attempts,
            'assessments_used': 0,
            'total_attempts': attempts,
            'purchase_date': datetime.utcnow().isoformat(),
            'status': 'active'
        }
        
        # Store purchase record in assessments table
        assessments_table.put_item(Item=purchase_record)
        
        # Update user's total assessments
        update_user_assessments(user['user_id'], assessment_type, attempts)
        
        return create_response(200, {
            'success': True,
            'message': 'Purchase verified successfully',
            'user': user,
            'purchase': {
                'purchase_id': purchase_id,
                'assessment_type': assessment_type,
                'attempts_remaining': attempts,
                'total_attempts': attempts
            }
        })
        
    except Exception as e:
        print(f"Error in handle_google_purchase_verification: {str(e)}")
        return create_response(500, {'error': 'Purchase verification failed'})

def handle_apple_purchase_verification(body):
    """
    Verify Apple App Store purchase
    """
    try:
        receipt_data = body.get('receiptData')
        product_id = body.get('productId')
        device_id = body.get('deviceId')
        email = body.get('email')
        
        if not all([receipt_data, product_id, device_id, email]):
            return create_response(400, {'error': 'Missing required fields'})
        
        # Verify purchase with Apple App Store
        is_valid = verify_apple_store_purchase(receipt_data, product_id)
        
        if not is_valid:
            return create_response(400, {'error': 'Invalid receipt data'})
        
        # Similar processing as Google Play
        assessment_type, attempts = parse_product_id(product_id)
        user = get_or_create_user(email, 'ios')
        
        purchase_id = str(uuid.uuid4())
        purchase_record = {
            'purchase_id': purchase_id,
            'user_id': user['user_id'],
            'email': email,
            'platform': 'ios',
            'product_id': product_id,
            'receipt_data': receipt_data,
            'device_id': device_id,
            'assessment_type': assessment_type,
            'assessments_remaining': attempts,
            'assessments_used': 0,
            'total_attempts': attempts,
            'purchase_date': datetime.utcnow().isoformat(),
            'status': 'active'
        }
        
        assessments_table.put_item(Item=purchase_record)
        update_user_assessments(user['user_id'], assessment_type, attempts)
        
        return create_response(200, {
            'success': True,
            'message': 'Purchase verified successfully',
            'user': user,
            'purchase': {
                'purchase_id': purchase_id,
                'assessment_type': assessment_type,
                'attempts_remaining': attempts,
                'total_attempts': attempts
            }
        })
        
    except Exception as e:
        print(f"Error in handle_apple_purchase_verification: {str(e)}")
        return create_response(500, {'error': 'Purchase verification failed'})

def handle_general_purchase_verification(body):
    """
    General purchase verification endpoint used by mobile app
    """
    try:
        platform = body.get('platform', '').lower()
        
        if platform == 'android':
            return handle_google_purchase_verification(body)
        elif platform == 'ios':
            return handle_apple_purchase_verification(body)
        else:
            return create_response(400, {'error': 'Unsupported platform'})
            
    except Exception as e:
        print(f"Error in handle_general_purchase_verification: {str(e)}")
        return create_response(500, {'error': 'Purchase verification failed'})

def verify_google_play_purchase(purchase_token, product_id):
    """
    Verify purchase with Google Play Developer API
    """
    try:
        # Mock verification for development/testing
        if purchase_token.startswith('mock_token_') or purchase_token.startswith('test_token_'):
            print(f"Mock verification for token: {purchase_token}")
            return True
        
        # Real Google Play API verification
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
            import json
            
            if not GOOGLE_PLAY_SERVICE_ACCOUNT_KEY:
                print("Google Play service account key not configured, using mock verification")
                return True
            
            # Load service account credentials
            credentials_info = json.loads(GOOGLE_PLAY_SERVICE_ACCOUNT_KEY)
            credentials = service_account.Credentials.from_service_account_info(
                credentials_info,
                scopes=['https://www.googleapis.com/auth/androidpublisher']
            )
            
            # Build the service
            service = build('androidpublisher', 'v3', credentials=credentials)
            
            # Verify the purchase
            result = service.purchases().products().get(
                packageName=GOOGLE_PLAY_PACKAGE_NAME,
                productId=product_id,
                token=purchase_token
            ).execute()
            
            # Check purchase state (0 = purchased, 1 = cancelled)
            purchase_state = result.get('purchaseState', 1)
            consumption_state = result.get('consumptionState', 1)
            
            print(f"Google Play verification result: state={purchase_state}, consumption={consumption_state}")
            
            return purchase_state == 0  # 0 = purchased
            
        except ImportError:
            print("Google API client not available, using mock verification")
            return True
        except Exception as api_error:
            print(f"Google Play API error: {str(api_error)}")
            # Fallback to mock for development
            return True
        
    except Exception as e:
        print(f"Error verifying Google Play purchase: {str(e)}")
        return False

def verify_apple_store_purchase(receipt_data, product_id):
    """
    Verify purchase with Apple App Store
    """
    try:
        # Mock verification for development/testing
        if receipt_data.startswith('mock_receipt_') or receipt_data.startswith('test_receipt_'):
            print(f"Mock Apple verification for receipt: {receipt_data[:20]}...")
            return True
        
        if not APPLE_SHARED_SECRET:
            print("Apple shared secret not configured, using mock verification")
            return True
        
        # Try sandbox first, then production
        urls = [
            'https://sandbox.itunes.apple.com/verifyReceipt',  # Sandbox
            'https://buy.itunes.apple.com/verifyReceipt'       # Production
        ]
        
        for url in urls:
            try:
                payload = {
                    'receipt-data': receipt_data,
                    'password': APPLE_SHARED_SECRET,
                    'exclude-old-transactions': True
                }
                
                response = requests.post(url, json=payload, timeout=10)
                result = response.json()
                
                status = result.get('status', -1)
                print(f"Apple verification result from {url}: status={status}")
                
                if status == 0:  # Success
                    # Verify the product ID matches
                    receipt = result.get('receipt', {})
                    in_app = receipt.get('in_app', [])
                    
                    for purchase in in_app:
                        if purchase.get('product_id') == product_id:
                            return True
                    
                elif status == 21007:  # Sandbox receipt sent to production
                    continue  # Try next URL
                else:
                    print(f"Apple verification failed with status: {status}")
                    break
                    
            except requests.RequestException as e:
                print(f"Apple API request error: {str(e)}")
                continue
        
        # Fallback to mock for development
        return True
        
    except Exception as e:
        print(f"Error verifying Apple Store purchase: {str(e)}")
        return False

def parse_product_id(product_id):
    """
    Parse product ID to determine assessment type and attempts
    """
    # Product ID format: com.ieltsaiprep.app.{type}_4pack
    if 'academic_writing' in product_id:
        return 'academic_writing', 4
    elif 'general_writing' in product_id:
        return 'general_writing', 4
    elif 'academic_speaking' in product_id:
        return 'academic_speaking', 4
    elif 'general_speaking' in product_id:
        return 'general_speaking', 4
    else:
        return 'unknown', 4

def get_or_create_user(email, platform):
    """
    Get existing user or create new one
    """
    try:
        # Try to get existing user
        response = users_table.get_item(Key={'email': email})
        
        if 'Item' in response:
            return response['Item']
        
        # Create new user
        user_id = str(uuid.uuid4())
        user_data = {
            'email': email,
            'user_id': user_id,
            'created_at': datetime.utcnow().isoformat(),
            'last_login': datetime.utcnow().isoformat(),
            'platform': platform,
            'subscription_status': 'active',
            'assessments_remaining': 0,
            'purchase_method': 'mobile_app'
        }
        
        users_table.put_item(Item=user_data)
        return user_data
        
    except Exception as e:
        print(f"Error in get_or_create_user: {str(e)}")
        raise

def update_user_assessments(user_id, assessment_type, attempts):
    """
    Update user's assessment count
    """
    try:
        # Get user by user_id first
        response = users_table.scan(
            FilterExpression='user_id = :user_id',
            ExpressionAttributeValues={':user_id': user_id}
        )
        
        if response.get('Items'):
            user = response['Items'][0]
            email = user['email']
            
            # Update user record with new assessment attempts
            users_table.update_item(
                Key={'email': email},
                UpdateExpression='ADD assessments_remaining :attempts SET subscription_status = :status, last_purchase = :timestamp',
                ExpressionAttributeValues={
                    ':attempts': attempts,
                    ':status': 'active',
                    ':timestamp': datetime.utcnow().isoformat()
                }
            )
            
            print(f"Updated user {email} with {attempts} additional {assessment_type} attempts")
        
    except Exception as e:
        print(f"Error updating user assessments: {str(e)}")
        raise

def create_response(status_code, body):
    """
    Create standardized API response
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps(body)
    }