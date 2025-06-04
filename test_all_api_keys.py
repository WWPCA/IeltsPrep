"""
Comprehensive API Key Testing Script
Tests all API keys to verify functionality
"""

import os
import boto3
import requests
import json
from botocore.exceptions import ClientError, NoCredentialsError

def test_aws_credentials():
    """Test AWS credentials and access"""
    print("Testing AWS Credentials...")
    
    try:
        # Test AWS credentials
        aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        aws_region = os.environ.get('AWS_REGION')
        
        print(f"AWS Access Key ID: {'Present' if aws_access_key else 'Missing'}")
        print(f"AWS Secret Access Key: {'Present' if aws_secret_key else 'Missing'}")
        print(f"AWS Region: {aws_region if aws_region else 'Missing'}")
        
        if not all([aws_access_key, aws_secret_key, aws_region]):
            print("❌ AWS credentials incomplete")
            return False
        
        # Test SES access
        ses_client = boto3.client(
            'ses',
            region_name=aws_region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
        
        # Test if we can list identities (basic permission test)
        response = ses_client.list_identities()
        print("✅ AWS SES access confirmed")
        
        # Test Bedrock access
        bedrock_client = boto3.client(
            'bedrock-runtime',
            region_name=aws_region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
        
        # Test with a simple model call
        try:
            response = bedrock_client.invoke_model(
                modelId='amazon.nova-lite-v1:0',
                contentType='application/json',
                accept='application/json',
                body=json.dumps({
                    "messages": [
                        {
                            "role": "user",
                            "content": [{"text": "Test connection"}]
                        }
                    ],
                    "inferenceConfig": {
                        "maxTokens": 10,
                        "temperature": 0.7
                    }
                })
            )
            print("✅ AWS Bedrock Nova Lite access confirmed")
        except ClientError as e:
            print(f"❌ AWS Bedrock access failed: {e}")
            return False
        
        return True
        
    except NoCredentialsError:
        print("❌ AWS credentials not found")
        return False
    except ClientError as e:
        print(f"❌ AWS access failed: {e}")
        return False
    except Exception as e:
        print(f"❌ AWS test error: {e}")
        return False

def test_recaptcha_keys():
    """Test reCAPTCHA v2 keys"""
    print("\nTesting reCAPTCHA v2 Keys...")
    
    site_key = os.environ.get('RECAPTCHA_V2_SITE_KEY')
    secret_key = os.environ.get('RECAPTCHA_V2_SECRET_KEY')
    
    print(f"reCAPTCHA v2 Site Key: {'Present' if site_key else 'Missing'}")
    print(f"reCAPTCHA v2 Secret Key: {'Present' if secret_key else 'Missing'}")
    
    if not site_key or not secret_key:
        print("❌ reCAPTCHA keys incomplete")
        return False
    
    # Test if site key format is correct
    if not site_key.startswith('6L'):
        print("❌ reCAPTCHA site key format invalid")
        return False
    
    # Test API connectivity with a dummy token (will fail but confirms API access)
    try:
        verify_url = 'https://www.google.com/recaptcha/api/siteverify'
        data = {
            'secret': secret_key,
            'response': 'test_token'
        }
        
        response = requests.post(verify_url, data=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            # Even with invalid token, we should get a valid JSON response
            if 'success' in result:
                print("✅ reCAPTCHA API connectivity confirmed")
                return True
        
        print("❌ reCAPTCHA API connectivity failed")
        return False
        
    except Exception as e:
        print(f"❌ reCAPTCHA test error: {e}")
        return False

def main():
    """Run all API key tests"""
    print("API KEY FUNCTIONALITY TEST")
    print("=" * 50)
    
    results = {}
    
    # Test AWS
    results['aws'] = test_aws_credentials()
    
    # Test reCAPTCHA
    results['recaptcha'] = test_recaptcha_keys()
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY:")
    print(f"AWS Services: {'✅ Working' if results['aws'] else '❌ Failed'}")
    print(f"reCAPTCHA v2: {'✅ Working' if results['recaptcha'] else '❌ Failed'}")
    
    if all(results.values()):
        print("\n🎉 All API keys are functional!")
    else:
        print("\n⚠️  Some API keys need attention")
        
        if not results['aws']:
            print("- AWS credentials may be invalid or insufficient permissions")
        if not results['recaptcha']:
            print("- reCAPTCHA keys may be invalid or misconfigured")

if __name__ == '__main__':
    main()