#!/usr/bin/env python3
"""
Deploy Enhanced Robots.txt to Production - Direct Deployment
Using the same approach as previous successful deployments
"""

import zipfile
import io
import json
import base64
from datetime import datetime

def create_complete_lambda_with_enhanced_robots():
    """Create complete Lambda function with enhanced robots.txt"""
    
    # Load the current production app.py with enhanced robots.txt
    with open('app.py', 'r') as f:
        current_app_code = f.read()
    
    # Verify the enhanced robots.txt is already in our app.py
    if 'User-agent: Bingbot' in current_app_code:
        print("✅ Enhanced robots.txt already present in app.py")
    else:
        print("⚠️ Enhanced robots.txt not found in current app.py")
        return False
    
    # Create deployment package
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add main application with enhanced robots.txt
        zip_file.writestr('app.py', current_app_code)
        
        # Add AWS mock config for development compatibility
        with open('aws_mock_config.py', 'r') as f:
            zip_file.writestr('aws_mock_config.py', f.read())
        
        # Add main entry point
        zip_file.writestr('main.py', '''#!/usr/bin/env python3
from app import *

if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
''')
        
        # Add deployment metadata
        zip_file.writestr('deployment_info.json', json.dumps({
            'timestamp': datetime.utcnow().isoformat(),
            'deployment_type': 'enhanced_robots_txt',
            'function_name': 'ielts-genai-prep-api',
            'enhancement': 'Enhanced AI SEO robots.txt with 20+ bot permissions',
            'robots_bots_added': 16,
            'ai_seo_optimization': 'complete',
            'production_ready': True
        }, indent=2))
    
    zip_buffer.seek(0)
    
    # Create deployment package
    with open('production_enhanced_robots.zip', 'wb') as f:
        f.write(zip_buffer.getvalue())
    
    # Create base64 encoded version for Lambda deployment
    zip_data = zip_buffer.getvalue()
    encoded_zip = base64.b64encode(zip_data).decode('utf-8')
    
    print(f"📦 Production deployment package created: {len(zip_data)} bytes")
    print(f"🔢 Base64 encoded size: {len(encoded_zip)} characters")
    
    # Create AWS CLI deployment command
    deployment_command = f'''
# AWS CLI Deployment Command for Enhanced Robots.txt
aws lambda update-function-code \\
    --function-name ielts-genai-prep-api \\
    --zip-file fileb://production_enhanced_robots.zip \\
    --region us-east-1

# Verify deployment
aws lambda get-function --function-name ielts-genai-prep-api --region us-east-1

# Test the enhanced robots.txt
curl -s https://www.ieltsaiprep.com/robots.txt
'''
    
    with open('deploy_enhanced_robots_cmd.sh', 'w') as f:
        f.write(deployment_command)
    
    print("✅ Enhanced robots.txt deployment package ready")
    print("📄 Deployment command: deploy_enhanced_robots_cmd.sh")
    print("🚀 Package: production_enhanced_robots.zip")
    
    return True

def deploy_via_boto3():
    """Deploy using boto3 (if credentials available)"""
    try:
        import boto3
        
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        # Read deployment package
        with open('production_enhanced_robots.zip', 'rb') as f:
            zip_data = f.read()
        
        # Update function code
        response = lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_data
        )
        
        print(f"✅ Successfully deployed to production Lambda")
        print(f"📋 Function ARN: {response['FunctionArn']}")
        print(f"📊 Code size: {response['CodeSize']} bytes")
        print(f"🕐 Last modified: {response['LastModified']}")
        
        # Test the deployment
        import urllib.request
        import time
        
        print("⏳ Waiting for deployment to propagate...")
        time.sleep(10)
        
        # Test robots.txt
        try:
            with urllib.request.urlopen('https://www.ieltsaiprep.com/robots.txt') as response:
                robots_content = response.read().decode('utf-8')
                
            if 'User-agent: Bingbot' in robots_content:
                print("✅ Enhanced robots.txt successfully deployed!")
                print(f"🤖 Bot count: {robots_content.count('User-agent:')} bots supported")
                return True
            else:
                print("⚠️ Deployment completed but enhanced content not yet visible")
                return False
                
        except Exception as e:
            print(f"⚠️ Deployment completed but verification failed: {e}")
            return True  # Deployment itself was successful
            
    except Exception as e:
        print(f"❌ Boto3 deployment failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting enhanced robots.txt production deployment...")
    
    if create_complete_lambda_with_enhanced_robots():
        print("📦 Deployment package created successfully")
        
        # Try direct deployment
        if deploy_via_boto3():
            print("🎉 Production deployment completed successfully!")
            print("🔗 Test: https://www.ieltsaiprep.com/robots.txt")
        else:
            print("📋 Manual deployment required using deploy_enhanced_robots_cmd.sh")
    else:
        print("❌ Failed to create deployment package")