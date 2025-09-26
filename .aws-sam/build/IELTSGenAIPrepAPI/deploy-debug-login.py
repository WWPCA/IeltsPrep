#!/usr/bin/env python3
"""
Deploy minimal debug Lambda to identify login issue
"""
import boto3
import zipfile
import os

def create_debug_lambda():
    """Create minimal debug Lambda"""
    
    lambda_code = '''import json
import hashlib
from datetime import datetime

def lambda_handler(event, context):
    """Debug Lambda handler"""
    try:
        method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        body = event.get('body', '')
        
        print(f"DEBUG: {method} {path}")
        print(f"DEBUG: Body: {body}")
        
        if path == '/api/login' and method == 'POST':
            try:
                data = json.loads(body) if body else {}
                email = data.get('email', '').strip().lower()
                password = data.get('password', '')
                
                print(f"DEBUG: Email: {email}")
                print(f"DEBUG: Password length: {len(password)}")
                
                # Test credentials check
                if email == 'test@ieltsgenaiprep.com' and password == 'testpassword123':
                    print("DEBUG: Credentials match!")
                    return {
                        'statusCode': 200,
                        'headers': {'Content-Type': 'application/json'},
                        'body': json.dumps({'success': True, 'message': 'Login successful'})
                    }
                else:
                    print(f"DEBUG: Credentials don't match - got {email} / {password}")
                    return {
                        'statusCode': 401,
                        'headers': {'Content-Type': 'application/json'},
                        'body': json.dumps({'success': False, 'message': 'Invalid credentials'})
                    }
            except Exception as e:
                print(f"DEBUG: Login error: {e}")
                return {
                    'statusCode': 500,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'success': False, 'message': str(e)})
                }
        elif path == '/login':
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/html'},  
                'body': """<!DOCTYPE html>
<html><head><title>Debug Login</title></head>
<body>
<h1>Debug Login</h1>
<div id="result"></div>
<script>
fetch('/api/login', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({email: 'test@ieltsgenaiprep.com', password: 'testpassword123'})
}).then(r => r.json()).then(data => {
    document.getElementById('result').innerHTML = JSON.stringify(data);
});
</script>
</body></html>"""
            }
        elif path == '/health':
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'status': 'debug', 'timestamp': datetime.utcnow().isoformat()})
            }
        else:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/html'},
                'body': f'<h1>Debug: {method} {path}</h1><a href="/login">Login</a>'
            }
            
    except Exception as e:
        print(f"DEBUG: Handler error: {e}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }'''
    
    with zipfile.ZipFile('lambda-debug.zip', 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
    
    return 'lambda-debug.zip'

def deploy_debug():
    """Deploy debug Lambda"""
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    try:
        zip_path = create_debug_lambda()
        
        with open(zip_path, 'rb') as f:
            zip_content = f.read()
        
        print("Deploying debug Lambda...")
        
        lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_content
        )
        
        waiter = lambda_client.get_waiter('function_updated')
        waiter.wait(FunctionName='ielts-genai-prep-api')
        
        os.remove(zip_path)
        print("Debug Lambda deployed!")
        return True
        
    except Exception as e:
        print(f"Deploy failed: {e}")
        return False

if __name__ == "__main__":
    deploy_debug()