"""
Check available foundation models in AWS Bedrock.
"""
import os
import boto3
from botocore.exceptions import ClientError

def check_available_models():
    """List available foundation models in AWS Bedrock."""
    try:
        # Create a Bedrock client
        bedrock = boto3.client(
            service_name='bedrock',  # Not bedrock-runtime, which is for inference
            region_name=os.environ.get('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
        )
        
        print("Checking available models in AWS Bedrock...")
        
        # List available foundation models
        response = bedrock.list_foundation_models()
        
        if 'modelSummaries' in response:
            models = response['modelSummaries']
            print(f"Found {len(models)} available models:")
            for model in models:
                model_id = model.get('modelId', 'Unknown')
                model_name = model.get('modelName', 'Unknown')
                print(f"- {model_id} ({model_name})")
        else:
            print("No models found or unexpected response format")
            
        return True
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        error_message = e.response.get('Error', {}).get('Message', str(e))
        print(f"ERROR: AWS Bedrock access failed with error: {error_code} - {error_message}")
        return False
    except Exception as e:
        print(f"ERROR: Something went wrong: {str(e)}")
        return False

if __name__ == "__main__":
    check_available_models()