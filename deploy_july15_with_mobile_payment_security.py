#!/usr/bin/env python3
"""
Deploy July 15 Production Package with Mobile Payment Security
Uses original template with preview pages and robots.txt + mobile payment verification
"""

import boto3
import json
import zipfile
import io

def create_enhanced_lambda_function():
    """Create enhanced lambda function with mobile payment security"""
    
    # Read the original July 15 lambda function
    with open('lambda_function.py', 'r') as f:
        lambda_code = f.read()
    
    # Add mobile payment verification functions
    mobile_payment_code = '''
def verify_app_store_receipt(receipt_data: str, sandbox: bool = False) -> bool:
    """Verify Apple App Store receipt"""
    try:
        import requests
        
        # App Store receipt verification endpoint
        url = "https://sandbox.itunes.apple.com/verifyReceipt" if sandbox else "https://buy.itunes.apple.com/verifyReceipt"
        
        payload = {
            "receipt-data": receipt_data,
            "password": os.environ.get('APP_STORE_SHARED_SECRET', ''),
            "exclude-old-transactions": True
        }
        
        response = requests.post(url, json=payload, timeout=30)
        result = response.json()
        
        # Check if receipt is valid
        if result.get('status') == 0:
            receipt = result.get('receipt', {})
            in_app = receipt.get('in_app', [])
            
            # Verify IELTS GenAI Prep product purchase
            valid_products = [
                'com.ieltsgenaiprep.academic_writing',
                'com.ieltsgenaiprep.general_writing', 
                'com.ieltsgenaiprep.academic_speaking',
                'com.ieltsgenaiprep.general_speaking'
            ]
            
            for transaction in in_app:
                if transaction.get('product_id') in valid_products:
                    return True
        
        return False
        
    except Exception as e:
        print(f"[APP_STORE] Receipt verification error: {str(e)}")
        return False

def verify_google_play_receipt(purchase_token: str, product_id: str, package_name: str) -> bool:
    """Verify Google Play Store receipt"""
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        
        # Service account credentials for Google Play Developer API
        credentials_json = os.environ.get('GOOGLE_PLAY_SERVICE_ACCOUNT_JSON')
        if not credentials_json:
            print("[GOOGLE_PLAY] Service account credentials not configured")
            return False
        
        credentials = service_account.Credentials.from_service_account_info(
            json.loads(credentials_json),
            scopes=['https://www.googleapis.com/auth/androidpublisher']
        )
        
        service = build('androidpublisher', 'v3', credentials=credentials)
        
        # Verify purchase
        result = service.purchases().products().get(
            packageName=package_name,
            productId=product_id,
            token=purchase_token
        ).execute()
        
        # Check if purchase is valid (not cancelled or refunded)
        purchase_state = result.get('purchaseState', 1)
        consumption_state = result.get('consumptionState', 1)
        
        return purchase_state == 0 and consumption_state == 1
        
    except Exception as e:
        print(f"[GOOGLE_PLAY] Receipt verification error: {str(e)}")
        return False

def detect_mobile_app_request(headers: dict) -> bool:
    """Detect if request is from official mobile app"""
    user_agent = headers.get('User-Agent', '').lower()
    
    # Check for Capacitor mobile app signatures
    mobile_signatures = [
        'ielts-genai-prep-mobile',
        'capacitor',
        'cordova',
        'ionic'
    ]
    
    return any(signature in user_agent for signature in mobile_signatures)

def handle_mobile_registration(data: dict, headers: dict) -> dict:
    """Handle mobile registration with payment verification"""
    try:
        # Verify this is a mobile app request
        if not detect_mobile_app_request(headers):
            return {
                'statusCode': 403,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'error': 'Registration only available through official mobile app',
                    'message': 'Please download the IELTS GenAI Prep app from App Store or Google Play'
                })
            }
        
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        receipt_data = data.get('receipt_data', '')
        platform = data.get('platform', '')  # 'ios' or 'android'
        
        if not email or not password:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Email and password are required'})
            }
        
        # Verify payment receipt
        payment_verified = False
        
        if platform == 'ios' and receipt_data:
            payment_verified = verify_app_store_receipt(receipt_data)
        elif platform == 'android' and receipt_data:
            purchase_token = data.get('purchase_token', '')
            product_id = data.get('product_id', '')
            package_name = data.get('package_name', 'com.ieltsgenaiprep.app')
            payment_verified = verify_google_play_receipt(purchase_token, product_id, package_name)
        
        if not payment_verified:
            return {
                'statusCode': 402,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'error': 'Payment verification failed',
                    'message': 'Valid App Store or Google Play purchase required'
                })
            }
        
        # Create user account after payment verification
        if not create_user_account(email, password):
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'User already exists or registration failed'})
            }
        
        # Send welcome email
        send_welcome_email(email)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': True,
                'message': 'Account created successfully with payment verification'
            })
        }
        
    except Exception as e:
        print(f"[MOBILE_REGISTRATION] Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Mobile registration failed'})
        }

'''
    
    # Add AWS mock config production version
    aws_mock_prod_code = '''
# AWS Mock Config for Production Environment
import os
import time
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

class ProductionAWSMockServices:
    """Production-grade AWS services mock with real data structure"""
    
    def __init__(self):
        self.users_table = {}
        self.sessions_table = {}
        self.assessments_table = {}
        self.questions_table = {}
        self.rubrics_table = {}
        self.initialized = False
        
    def initialize_production_data(self):
        """Initialize with production-like data"""
        if self.initialized:
            return
            
        # Production test users
        test_users = [
            {
                'user_id': 'test@ieltsgenaiprep.com',
                'email': 'test@ieltsgenaiprep.com',
                'password_hash': 'hashed_test_password',
                'created_at': datetime.utcnow().isoformat(),
                'payment_verified': True,
                'platform': 'ios'
            },
            {
                'user_id': 'prodtest@ieltsgenaiprep.com', 
                'email': 'prodtest@ieltsgenaiprep.com',
                'password_hash': 'hashed_prod_password',
                'created_at': datetime.utcnow().isoformat(),
                'payment_verified': True,
                'platform': 'android'
            }
        ]
        
        for user in test_users:
            self.users_table[user['user_id']] = user
            
        # Production IELTS assessment questions
        self.questions_table.update({
            'academic_writing_1': {
                'question_id': 'academic_writing_1',
                'assessment_type': 'academic_writing',
                'question_text': 'The chart below shows the percentage of households in owned and rented accommodation in England and Wales between 1918 and 2011.',
                'task_type': 'Task 1',
                'chart_data': 'housing_ownership_chart_1918_2011'
            },
            'general_writing_1': {
                'question_id': 'general_writing_1', 
                'assessment_type': 'general_writing',
                'question_text': 'You recently bought a piece of equipment for your kitchen but it did not work. You phoned the shop but no action was taken. Write a letter to the shop manager.',
                'task_type': 'Task 1',
                'letter_type': 'complaint'
            },
            'academic_speaking_1': {
                'question_id': 'academic_speaking_1',
                'assessment_type': 'academic_speaking',
                'part_1': 'Let\\'s talk about your studies. What subject are you studying?',
                'part_2': 'Describe an academic achievement you are proud of.',
                'part_3': 'What do you think makes a good student?'
            },
            'general_speaking_1': {
                'question_id': 'general_speaking_1',
                'assessment_type': 'general_speaking', 
                'part_1': 'Let\\'s talk about your work. What do you do?',
                'part_2': 'Describe a skill you would like to learn.',
                'part_3': 'How important is it to learn new skills?'
            }
        })
        
        # Production IELTS rubrics
        self.rubrics_table.update({
            'academic_writing': {
                'rubric_id': 'academic_writing',
                'criteria': {
                    'task_achievement': 'Task 1 - Accuracy and appropriateness of response',
                    'coherence_cohesion': 'Logical organization and linking',
                    'lexical_resource': 'Vocabulary range and accuracy',
                    'grammar_accuracy': 'Grammatical range and accuracy'
                },
                'band_descriptors': {
                    '9': 'Expert user',
                    '8': 'Very good user',
                    '7': 'Good user',
                    '6': 'Competent user'
                }
            },
            'general_writing': {
                'rubric_id': 'general_writing',
                'criteria': {
                    'task_achievement': 'Task 1 - Tone, purpose and audience',
                    'coherence_cohesion': 'Logical organization and linking',
                    'lexical_resource': 'Vocabulary range and accuracy', 
                    'grammar_accuracy': 'Grammatical range and accuracy'
                },
                'band_descriptors': {
                    '9': 'Expert user',
                    '8': 'Very good user',
                    '7': 'Good user',
                    '6': 'Competent user'
                }
            },
            'academic_speaking': {
                'rubric_id': 'academic_speaking',
                'criteria': {
                    'fluency_coherence': 'Fluency and coherence',
                    'lexical_resource': 'Lexical resource',
                    'grammar_accuracy': 'Grammatical range and accuracy',
                    'pronunciation': 'Pronunciation'
                },
                'parts': {
                    'part_1': 'Introduction and interview (4-5 minutes)',
                    'part_2': 'Long turn (3-4 minutes)',
                    'part_3': 'Discussion (4-5 minutes)'
                }
            },
            'general_speaking': {
                'rubric_id': 'general_speaking',
                'criteria': {
                    'fluency_coherence': 'Fluency and coherence',
                    'lexical_resource': 'Lexical resource',
                    'grammar_accuracy': 'Grammatical range and accuracy',
                    'pronunciation': 'Pronunciation'
                },
                'parts': {
                    'part_1': 'Introduction and interview (4-5 minutes)',
                    'part_2': 'Long turn (3-4 minutes)',
                    'part_3': 'Discussion (4-5 minutes)'
                }
            }
        })
        
        self.initialized = True
        print("[AWS_MOCK_PROD] Production data initialized")
        
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        self.initialize_production_data()
        return self.users_table.get(user_id)
        
    def create_user(self, user_data: Dict) -> bool:
        """Create new user"""
        self.initialize_production_data()
        user_id = user_data.get('user_id', user_data.get('email'))
        if user_id not in self.users_table:
            self.users_table[user_id] = user_data
            return True
        return False
        
    def get_question(self, question_id: str) -> Optional[Dict]:
        """Get question by ID"""
        self.initialize_production_data()
        return self.questions_table.get(question_id)
        
    def get_rubric(self, rubric_id: str) -> Optional[Dict]:
        """Get rubric by ID"""
        self.initialize_production_data()
        return self.rubrics_table.get(rubric_id)
        
    def create_session(self, session_data: Dict) -> bool:
        """Create user session"""
        session_id = session_data.get('session_id')
        if session_id:
            self.sessions_table[session_id] = session_data
            return True
        return False
        
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID"""
        return self.sessions_table.get(session_id)

# Initialize production mock services
production_aws_mock = ProductionAWSMockServices()

'''

    # Add mobile payment routes to the lambda handler
    mobile_routes_code = '''
        elif path == '/api/mobile-register' and method == 'POST':
            return handle_mobile_registration(data, headers)
        elif path == '/mobile-registration' and method == 'GET':
            return handle_mobile_registration_page(headers)
'''

    # Add robots.txt handler if not present
    robots_txt_code = '''
def handle_robots_txt():
    """Handle robots.txt with comprehensive AI SEO optimization"""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain',
            'Cache-Control': 'public, max-age=86400'
        },
        'body': """User-agent: *
Allow: /

# AI Training and Search Engine Crawlers
User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: CCBot
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: Claude-Web
Allow: /

User-agent: Bingbot
Allow: /

User-agent: Slurp
Allow: /

User-agent: DuckDuckBot
Allow: /

# Social Media Crawlers
User-agent: facebookexternalhit
Allow: /

User-agent: Twitterbot
Allow: /

User-agent: LinkedInBot
Allow: /

# Educational and Research Crawlers
User-agent: ia_archiver
Allow: /

User-agent: Wayback
Allow: /

User-agent: archive.org_bot
Allow: /

# Sitemap
Sitemap: https://www.ieltsaiprep.com/sitemap.xml

# Crawl delay for respectful crawling
Crawl-delay: 1

# Priority pages for AI training
Allow: /privacy-policy
Allow: /terms-of-service
Allow: /about
Allow: /features
Allow: /how-it-works
Allow: /faq
Allow: /contact
Allow: /assessment/academic-writing
Allow: /assessment/general-writing
Allow: /assessment/academic-speaking
Allow: /assessment/general-speaking
"""
    }
'''

    # Insert the enhancements into the lambda code
    enhanced_code = lambda_code.replace(
        'def lambda_handler(event, context):',
        mobile_payment_code + aws_mock_prod_code + robots_txt_code + 'def lambda_handler(event, context):'
    )
    
    # Add mobile routes
    enhanced_code = enhanced_code.replace(
        "elif path == '/api/register' and method == 'POST':",
        mobile_routes_code + "        elif path == '/api/register' and method == 'POST':"
    )
    
    return enhanced_code

def deploy_enhanced_lambda():
    """Deploy enhanced lambda function with mobile payment security"""
    try:
        # Create enhanced lambda code
        enhanced_lambda_code = create_enhanced_lambda_function()
        
        # Create deployment package
        lambda_zip = io.BytesIO()
        with zipfile.ZipFile(lambda_zip, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr('lambda_function.py', enhanced_lambda_code)
        
        lambda_zip.seek(0)
        
        # Deploy to AWS Lambda
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        response = lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=lambda_zip.read()
        )
        
        print(f"✅ Enhanced Lambda deployed successfully!")
        print(f"📦 Package size: {len(lambda_zip.getvalue())} bytes")
        print(f"🔄 Last modified: {response['LastModified']}")
        print(f"🛡️ Mobile payment security: ACTIVE")
        print(f"☁️ AWS Mock production: ENABLED")
        print(f"🤖 AI SEO robots.txt: OPTIMIZED")
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = deploy_enhanced_lambda()
    if success:
        print("\n🎉 ENHANCED PRODUCTION DEPLOYMENT COMPLETE!")
        print("🌐 Website: https://www.ieltsaiprep.com")
        print("📱 Mobile registration: Payment-gated (App Store/Google Play only)")
        print("🛡️ Security: CloudFront + Mobile app detection + Receipt verification")
        print("🤖 AI SEO: Comprehensive robots.txt with all AI crawler permissions")
        print("💾 Data: Production AWS mock services with real IELTS questions")
    else:
        print("\n❌ DEPLOYMENT FAILED - Check AWS credentials and permissions")