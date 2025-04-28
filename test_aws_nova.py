"""
Test AWS Bedrock access for Nova Micro model with existing credentials.
"""
import os
import boto3
import json
from botocore.exceptions import ClientError

def test_nova_micro_access():
    """Test if we have proper access to AWS Bedrock Nova Micro model."""
    try:
        # Create a Bedrock runtime client using existing credentials
        bedrock_runtime = boto3.client(
            service_name='bedrock-runtime',
            region_name=os.environ.get('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
        )
        
        print("Checking AWS Bedrock access for Nova Micro model with current credentials...")
        
        # Prepare a simple test request for Nova Micro
        request_body = {
            "inferenceConfig": {
                "max_new_tokens": 100
            },
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": "Explain IELTS assessment in one sentence."
                        }
                    ]
                }
            ]
        }
        
        # Make the API call
        response = bedrock_runtime.invoke_model(
            modelId="amazon.nova-micro-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps(request_body)
        )
        
        # Parse the response to verify it worked
        response_body = json.loads(response.get('body').read())
        model_output = response_body.get('output', {})
        response_text = model_output.get('text', '')
        
        print("SUCCESS! Nova Micro model responded with:")
        print(response_text)
        return True
        
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        error_message = e.response.get('Error', {}).get('Message', str(e))
        print(f"ERROR: AWS Bedrock access failed with error: {error_code} - {error_message}")
        print("You may need to request access to Nova Micro models in AWS Bedrock or update your IAM permissions.")
        return False
    except Exception as e:
        print(f"ERROR: Something went wrong: {str(e)}")
        return False

if __name__ == "__main__":
    test_nova_micro_access()