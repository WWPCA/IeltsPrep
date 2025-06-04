"""
Check AWS Bedrock API Credentials
This script validates AWS credentials for Bedrock access.
"""

import os
import boto3
import json
from botocore.exceptions import ClientError, NoCredentialsError

def check_bedrock_credentials():
    """
    Check if AWS Bedrock credentials are correctly configured.
    
    Returns:
        bool: True if credentials are valid, False otherwise
    """
    print("Checking AWS Bedrock credentials...")
    
    # Check if AWS credentials are set
    aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    aws_region = os.environ.get('AWS_REGION')
    
    if not aws_access_key or not aws_secret_key:
        print("AWS credentials are missing. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables.")
        return False
        
    if not aws_region:
        print("AWS_REGION not set. Using default region us-east-1.")
        os.environ['AWS_REGION'] = 'us-east-1'
    
    try:
        # Try to create a Bedrock client
        client = boto3.client(
            service_name='bedrock-runtime',
            region_name=os.environ.get('AWS_REGION', 'us-east-1')
        )
        
        # Prepare a simple test request
        request_body = {
            "inferenceConfig": {
                "max_new_tokens": 5
            },
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": "Hello"
                        }
                    ]
                }
            ]
        }
        
        # Make a lightweight API call to verify access
        response = client.invoke_model(
            modelId="amazon.nova-sonic-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps(request_body)
        )
        
        # Check response status code
        status_code = response.get('ResponseMetadata', {}).get('HTTPStatusCode')
        if status_code == 200:
            print("AWS Bedrock credentials are valid!")
            return True
        else:
            print(f"AWS Bedrock API returned unexpected status code: {status_code}")
            return False
            
    except NoCredentialsError:
        print("No AWS credentials found. Please configure AWS credentials.")
        return False
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        error_message = e.response.get('Error', {}).get('Message', str(e))
        print(f"AWS Bedrock API error: {error_code} - {error_message}")
        
        if error_code == 'AccessDeniedException':
            print("Access denied to Bedrock API. Ensure your IAM role has appropriate permissions.")
        elif error_code == 'ValidationException':
            print("Validation error. Check if the model ID is correct and available in your region.")
        elif error_code == 'ResourceNotFoundException':
            print("Resource not found. Check if the model is available in your selected region.")
            
        return False
    except Exception as e:
        print(f"Error checking Bedrock credentials: {str(e)}")
        return False

if __name__ == "__main__":
    check_bedrock_credentials()