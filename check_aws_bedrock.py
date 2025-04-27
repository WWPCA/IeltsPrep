"""
Check AWS Bedrock API access for Claude models.
"""
import os
import boto3
import json
from botocore.exceptions import ClientError

def check_bedrock_access():
    """Check if we have access to AWS Bedrock with Claude models."""
    try:
        # Create a Bedrock client
        bedrock_runtime = boto3.client(
            service_name='bedrock-runtime',
            region_name=os.environ.get('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
        )
        
        # Just print available models to check credentials
        print("Checking AWS Bedrock access with current credentials...")
        
        # Test with a simple prompt to Claude
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 100,
            "messages": [
                {
                    "role": "user",
                    "content": "Hello, can you respond with a single sentence confirming you're Claude via AWS Bedrock?"
                }
            ]
        })
        
        response = bedrock_runtime.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body=body
        )
        
        response_body = json.loads(response.get('body').read())
        print("SUCCESS! Claude via AWS Bedrock responded with:")
        print(response_body['content'][0]['text'])
        return True
        
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        error_message = e.response.get('Error', {}).get('Message', str(e))
        print(f"ERROR: AWS Bedrock access failed with error: {error_code} - {error_message}")
        print("You may need to request access to Claude models in AWS Bedrock or update your IAM permissions.")
        return False
    except Exception as e:
        print(f"ERROR: Something went wrong: {str(e)}")
        return False

if __name__ == "__main__":
    check_bedrock_access()