#!/usr/bin/env python3
"""
Production Backend Testing Script
Tests authentication, AI assessment, and purchase verification
"""

import json
import boto3
import requests
import time
from datetime import datetime

# AWS Configuration
AWS_REGION = 'us-east-1'
LAMBDA_CLIENT = boto3.client('lambda', region_name=AWS_REGION)

def test_auth_handler():
    """Test authentication Lambda function"""
    print("🔐 Testing Authentication Handler...")
    
    test_cases = [
        {
            'name': 'Health Check',
            'payload': {
                'httpMethod': 'GET',
                'path': '/api/health'
            },
            'expected_status': 200
        },
        {
            'name': 'User Registration',
            'payload': {
                'httpMethod': 'POST',
                'path': '/api/register',
                'body': json.dumps({
                    'email': 'test@ieltsaiprep.com',
                    'password': 'TestPassword123!',
                    'platform': 'mobile'
                })
            },
            'expected_status': 200
        },
        {
            'name': 'User Login',
            'payload': {
                'httpMethod': 'POST',
                'path': '/api/login',
                'body': json.dumps({
                    'email': 'test@ieltsaiprep.com',
                    'password': 'TestPassword123!',
                    'platform': 'mobile'
                })
            },
            'expected_status': 200
        },
        {
            'name': 'Mobile Login',
            'payload': {
                'httpMethod': 'POST',
                'path': '/api/mobile-login',
                'body': json.dumps({
                    'email': 'test@ieltsaiprep.com',
                    'password': 'TestPassword123!',
                    'platform': 'mobile'
                })
            },
            'expected_status': 200
        }
    ]
    
    results = []
    access_token = None
    
    for test in test_cases:
        try:
            response = LAMBDA_CLIENT.invoke(
                FunctionName='ielts-auth-handler',
                Payload=json.dumps(test['payload'])
            )
            
            result = json.loads(response['Payload'].read())
            status_code = result.get('statusCode', 500)
            body = json.loads(result.get('body', '{}'))
            
            # Extract access token for later tests
            if test['name'] == 'User Login' and status_code == 200:
                access_token = body.get('accessToken')
            
            success = status_code == test['expected_status']
            results.append({
                'test': test['name'],
                'status': status_code,
                'success': success,
                'message': body.get('message', body.get('error', 'No message'))
            })
            
            print(f"  {'✅' if success else '❌'} {test['name']}: {status_code} - {body.get('message', body.get('error', 'OK'))}")
            
        except Exception as e:
            results.append({
                'test': test['name'],
                'status': 'ERROR',
                'success': False,
                'message': str(e)
            })
            print(f"  ❌ {test['name']}: ERROR - {str(e)}")
    
    return results, access_token

def test_nova_ai_handler(access_token):
    """Test Nova AI Lambda function"""
    print("\\n🤖 Testing Nova AI Handler...")
    
    if not access_token:
        print("  ⚠️  Skipping Nova AI tests - no access token available")
        return []
    
    test_cases = [
        {
            'name': 'Nova Sonic Connect',
            'payload': {
                'httpMethod': 'POST',
                'path': '/api/nova-sonic-connect',
                'headers': {'Authorization': f'Bearer {access_token}'},
                'body': json.dumps({})
            },
            'expected_status': 200
        },
        {
            'name': 'Maya Introduction',
            'payload': {
                'httpMethod': 'POST',
                'path': '/api/maya/introduction',
                'headers': {'Authorization': f'Bearer {access_token}'},
                'body': json.dumps({
                    'assessmentType': 'academic_speaking'
                })
            },
            'expected_status': 200
        },
        {
            'name': 'Writing Assessment',
            'payload': {
                'httpMethod': 'POST',
                'path': '/api/nova-micro/writing',
                'headers': {'Authorization': f'Bearer {access_token}'},
                'body': json.dumps({
                    'text': 'This is a sample IELTS writing response for testing purposes. It demonstrates the candidate\\'s ability to write coherently and address the task requirements.',
                    'assessmentType': 'academic_writing',
                    'questionPrompt': 'Some people believe that technology has made our lives easier. To what extent do you agree or disagree?'
                })
            },
            'expected_status': 200
        }
    ]
    
    results = []
    
    for test in test_cases:
        try:
            response = LAMBDA_CLIENT.invoke(
                FunctionName='ielts-nova-ai-handler',
                Payload=json.dumps(test['payload'])
            )
            
            result = json.loads(response['Payload'].read())
            status_code = result.get('statusCode', 500)
            body = json.loads(result.get('body', '{}'))
            
            success = status_code == test['expected_status']
            results.append({
                'test': test['name'],
                'status': status_code,
                'success': success,
                'message': body.get('message', body.get('error', 'OK'))
            })
            
            print(f"  {'✅' if success else '❌'} {test['name']}: {status_code} - {body.get('message', body.get('error', 'OK'))}")
            
        except Exception as e:
            results.append({
                'test': test['name'],
                'status': 'ERROR',
                'success': False,
                'message': str(e)
            })
            print(f"  ❌ {test['name']}: ERROR - {str(e)}")
    
    return results

def test_purchase_handler():
    """Test purchase verification Lambda function"""
    print("\\n💰 Testing Purchase Handler...")
    
    test_cases = [
        {
            'name': 'Google Play Purchase Verification',
            'payload': {
                'httpMethod': 'POST',
                'path': '/purchase/verify/google',
                'body': json.dumps({
                    'purchaseToken': 'test_token_google_123456789',
                    'productId': 'com.ieltsaiprep.app.academic_writing_4pack',
                    'email': 'test@ieltsaiprep.com',
                    'deviceId': 'test_device_android_123'
                })
            },
            'expected_status': 200
        },
        {
            'name': 'Apple Store Purchase Verification',
            'payload': {
                'httpMethod': 'POST',
                'path': '/purchase/verify/apple',
                'body': json.dumps({
                    'receiptData': 'test_receipt_apple_123456789',
                    'productId': 'com.ieltsaiprep.app.general_speaking_4pack',
                    'email': 'test@ieltsaiprep.com',
                    'deviceId': 'test_device_ios_123'
                })
            },
            'expected_status': 200
        },
        {
            'name': 'General Purchase Verification (Android)',
            'payload': {
                'httpMethod': 'POST',
                'path': '/api/verify-purchase',
                'body': json.dumps({
                    'platform': 'android',
                    'purchaseToken': 'test_token_general_123456789',
                    'productId': 'com.ieltsaiprep.app.academic_speaking_4pack',
                    'email': 'test@ieltsaiprep.com',
                    'deviceId': 'test_device_general_123'
                })
            },
            'expected_status': 200
        },
        {
            'name': 'General Purchase Verification (iOS)',
            'payload': {
                'httpMethod': 'POST',
                'path': '/api/verify-purchase',
                'body': json.dumps({
                    'platform': 'ios',
                    'receiptData': 'test_receipt_general_123456789',
                    'productId': 'com.ieltsaiprep.app.general_writing_4pack',
                    'email': 'test@ieltsaiprep.com',
                    'deviceId': 'test_device_ios_general_123'
                })
            },
            'expected_status': 200
        }
    ]
    
    results = []
    
    for test in test_cases:
        try:
            response = LAMBDA_CLIENT.invoke(
                FunctionName='ielts-purchase-handler',
                Payload=json.dumps(test['payload'])
            )
            
            result = json.loads(response['Payload'].read())
            status_code = result.get('statusCode', 500)
            body = json.loads(result.get('body', '{}'))
            
            success = status_code == test['expected_status']
            results.append({
                'test': test['name'],
                'status': status_code,
                'success': success,
                'message': body.get('message', body.get('error', 'OK'))
            })
            
            print(f"  {'✅' if success else '❌'} {test['name']}: {status_code} - {body.get('message', body.get('error', 'OK'))}")
            
        except Exception as e:
            results.append({
                'test': test['name'],
                'status': 'ERROR',
                'success': False,
                'message': str(e)
            })
            print(f"  ❌ {test['name']}: ERROR - {str(e)}")
    
    return results

def test_other_handlers():
    """Test other Lambda functions"""
    print("\\n📊 Testing Other Handlers...")
    
    functions_to_test = [
        ('ielts-assessment-handler', '/assessment/academic-writing'),
        ('ielts-user-handler', '/dashboard'),
        ('ielts-qr-auth-handler', '/api/auth/generate-qr')
    ]
    
    results = []
    
    for function_name, test_path in functions_to_test:
        try:
            response = LAMBDA_CLIENT.invoke(
                FunctionName=function_name,
                Payload=json.dumps({
                    'httpMethod': 'GET',
                    'path': test_path
                })
            )
            
            result = json.loads(response['Payload'].read())
            status_code = result.get('statusCode', 500)
            body = json.loads(result.get('body', '{}'))
            
            success = status_code < 500  # Accept any non-server-error status
            results.append({
                'test': function_name,
                'status': status_code,
                'success': success,
                'message': body.get('message', body.get('error', 'OK'))
            })
            
            print(f"  {'✅' if success else '❌'} {function_name}: {status_code} - {body.get('message', body.get('error', 'OK'))}")
            
        except Exception as e:
            results.append({
                'test': function_name,
                'status': 'ERROR',
                'success': False,
                'message': str(e)
            })
            print(f"  ❌ {function_name}: ERROR - {str(e)}")
    
    return results

def test_dynamodb_connectivity():
    """Test DynamoDB table connectivity"""
    print("\\n🗄️  Testing DynamoDB Connectivity...")
    
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    
    tables_to_test = [
        'ielts-genai-prep-users',
        'ielts-genai-prep-assessments',
        'ielts-genai-prep-auth-tokens'
    ]
    
    results = []
    
    for table_name in tables_to_test:
        try:
            table = dynamodb.Table(table_name)
            
            # Test table exists and is accessible
            response = table.scan(Limit=1)
            
            results.append({
                'test': f'DynamoDB {table_name}',
                'status': 'ACTIVE',
                'success': True,
                'message': f'Table accessible, item count: {response.get("Count", 0)}'
            })
            
            print(f"  ✅ {table_name}: ACTIVE - Accessible")
            
        except Exception as e:
            results.append({
                'test': f'DynamoDB {table_name}',
                'status': 'ERROR',
                'success': False,
                'message': str(e)
            })
            print(f"  ❌ {table_name}: ERROR - {str(e)}")
    
    return results

def generate_test_report(all_results):
    """Generate comprehensive test report"""
    print("\\n" + "=" * 60)
    print("📋 COMPREHENSIVE TEST REPORT")
    print("=" * 60)
    
    total_tests = sum(len(results) for results in all_results.values())
    passed_tests = sum(sum(1 for r in results if r['success']) for results in all_results.values())
    
    print(f"\\n📊 Overall Results:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {passed_tests}")
    print(f"   Failed: {total_tests - passed_tests}")
    print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print(f"\\n📋 Detailed Results:")
    
    for category, results in all_results.items():
        category_passed = sum(1 for r in results if r['success'])
        category_total = len(results)
        
        print(f"\\n  {category}:")
        print(f"    Passed: {category_passed}/{category_total}")
        
        for result in results:
            status_icon = "✅" if result['success'] else "❌"
            print(f"    {status_icon} {result['test']}: {result['status']} - {result['message']}")
    
    # Recommendations
    print(f"\\n🔧 Recommendations:")
    
    if passed_tests == total_tests:
        print("   🎉 All tests passed! Your backend is ready for production.")
        print("   ✅ Authentication system is working correctly")
        print("   ✅ AI assessment integration is functional")
        print("   ✅ Purchase verification is ready for Play Console")
        print("   ✅ Database connectivity is stable")
    else:
        print("   ⚠️  Some tests failed. Please review the following:")
        
        for category, results in all_results.items():
            failed_tests = [r for r in results if not r['success']]
            if failed_tests:
                print(f"   • {category}: {len(failed_tests)} failed tests")
                for test in failed_tests:
                    print(f"     - {test['test']}: {test['message']}")
    
    print(f"\\n🚀 Next Steps:")
    print("   1. Fix any failed tests before production deployment")
    print("   2. Set up Google Play Console with real service account keys")
    print("   3. Configure Apple App Store shared secret")
    print("   4. Update mobile app with production AWS configuration")
    print("   5. Enable Bedrock Nova models in your AWS account")
    print("   6. Set up monitoring and alerting for production")
    
    return {
        'total_tests': total_tests,
        'passed_tests': passed_tests,
        'success_rate': (passed_tests/total_tests)*100,
        'all_passed': passed_tests == total_tests
    }

def main():
    """Main testing function"""
    print("🧪 Production Backend Testing Suite")
    print("Testing IELTS GenAI Prep Lambda Functions")
    print("=" * 60)
    
    all_results = {}
    
    try:
        # Test authentication
        auth_results, access_token = test_auth_handler()
        all_results['Authentication'] = auth_results
        
        # Test Nova AI (requires auth token)
        ai_results = test_nova_ai_handler(access_token)
        all_results['AI Assessment'] = ai_results
        
        # Test purchase verification
        purchase_results = test_purchase_handler()
        all_results['Purchase Verification'] = purchase_results
        
        # Test other handlers
        other_results = test_other_handlers()
        all_results['Other Functions'] = other_results
        
        # Test DynamoDB
        db_results = test_dynamodb_connectivity()
        all_results['Database'] = db_results
        
        # Generate comprehensive report
        report = generate_test_report(all_results)
        
        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"backend_test_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'summary': report,
                'detailed_results': all_results
            }, f, indent=2)
        
        print(f"\\n📄 Detailed report saved to: {report_file}")
        
        # Exit with appropriate code
        sys.exit(0 if report['all_passed'] else 1)
        
    except Exception as e:
        print(f"\\n❌ Testing suite failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    import sys
    main()