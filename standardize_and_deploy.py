#!/usr/bin/env python3
"""
Standardize DynamoDB questions and deploy correct template
"""

import boto3
import json
import zipfile
import os
from datetime import datetime

def standardize_dynamodb_questions():
    """Standardize assessment_type naming in DynamoDB"""
    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('ielts-assessment-questions')
        
        print("🔧 Standardizing DynamoDB question naming...")
        
        # Scan all items
        response = table.scan()
        items = response['Items']
        
        # Mapping for standardization
        type_mapping = {
            'academic-writing': 'academic_writing',
            'general-writing': 'general_writing',
            'academic-speaking': 'academic_speaking',
            'general-speaking': 'general_speaking'
        }
        
        updated_count = 0
        for item in items:
            current_type = item.get('assessment_type')
            if current_type in type_mapping:
                # Update to standardized format
                item['assessment_type'] = type_mapping[current_type]
                table.put_item(Item=item)
                updated_count += 1
        
        print(f"✅ Standardized {updated_count} question types")
        
        # Verify final count
        final_response = table.scan()
        final_items = final_response['Items']
        
        type_counts = {}
        for item in final_items:
            assessment_type = item.get('assessment_type', 'unknown')
            type_counts[assessment_type] = type_counts.get(assessment_type, 0) + 1
        
        print(f"📊 Final DynamoDB Status:")
        print(f"   Total questions: {len(final_items)}")
        for type_name, count in type_counts.items():
            print(f"     • {type_name}: {count}")
        
        return len(final_items)
        
    except Exception as e:
        print(f"❌ Error standardizing DynamoDB: {e}")
        return 0

def create_correct_template_deployment():
    """Create deployment with correct template and standardized questions"""
    
    # Read the current Replit template
    with open('current_replit_template.html', 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Escape the template for Python string
    escaped_template = template_content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
    
    lambda_code = f'''
import json
import os
import random
from datetime import datetime

def get_questions_from_dynamodb():
    """Get questions from DynamoDB with standardized types"""
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
    """Main Lambda handler with correct template and question integration"""
    
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
        
        # Count by standardized types
        type_counts = {{}}
        for q in questions:
            assessment_type = q.get('assessment_type', 'unknown')
            type_counts[assessment_type] = type_counts.get(assessment_type, 0) + 1
        
        return {{
            'statusCode': 200,
            'body': json.dumps({{
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'questions_total': len(questions),
                'questions_by_type': type_counts,
                'template': 'correct_replit_template',
                'version': 'standardized_production_v1.0'
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
                        'source': 'dynamodb_standardized',
                        'total_available': len(filtered_questions),
                        'assessment_type': assessment_type
                    }}),
                    'headers': {{'Content-Type': 'application/json'}}
                }}
        
        return {{
            'statusCode': 400,
            'body': json.dumps({{'error': 'Assessment type required'}}),
            'headers': {{'Content-Type': 'application/json'}}
        }}
    
    # Robots.txt for AI SEO
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
    
    # Home page with exact Replit template
    if path == '/':
        return {{
            'statusCode': 200,
            'body': "{escaped_template}",
            'headers': {{'Content-Type': 'text/html'}}
        }}
    
    # Default 404 response
    return {{
        'statusCode': 404,
        'body': json.dumps({{'error': 'Page not found'}}),
        'headers': {{'Content-Type': 'application/json'}}
    }}
'''
    
    # Create deployment package
    package_name = 'standardized_production_lambda.zip'
    
    with zipfile.ZipFile(package_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr('lambda_function.py', lambda_code)
        zipf.writestr('requirements.txt', 'boto3>=1.26.0\\nbotocore>=1.29.0')
    
    package_size = os.path.getsize(package_name)
    
    print(f"\\n✅ Created {package_name} ({package_size:,} bytes)")
    print(f"📄 Includes: Exact Replit template + Standardized question database")
    
    return package_name, package_size

def main():
    """Main deployment function"""
    print("🚀 STANDARDIZING DYNAMODB & DEPLOYING CORRECT TEMPLATE")
    print("=" * 60)
    
    # Standardize DynamoDB questions
    question_count = standardize_dynamodb_questions()
    
    # Create deployment package
    package_name, package_size = create_correct_template_deployment()
    
    print(f"\\n🎉 PRODUCTION DEPLOYMENT READY!")
    print(f"📊 DynamoDB: {question_count} questions with standardized types")
    print(f"📦 Package: {package_name} ({package_size:,} bytes)")
    print(f"📄 Template: Exact Replit preview match")
    print(f"🌐 Ready for AWS Lambda deployment")
    
    print(f"\\n🔧 Next Steps:")
    print(f"1. Upload {package_name} to AWS Lambda function 'ielts-genai-prep-api'")
    print(f"2. Website will match Replit preview exactly")
    print(f"3. Test at www.ieltsaiprep.com")

if __name__ == "__main__":
    main()