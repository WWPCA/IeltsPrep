"""
Check what Nova models are available with current AWS credentials
"""

import boto3
import json
from botocore.exceptions import ClientError

def check_available_models():
    """Check available Nova models in AWS Bedrock"""
    
    try:
        # Initialize Bedrock client
        bedrock = boto3.client('bedrock', region_name='us-east-1')
        
        print("Checking available Nova models...")
        
        # List foundation models
        response = bedrock.list_foundation_models()
        
        nova_models = []
        for model in response['modelSummaries']:
            if 'nova' in model['modelId'].lower():
                nova_models.append({
                    'modelId': model['modelId'],
                    'modelName': model.get('modelName', 'Unknown'),
                    'outputModalities': model.get('outputModalities', []),
                    'inputModalities': model.get('inputModalities', [])
                })
        
        print(f"\nFound {len(nova_models)} Nova models:")
        for model in nova_models:
            print(f"- {model['modelId']}")
            print(f"  Name: {model['modelName']}")
            print(f"  Input: {model['inputModalities']}")
            print(f"  Output: {model['outputModalities']}")
            print()
            
        return nova_models
        
    except ClientError as e:
        print(f"Error checking models: {e}")
        return []

def test_nova_models(models):
    """Test each available Nova model"""
    
    runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    for model in models:
        model_id = model['modelId']
        print(f"Testing {model_id}...")
        
        try:
            # Simple text request
            request_body = {
                "messages": [
                    {
                        "role": "user",
                        "content": [{"text": "Hello, can you help with IELTS practice?"}]
                    }
                ],
                "inferenceConfig": {
                    "maxTokens": 50,
                    "temperature": 0.7
                }
            }
            
            response = runtime.invoke_model(
                modelId=model_id,
                contentType='application/json',
                accept='application/json',
                body=json.dumps(request_body)
            )
            
            print(f"✓ {model_id} - SUCCESS")
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            print(f"✗ {model_id} - {error_code}")

if __name__ == "__main__":
    models = check_available_models()
    if models:
        test_nova_models(models)
    else:
        print("No Nova models found or access denied")