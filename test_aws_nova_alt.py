"""
Test AWS Bedrock access for Nova Micro model with alternative model ID.
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
        
        print("Checking AWS Bedrock access for Nova Micro model with alternative model ID...")
        
        # Alternative model IDs to try
        model_ids = [
            "amazon.nova-v1:0",
            "amazon.nova-micro-v1",
            "amazon.nova-micro",
            "amazon.titan-text-lite-v1",
            "anthropic.claude-3-haiku-20240307-v1:0"
        ]
        
        success = False
        
        for model_id in model_ids:
            print(f"\nTrying model ID: {model_id}")
            try:
                # Prepare a simple test request
                if "claude" in model_id:
                    # Claude models use a different request format
                    request_body = {
                        "anthropic_version": "bedrock-2023-05-31",
                        "max_tokens": 100,
                        "messages": [
                            {
                                "role": "user",
                                "content": "Explain IELTS assessment in one sentence."
                            }
                        ]
                    }
                elif "titan" in model_id:
                    # Titan models use a different request format
                    request_body = {
                        "inputText": "Explain IELTS assessment in one sentence.",
                        "textGenerationConfig": {
                            "maxTokenCount": 100,
                            "temperature": 0.7,
                            "topP": 0.9
                        }
                    }
                else:
                    # Nova models use this format
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
                    modelId=model_id,
                    contentType="application/json",
                    accept="application/json",
                    body=json.dumps(request_body)
                )
                
                # If we get here, the request was successful
                print(f"SUCCESS with model {model_id}!")
                
                # Parse the response to verify it worked
                response_body = json.loads(response.get('body').read())
                print(f"Response: {response_body}")
                
                success = True
                break
                
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', 'Unknown')
                error_message = e.response.get('Error', {}).get('Message', str(e))
                print(f"Error with {model_id}: {error_code} - {error_message}")
            except Exception as e:
                print(f"Unexpected error with {model_id}: {str(e)}")
        
        if not success:
            print("\nNone of the tested models were accessible with current credentials.")
        
        return success
        
    except Exception as e:
        print(f"ERROR: Something went wrong: {str(e)}")
        return False

if __name__ == "__main__":
    test_nova_micro_access()