#!/usr/bin/env python3
"""
Test script for IELTS AI Prep email service
Tests the welcome email functionality
"""

import json
import boto3
import requests
from botocore.exceptions import ClientError

def test_lambda_function_directly():
    """Test the Lambda function directly"""
    print("🧪 Testing Lambda function directly...")
    
    try:
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        # Test payload
        test_event = {
            "type": "welcome",
            "email": "test@example.com",
            "name": "Test User"
        }
        
        response = lambda_client.invoke(
            FunctionName='ielts-email-service',
            InvocationType='RequestResponse',
            Payload=json.dumps(test_event)
        )
        
        result = json.loads(response['Payload'].read())
        print(f"✅ Lambda response: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Lambda test failed: {e}")
        return False

def test_api_gateway_endpoint():
    """Test via API Gateway endpoint"""
    print("\n🌐 Testing API Gateway endpoint...")
    
    # You'll need to replace this with your actual API Gateway URL
    api_url = "https://your-api-gateway-url/prod/send-email"
    
    payload = {
        "type": "welcome",
        "email": "test@example.com",
        "name": "Test User"
    }
    
    try:
        response = requests.post(
            api_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"✅ API Gateway test successful: {response.json()}")
            return True
        else:
            print(f"❌ API Gateway test failed: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API Gateway test failed: {e}")
        return False

def test_ses_configuration():
    """Test SES configuration"""
    print("\n📧 Testing SES configuration...")
    
    try:
        ses_client = boto3.client('ses', region_name='us-east-1')
        
        # Check if sender email is verified
        response = ses_client.get_identity_verification_attributes(
            Identities=['donotreply@ieltsaiprep.com']
        )
        
        verification_status = response['VerificationAttributes'].get(
            'donotreply@ieltsaiprep.com', {}
        ).get('VerificationStatus', 'NotFound')
        
        if verification_status == 'Success':
            print("✅ SES sender email is verified")
            return True
        else:
            print(f"❌ SES sender email verification status: {verification_status}")
            print("   Please verify donotreply@ieltsaiprep.com in AWS SES console")
            return False
            
    except Exception as e:
        print(f"❌ SES configuration test failed: {e}")
        return False

def test_send_real_email():
    """Send a real test email (use your own email)"""
    print("\n📮 Testing real email send...")
    
    # Replace with your email for testing
    test_email = input("Enter your email address for testing (or press Enter to skip): ").strip()
    
    if not test_email:
        print("⏭️  Skipping real email test")
        return True
    
    try:
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        test_event = {
            "type": "welcome",
            "email": test_email,
            "name": "Test User"
        }
        
        response = lambda_client.invoke(
            FunctionName='ielts-email-service',
            InvocationType='RequestResponse',
            Payload=json.dumps(test_event)
        )
        
        result = json.loads(response['Payload'].read())
        
        if result.get('statusCode') == 200:
            print(f"✅ Real email sent successfully to {test_email}")
            print("   Check your inbox for the welcome email!")
            return True
        else:
            print(f"❌ Failed to send real email: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Real email test failed: {e}")
        return False

def main():
    """Run all email service tests"""
    print("🚀 IELTS AI Prep Email Service Test Suite")
    print("=" * 50)
    
    tests = [
        ("SES Configuration", test_ses_configuration),
        ("Lambda Function", test_lambda_function_directly),
        ("Real Email Send", test_send_real_email),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Email service is ready to use.")
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
        print("\nCommon issues:")
        print("- SES sender email not verified")
        print("- Lambda function not deployed")
        print("- AWS credentials not configured")
        print("- API Gateway endpoint not set up")

if __name__ == "__main__":
    main()