import boto3
import json

def test_lambda_function(function_name, payload):
    """Test a Lambda function"""
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    try:
        response = lambda_client.invoke(
            FunctionName=function_name,
            Payload=json.dumps(payload)
        )
        
        result = json.loads(response['Payload'].read())
        print(f"✅ {function_name} test result:")
        print(f"   Status Code: {result.get('statusCode')}")
        print(f"   Response: {json.dumps(result, indent=2)}")
        return result
        
    except Exception as e:
        print(f"❌ {function_name} test failed: {str(e)}")
        return None

# Test the auth handler health endpoint
print("🧪 Testing Lambda Functions")
print("=" * 40)

test_payload = {
    "httpMethod": "GET",
    "path": "/api/health"
}

test_lambda_function("ielts-auth-handler", test_payload)