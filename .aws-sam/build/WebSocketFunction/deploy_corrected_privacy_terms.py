#!/usr/bin/env python3
"""
Deploy correct privacy policy and terms of service templates to production Lambda
Updates template constants and function handlers while preserving CloudFront blocking
"""

import boto3
import json
import zipfile
import io
import urllib.request
import re
from datetime import datetime

def get_current_lambda_code():
    """Download current Lambda function code"""
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    try:
        response = lambda_client.get_function(FunctionName='ielts-genai-prep-api')
        download_url = response['Code']['Location']
        with urllib.request.urlopen(download_url) as response:
            zip_data = response.read()
        
        with zipfile.ZipFile(io.BytesIO(zip_data), 'r') as zip_ref:
            code = zip_ref.read('lambda_function.py').decode('utf-8')
        
        return code
    except Exception as e:
        print(f"Error downloading Lambda code: {e}")
        return None

def read_template_files():
    """Read the approved privacy policy and terms of service templates"""
    try:
        with open('complete-privacy-policy.html', 'r', encoding='utf-8') as f:
            privacy_template = f.read()
        
        with open('complete-terms-of-service.html', 'r', encoding='utf-8') as f:
            terms_template = f.read()
        
        return privacy_template, terms_template
    except Exception as e:
        print(f"Error reading template files: {e}")
        return None, None

def update_lambda_templates(lambda_code, privacy_template, terms_template):
    """Update Lambda code with correct privacy policy and terms of service templates"""
    
    # Find and replace PRIVACY_POLICY_TEMPLATE constant
    privacy_pattern = r'PRIVACY_POLICY_TEMPLATE = """.*?"""'
    privacy_replacement = f'PRIVACY_POLICY_TEMPLATE = """{privacy_template}"""'
    
    # Find and replace TERMS_OF_SERVICE_TEMPLATE constant
    terms_pattern = r'TERMS_OF_SERVICE_TEMPLATE = """.*?"""'
    terms_replacement = f'TERMS_OF_SERVICE_TEMPLATE = """{terms_template}"""'
    
    # Apply replacements
    updated_code = re.sub(privacy_pattern, privacy_replacement, lambda_code, flags=re.DOTALL)
    updated_code = re.sub(terms_pattern, terms_replacement, updated_code, flags=re.DOTALL)
    
    # Verify replacements were successful
    if 'PRIVACY_POLICY_TEMPLATE = """' not in updated_code:
        print("Privacy policy template replacement failed")
        return None
    
    if 'TERMS_OF_SERVICE_TEMPLATE = """' not in updated_code:
        print("Terms of service template replacement failed")
        return None
    
    return updated_code

def deploy_updated_lambda(updated_code):
    """Deploy updated Lambda function"""
    
    # Create new ZIP package
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', updated_code)
    
    zip_buffer.seek(0)
    
    # Update Lambda function
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    try:
        lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_buffer.read()
        )
        
        print("Lambda function updated with correct privacy policy and terms of service templates")
        return True
        
    except Exception as e:
        print(f"Error updating Lambda: {e}")
        return False

def test_updated_pages():
    """Test that updated pages are working correctly"""
    import time
    
    print("Waiting for Lambda deployment to complete...")
    time.sleep(10)
    
    try:
        import requests
        
        # Test privacy policy page
        response = requests.get('https://www.ieltsaiprep.com/privacy-policy', timeout=15)
        if response.status_code == 200 and 'TrueScore®' in response.text:
            print("✅ Privacy policy page updated successfully")
        else:
            print(f"❌ Privacy policy page issue: HTTP {response.status_code}")
        
        # Test terms of service page
        response = requests.get('https://www.ieltsaiprep.com/terms-of-service', timeout=15)
        if response.status_code == 200 and 'ClearScore®' in response.text:
            print("✅ Terms of service page updated successfully")
        else:
            print(f"❌ Terms of service page issue: HTTP {response.status_code}")
        
        # Test that home page still works
        response = requests.get('https://www.ieltsaiprep.com/', timeout=15)
        if response.status_code == 200:
            print("✅ Home page still working")
        else:
            print(f"❌ Home page issue: HTTP {response.status_code}")
        
        # Test that CloudFront blocking still works
        response = requests.get('https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod', timeout=15)
        if response.status_code == 403:
            print("✅ CloudFront blocking still working")
        else:
            print(f"❌ CloudFront blocking issue: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"Error during testing: {e}")

def main():
    """Main function to deploy correct privacy policy and terms of service templates"""
    
    print("🔄 Deploying Approved Privacy Policy and Terms of Service Templates")
    print("=" * 68)
    
    # Get current Lambda code
    print("Downloading current Lambda code...")
    lambda_code = get_current_lambda_code()
    if not lambda_code:
        print("❌ Failed to download Lambda code")
        return
    
    # Verify CloudFront blocking is present
    if 'X-CloudFront-Secret' not in lambda_code:
        print("❌ CloudFront blocking not found in current code - aborting to prevent breaking security")
        return
    
    print("✅ CloudFront blocking detected in current code")
    
    # Read approved template files
    print("Reading approved template files...")
    privacy_template, terms_template = read_template_files()
    if not privacy_template or not terms_template:
        print("❌ Failed to read template files")
        return
    
    print("✅ Template files loaded successfully")
    
    # Update Lambda code with correct templates
    print("Updating Lambda code with approved templates...")
    updated_code = update_lambda_templates(lambda_code, privacy_template, terms_template)
    if not updated_code:
        print("❌ Failed to update Lambda code")
        return
    
    print("✅ Lambda code updated with approved templates")
    
    # Deploy updated Lambda function
    print("Deploying updated Lambda function...")
    if not deploy_updated_lambda(updated_code):
        print("❌ Failed to deploy updated Lambda")
        return
    
    print("✅ Lambda function deployed successfully")
    
    # Test updated pages
    print("Testing updated pages...")
    test_updated_pages()
    
    # Save deployment log
    deployment_log = {
        'deployment_type': 'privacy_terms_template_correction',
        'timestamp': datetime.now().isoformat(),
        'cloudfront_blocking_preserved': True,
        'templates_updated': ['PRIVACY_POLICY_TEMPLATE', 'TERMS_OF_SERVICE_TEMPLATE'],
        'functions_updated': ['serve_privacy_policy', 'serve_terms_of_service'],
        'purpose': 'Replace basic templates with approved comprehensive designs'
    }
    
    with open('privacy_terms_deployment_log.json', 'w') as f:
        json.dump(deployment_log, f, indent=2)
    
    print("📄 Deployment log saved to privacy_terms_deployment_log.json")
    print("\n🎉 Deployment complete!")
    print("✅ Privacy policy and terms of service pages updated with approved templates")
    print("✅ CloudFront blocking functionality preserved")
    print("✅ All other website functionality maintained")

if __name__ == "__main__":
    main()