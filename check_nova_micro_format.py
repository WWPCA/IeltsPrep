"""
Check the correct format for AWS Bedrock Nova Micro model.
"""
import os
import json
import boto3
from botocore.exceptions import ClientError

def check_nova_micro_format():
    """Check the correct format for AWS Bedrock Nova Micro model."""
    try:
        # Create a Bedrock Runtime client
        bedrock_runtime = boto3.client(
            service_name='bedrock-runtime',
            region_name=os.environ.get('AWS_REGION', 'us-east-1'),
        )
        
        # Fix the content format for Nova Micro - it needs content as an array
        request_body = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"text": "Hello, can you help me evaluate an IELTS essay?"}
                    ]
                }
            ]
        }
        
        # Try to invoke the model
        response = bedrock_runtime.invoke_model(
            modelId="amazon.nova-micro-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps(request_body)
        )
        
        # If we get here, we have successful access
        response_body = json.loads(response.get('body').read())
        print("Access to AWS Bedrock Nova Micro model successful!")
        print(f"Response: {json.dumps(response_body, indent=2)}")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"ERROR: AWS Bedrock access failed with error: {error_code} - {error_message}")
        return False
    except Exception as e:
        print(f"ERROR: Unknown error when accessing AWS Bedrock: {str(e)}")
        return False

if __name__ == "__main__":
    check_nova_micro_format()