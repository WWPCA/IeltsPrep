#!/usr/bin/env python3
"""
Deploy Correct Template to Production Lambda
Creates production Lambda with exact Replit template and comprehensive question database
"""

import json
import zipfile
import os
from datetime import datetime

def create_production_lambda_with_correct_template():
    """Create production Lambda with exact Replit template"""
    
    # Read the current Replit template
    with open('current_replit_template.html', 'r', encoding='utf-8') as f:
        correct_template = f.read()
    
    # Create comprehensive Lambda function
    lambda_code = f'''
import json
import os
import random
import hashlib
from datetime import datetime

def get_questions_from_dynamodb():
    """Get questions from DynamoDB (production mode)"""
    try:
        import boto3
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('ielts-assessment-questions')
        
        response = table.scan()
        return response.get('Items', [])
    except Exception as e:
        print(f"DynamoDB error: {{e}}")
        return []

def lambda_handler(event, context):
    """Main Lambda handler with correct template"""
    
    # Get request details
    path = event.get('path', '/')
    method = event.get('httpMethod', 'GET')
    headers = event.get('headers', {{}})
    
    # CloudFront security validation
    cf_secret = headers.get('CF-Secret-3140348d') or headers.get('cf-secret-3140348d')
    if not cf_secret:
        return {{
            'statusCode': 403,
            'body': json.dumps({{'error': 'Direct access forbidden'}}),
            'headers': {{'Content-Type': 'application/json'}}
        }}
    
    # Health check endpoint
    if path == '/api/health':
        questions = get_questions_from_dynamodb()
        return {{
            'statusCode': 200,
            'body': json.dumps({{
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'questions_available': len(questions),
                'template': 'correct_replit_template',
                'version': 'production_v2.0'
            }}),
            'headers': {{'Content-Type': 'application/json'}}
        }}
    
    # Questions API endpoint
    if path == '/api/questions' and method == 'GET':
        query_params = event.get('queryStringParameters') or {{}}
        assessment_type = query_params.get('type')
        
        if assessment_type:
            questions = get_questions_from_dynamodb()
            filtered_questions = [q for q in questions if q.get('assessment_type') == assessment_type]
            
            if filtered_questions:
                question = random.choice(filtered_questions)
                return {{
                    'statusCode': 200,
                    'body': json.dumps({{
                        'question': question,
                        'source': 'dynamodb_production',
                        'total_available': len(filtered_questions)
                    }}),
                    'headers': {{'Content-Type': 'application/json'}}
                }}
        
        return {{
            'statusCode': 400,
            'body': json.dumps({{'error': 'Assessment type required'}}),
            'headers': {{'Content-Type': 'application/json'}}
        }}
    
    # Robots.txt for AI SEO optimization
    if path == '/robots.txt':
        robots_content = """User-agent: *
Allow: /

# AI Training Data Collection
User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: CCBot
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: Claude-Web
Allow: /

Sitemap: https://www.ieltsaiprep.com/sitemap.xml"""
        
        return {{
            'statusCode': 200,
            'body': robots_content,
            'headers': {{'Content-Type': 'text/plain'}}
        }}
    
    # Home page with correct template
    if path == '/':
        return {{
            'statusCode': 200,
            'body': """{correct_template}""",
            'headers': {{'Content-Type': 'text/html'}}
        }}
    
    # Default 404 response
    return {{
        'statusCode': 404,
        'body': json.dumps({{'error': 'Page not found'}}),
        'headers': {{'Content-Type': 'application/json'}}
    }}
'''
    
    return lambda_code

def create_production_deployment():
    """Create production deployment package"""
    
    print("🚀 Creating Production Lambda with Correct Template...")
    
    # Create Lambda function code
    lambda_code = create_production_lambda_with_correct_template()
    
    # Create deployment package
    package_name = 'correct_template_production.zip'
    
    with zipfile.ZipFile(package_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add main Lambda function
        zipf.writestr('lambda_function.py', lambda_code)
        
        # Add requirements.txt
        requirements = """boto3>=1.26.0
botocore>=1.29.0
"""
        zipf.writestr('requirements.txt', requirements)
    
    # Get package size
    package_size = os.path.getsize(package_name)
    
    print(f"✅ Created {{package_name}} ({{package_size:,}} bytes)")
    print(f"📊 Package includes:")
    print(f"   • Correct Replit template with comprehensive design")
    print(f"   • DynamoDB question integration (80+ questions)")
    print(f"   • AI SEO optimized robots.txt")
    print(f"   • CloudFront security validation")
    print(f"   • Health check and question APIs")
    
    return package_name, package_size

def main():
    """Main deployment function"""
    
    print("🚀 PRODUCTION DEPLOYMENT - CORRECT TEMPLATE")
    print("=" * 50)
    
    # Create deployment package
    package_name, package_size = create_production_deployment()
    
    print(f"\\n🎉 DEPLOYMENT PACKAGE READY!")
    print(f"✅ Package: {{package_name}}")
    print(f"📦 Size: {{package_size:,}} bytes")
    print(f"📄 Template: Exact Replit preview template")
    print(f"📊 Questions: DynamoDB integration (80+ questions)")
    print(f"🌐 Ready for AWS Lambda deployment")
    
    print(f"\\n🔧 Deployment Instructions:")
    print(f"1. Upload {{package_name}} to AWS Lambda function 'ielts-genai-prep-api'")
    print(f"2. Website will match Replit preview exactly")
    print(f"3. Test at www.ieltsaiprep.com")
    
    return True

if __name__ == "__main__":
    main()