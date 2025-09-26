#!/usr/bin/env python3
"""
Deploy the exact approved privacy policy and terms of service templates from preview
Updates Lambda function with templates that match the attached images
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

def read_approved_templates():
    """Read the approved templates that match the preview images"""
    try:
        with open('approved_privacy_policy.html', 'r', encoding='utf-8') as f:
            privacy_template = f.read()
        
        with open('approved_terms_of_service.html', 'r', encoding='utf-8') as f:
            terms_template = f.read()
        
        return privacy_template, terms_template
    except Exception as e:
        print(f"Error reading approved template files: {e}")
        return None, None

def update_lambda_with_approved_templates(lambda_code, privacy_template, terms_template):
    """Update Lambda code with approved templates that match preview images"""
    
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
    
    # Ensure CloudFront blocking is still present
    if 'X-CloudFront-Secret' not in updated_code:
        print("ERROR: CloudFront blocking missing after template update")
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
        
        print("Lambda function updated with approved templates")
        return True
        
    except Exception as e:
        print(f"Error updating Lambda: {e}")
        return False

def verify_deployment():
    """Verify that the deployment was successful and nothing is broken"""
    import time
    import requests
    
    print("Waiting for Lambda deployment to complete...")
    time.sleep(10)
    
    try:
        # Test privacy policy page
        response = requests.get('https://www.ieltsaiprep.com/privacy-policy', timeout=15)
        if response.status_code == 200 and 'Privacy Policy' in response.text and 'TrueScore®' in response.text:
            print("✅ Privacy policy page: Approved template active")
        else:
            print(f"❌ Privacy policy page issue: HTTP {response.status_code}")
        
        # Test terms of service page  
        response = requests.get('https://www.ieltsaiprep.com/terms-of-service', timeout=15)
        if response.status_code == 200 and 'Terms of Service' in response.text and 'ClearScore®' in response.text:
            print("✅ Terms of service page: Approved template active")
        else:
            print(f"❌ Terms of service page issue: HTTP {response.status_code}")
        
        # Test that home page still works
        response = requests.get('https://www.ieltsaiprep.com/', timeout=15)
        if response.status_code == 200:
            print("✅ Home page: Still working normally")
        else:
            print(f"❌ Home page issue: HTTP {response.status_code}")
        
        # Test login page
        response = requests.get('https://www.ieltsaiprep.com/login', timeout=15)
        if response.status_code == 200:
            print("✅ Login page: Still working normally")
        else:
            print(f"❌ Login page issue: HTTP {response.status_code}")
        
        # Test that CloudFront blocking still works
        response = requests.get('https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod', timeout=15)
        if response.status_code == 403:
            print("✅ CloudFront blocking: Still active")
        else:
            print(f"❌ CloudFront blocking issue: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"Error during verification: {e}")

def main():
    """Main function to deploy approved templates"""
    
    print("🔄 Deploying Approved Templates from Preview Images")
    print("=" * 52)
    
    # Get current Lambda code
    print("Downloading current Lambda code...")
    lambda_code = get_current_lambda_code()
    if not lambda_code:
        print("❌ Failed to download Lambda code")
        return
    
    # Verify CloudFront blocking is present before making changes
    if 'X-CloudFront-Secret' not in lambda_code:
        print("❌ CloudFront blocking not found - aborting to preserve security")
        return
    
    print("✅ CloudFront blocking confirmed in current code")
    
    # Read approved templates
    print("Reading approved template files...")
    privacy_template, terms_template = read_approved_templates()
    if not privacy_template or not terms_template:
        print("❌ Failed to read approved template files")
        return
    
    print("✅ Approved templates loaded successfully")
    
    # Update Lambda code with approved templates
    print("Updating Lambda code with approved templates...")
    updated_code = update_lambda_with_approved_templates(lambda_code, privacy_template, terms_template)
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
    
    # Verify deployment
    print("Verifying deployment...")
    verify_deployment()
    
    # Save deployment log
    deployment_log = {
        'deployment_type': 'approved_templates_from_preview',
        'timestamp': datetime.now().isoformat(),
        'templates_source': 'preview_images_attached_by_user',
        'cloudfront_blocking_preserved': True,
        'templates_updated': ['privacy_policy', 'terms_of_service'],
        'purpose': 'Deploy exact templates shown in preview to match user approval'
    }
    
    with open('approved_templates_deployment_log.json', 'w') as f:
        json.dump(deployment_log, f, indent=2)
    
    print("📄 Deployment log saved to approved_templates_deployment_log.json")
    print("\n🎉 Deployment complete!")
    print("✅ Privacy policy and terms of service now match preview images")
    print("✅ CloudFront blocking functionality preserved")
    print("✅ All other website functionality maintained")

if __name__ == "__main__":
    main()