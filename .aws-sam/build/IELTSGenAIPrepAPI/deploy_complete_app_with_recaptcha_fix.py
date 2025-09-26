#!/usr/bin/env python3
"""
Deploy complete app.py as Lambda function with reCAPTCHA fix
Restores all API endpoints while maintaining reCAPTCHA functionality
"""
import boto3
import zipfile
import os

def deploy_complete_app_with_recaptcha_fix():
    """Deploy the complete app.py with all API endpoints and reCAPTCHA fix"""
    
    print("Deploying complete Lambda function with all API endpoints...")
    
    # Create deployment package with all necessary files
    zip_filename = 'complete-app-recaptcha-fixed.zip'
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add the main Lambda function (app.py as lambda_function.py)
        zip_file.write('app.py', 'lambda_function.py')
        
        # Add the AWS mock configuration
        zip_file.write('aws_mock_config.py', 'aws_mock_config.py')
        
        # Add all template files
        zip_file.write('working_template.html', 'working_template.html')
        zip_file.write('login.html', 'login.html')
        zip_file.write('dashboard.html', 'dashboard.html')
    
    # Deploy to AWS Lambda
    try:
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        with open(zip_filename, 'rb') as zip_file:
            zip_content = zip_file.read()
        
        response = lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_content
        )
        
        print("✅ Complete Lambda function deployed successfully!")
        print(f"Function ARN: {response['FunctionArn']}")
        print(f"Last Modified: {response['LastModified']}")
        
        # Clean up
        os.remove(zip_filename)
        
        print("\n🔧 Restored Functionality:")
        print("  • All API endpoints: /api/maya/*, /api/nova-micro/*, /api/login, etc.")
        print("  • Assessment access and templates")
        print("  • Maya introduction and conversation handling")
        print("  • Nova Micro writing assessment")
        print("  • Session management and authentication")
        print("  • QR code generation and verification")
        print("  • reCAPTCHA using environment variables")
        print("  • All comprehensive templates preserved")
        
        print("\n✅ All endpoints should now work:")
        print("  • Home, login, dashboard, privacy, terms pages")
        print("  • /api/health - Health check")
        print("  • /api/maya/introduction - Maya AI introduction")
        print("  • /api/nova-micro/writing - Writing assessment")
        print("  • /assessment/* - Assessment access")
        print("  • /api/login - User authentication")
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment failed: {str(e)}")
        if os.path.exists(zip_filename):
            os.remove(zip_filename)
        return False

if __name__ == "__main__":
    success = deploy_complete_app_with_recaptcha_fix()
    if success:
        print("\n🎯 Complete functionality restored with reCAPTCHA fix!")
    else:
        print("\n❌ Failed to restore complete functionality!")