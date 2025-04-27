"""
Check AWS Bedrock API access for Titan models.
"""
import os
import boto3
import json
from botocore.exceptions import ClientError

def check_titan_access():
    """Check if we have access to AWS Bedrock with Titan models."""
    try:
        # Create a Bedrock client
        bedrock_runtime = boto3.client(
            service_name='bedrock-runtime',
            region_name=os.environ.get('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
        )
        
        # Just print available models to check credentials
        print("Checking AWS Bedrock access for Titan model with current credentials...")
        
        # Test with a simple prompt to Titan
        body = json.dumps({
            "inputText": "Explain IELTS writing assessment in a single sentence.",
            "textGenerationConfig": {
                "maxTokenCount": 100,
                "temperature": 0.7,
                "topP": 0.9
            }
        })
        
        # Try amazon.titan-text-express-v1
        response = bedrock_runtime.invoke_model(
            modelId="amazon.titan-text-express-v1",
            body=body
        )
        
        response_body = json.loads(response.get('body').read())
        print("SUCCESS! Titan text model responded with:")
        print(response_body.get('results', [])[0].get('outputText', 'No output'))
        return True
        
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        error_message = e.response.get('Error', {}).get('Message', str(e))
        print(f"ERROR: AWS Bedrock access failed with error: {error_code} - {error_message}")
        print("You may need to request access to Titan models in AWS Bedrock or update your IAM permissions.")
        return False
    except Exception as e:
        print(f"ERROR: Something went wrong: {str(e)}")
        return False

if __name__ == "__main__":
    check_titan_access()