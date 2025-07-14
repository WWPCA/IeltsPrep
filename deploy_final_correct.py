#!/usr/bin/env python3
"""
Deploy the CORRECT version with working_template.html that has comprehensive FAQs
"""

import boto3
import json
import zipfile
import io

def deploy_final_correct():
    """Deploy the correct version using working_template.html"""
    
    # Read the working_template.html with comprehensive FAQs
    with open('working_template.html', 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Create simple Lambda function that serves this template
    lambda_code = '''
import json

def lambda_handler(event, context):
    try:
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        headers = event.get('headers', {})
        
        # Check CloudFront security header
        cf_secret = headers.get('cf-secret', '')
        if cf_secret != 'CF-Secret-3140348d':
            return {
                'statusCode': 403,
                'body': json.dumps({'error': 'Forbidden - Direct access not allowed'})
            }
        
        if path == '/':
            return handle_home_page()
        elif path == '/login':
            return handle_login_page()
        elif path == '/privacy-policy':
            return handle_privacy_policy()
        elif path == '/terms-of-service':
            return handle_terms_of_service()
        elif path == '/dashboard':
            return handle_dashboard()
        elif path == '/robots.txt':
            return handle_robots_txt()
        else:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'text/html'},
                'body': '<h1>Page not found</h1>'
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': '<h1>Internal server error</h1>'
        }

def handle_home_page():
    """Serve the CORRECT home page with comprehensive FAQs"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': """''' + template_content + '''"""
    }

def handle_login_page():
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '<h1>Login</h1><p>Login page</p>'
    }

def handle_privacy_policy():
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '<h1>Privacy Policy</h1>'
    }

def handle_terms_of_service():
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '<h1>Terms of Service</h1>'
    }

def handle_dashboard():
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '<h1>Dashboard</h1>'
    }

def handle_robots_txt():
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/plain'},
        'body': 'User-agent: *\\nAllow: /'
    }
'''
    
    # Create deployment zip
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
    
    zip_buffer.seek(0)
    zip_content = zip_buffer.read()
    
    try:
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        # Update function code
        response = lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_content
        )
        
        print(f"✅ CORRECT version deployed successfully!")
        print(f"Function: {response['FunctionName']}")
        print(f"Last Modified: {response['LastModified']}")
        print(f"Code Size: {response['CodeSize']} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = deploy_final_correct()
    if success:
        print("\\n✅ CORRECT VERSION DEPLOYED!")
        print("🌐 Website: https://www.ieltsaiprep.com")
        print("📚 Comprehensive FAQs from working_template.html")
        print("📊 Academic Writing Assessment Sample included")
    else:
        print("\\n❌ DEPLOYMENT FAILED")