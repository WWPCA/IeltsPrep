"""
Check AWS Bedrock API access for Amazon Nova Sonic model.
"""
import os
import json
import boto3
from botocore.exceptions import ClientError

def check_nova_sonic_access():
    """Check if we have access to AWS Bedrock with Nova Sonic models."""
    print("Checking AWS Bedrock access for Nova Sonic model with current credentials...")
    
    try:
        # Create a Bedrock Runtime client
        bedrock_runtime = boto3.client(
            service_name='bedrock-runtime',
            region_name=os.environ.get('AWS_REGION', 'us-east-1'),
        )
        
        # Prepare a simple prompt for Nova Sonic using the correct format
        request_body = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": "Hello, can you help me with IELTS speaking practice?"
                        }
                    ]
                }
            ],
            "inferenceConfig": {
                "max_new_tokens": 100,
                "temperature": 0.5,
                "top_p": 0.9
            }
        }
        
        # Try to invoke the Nova Sonic model
        response = bedrock_runtime.invoke_model(
            modelId="amazon.nova-sonic-v1:0",
            contentType="application/json",
            accept="application/json",
            body=bytes(json.dumps(request_body), 'utf-8')
        )
        
        # If we get here, we have successful access
        print("Access to AWS Bedrock Nova Sonic model successful!")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"ERROR: AWS Bedrock access failed with error: {error_code} - {error_message}")
        print("You may need to request access to Nova Sonic models in AWS Bedrock or update your IAM permissions.")
        return False
    except Exception as e:
        print(f"ERROR: Unknown error when accessing AWS Bedrock: {str(e)}")
        return False

if __name__ == "__main__":
    check_nova_sonic_access()