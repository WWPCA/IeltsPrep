#!/usr/bin/env python3
"""
Fix Production Deployment - Deploy Working Version with Enhanced Robots.txt
"""

import boto3
import json
import zipfile
import io
import base64
from datetime import datetime

def create_working_production_package():
    """Create a working production package with enhanced robots.txt"""
    
    # Load current working app.py
    with open('app.py', 'r') as f:
        app_code = f.read()
    
    # Verify enhanced robots.txt is present
    if 'User-agent: Bingbot' not in app_code:
        print("❌ Enhanced robots.txt not found in app.py")
        return False
    
    # Create clean production package
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add main application
        zip_file.writestr('app.py', app_code)
        
        # Add AWS mock config
        with open('aws_mock_config.py', 'r') as f:
            zip_file.writestr('aws_mock_config.py', f.read())
        
        # Add simple requirements.txt
        zip_file.writestr('requirements.txt', '''
boto3==1.34.0
urllib3==1.26.0
''')
        
        # Add deployment info
        zip_file.writestr('deployment_info.json', json.dumps({
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'enhancement': 'Enhanced robots.txt with AI SEO optimization',
            'status': 'production_ready'
        }, indent=2))
    
    zip_buffer.seek(0)
    zip_data = zip_buffer.getvalue()
    
    # Save package
    with open('production_fix_package.zip', 'wb') as f:
        f.write(zip_data)
    
    print(f"✅ Production package created: {len(zip_data)} bytes")
    return zip_data

def deploy_fixed_version():
    """Deploy the fixed version to production"""
    try:
        # Create package
        zip_data = create_working_production_package()
        if not zip_data:
            return False
        
        # Deploy to Lambda
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        response = lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_data
        )
        
        print(f"✅ Successfully deployed fixed version")
        print(f"📋 Function ARN: {response['FunctionArn']}")
        print(f"📊 Code size: {response['CodeSize']} bytes")
        
        # Wait for deployment
        import time
        print("⏳ Waiting for deployment to propagate...")
        time.sleep(15)
        
        # Test the fix
        import urllib.request
        
        try:
            # Test home page
            with urllib.request.urlopen('https://www.ieltsaiprep.com/', timeout=10) as response:
                if response.status == 200:
                    print("✅ Home page working")
                else:
                    print(f"⚠️ Home page status: {response.status}")
        except Exception as e:
            print(f"⚠️ Home page test failed: {e}")
        
        try:
            # Test robots.txt
            with urllib.request.urlopen('https://www.ieltsaiprep.com/robots.txt', timeout=10) as response:
                if response.status == 200:
                    content = response.read().decode('utf-8')
                    bot_count = content.count('User-agent:')
                    print(f"✅ Robots.txt working with {bot_count} bots")
                    
                    if 'User-agent: Bingbot' in content:
                        print("✅ Enhanced robots.txt successfully deployed!")
                        return True
                    else:
                        print("⚠️ Enhanced content not yet visible")
                        return False
                else:
                    print(f"⚠️ Robots.txt status: {response.status}")
                    return False
        except Exception as e:
            print(f"⚠️ Robots.txt test failed: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Fixing production deployment...")
    
    if deploy_fixed_version():
        print("🎉 Production deployment fixed successfully!")
        print("🔗 Test: https://www.ieltsaiprep.com/robots.txt")
    else:
        print("❌ Production deployment still has issues")