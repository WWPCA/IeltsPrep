"""
Test Nova Sonic with proper AWS documentation patterns
"""

import os
import boto3
import json
import logging
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_nova_sonic_welcome_trigger():
    """Test Nova Sonic with system-only trigger pattern from AWS docs"""
    
    try:
        client = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        logger.info("Testing Nova Sonic welcome trigger with system-only message...")
        
        # Following AWS documentation pattern - system message only to trigger Nova Sonic first
        request_body = {
            "messages": [
                {
                    "role": "system",
                    "content": [{"text": "You are Maya, a certified IELTS Speaking examiner. Start the conversation immediately with a warm welcome and introduce yourself. Begin speaking now."}]
                }
            ],
            "inferenceConfig": {
                "maxTokens": 150,
                "temperature": 0.7,
                "topP": 0.9
            },
            "additionalModelRequestFields": {
                "audio": {
                    "format": "mp3",
                    "voice": "amy"
                }
            }
        }
        
        response = client.invoke_model(
            modelId='amazon.nova-sonic-v1:0',
            contentType='application/json',
            accept='application/json',
            body=json.dumps(request_body)
        )
        
        result = json.loads(response['body'].read())
        logger.info("Nova Sonic welcome trigger successful!")
        logger.info(f"Response structure: {list(result.keys())}")
        
        return True, result
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        logger.error(f"Nova Sonic error: {error_code} - {error_message}")
        
        if error_code == 'AccessDeniedException':
            return False, "Access denied - Nova Sonic may require additional permissions"
        elif error_code == 'ValidationException':
            return False, "Validation error - Nova Sonic access or format issue"
        elif error_code == 'ResourceNotFoundException':
            return False, "Nova Sonic model not found in this region"
        else:
            return False, f"Error: {error_code} - {error_message}"
            
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False, str(e)

def test_speech_to_speech_format():
    """Test speech-to-speech conversation format"""
    
    try:
        client = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        logger.info("Testing speech-to-speech conversation format...")
        
        # Sample base64 audio (minimal test)
        test_audio = "UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA="
        
        request_body = {
            "messages": [
                {
                    "role": "system",
                    "content": [{"text": "You are Maya, an IELTS examiner. Continue the conversation."}]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "audio": {
                                "format": "wav",
                                "source": {
                                    "bytes": test_audio
                                }
                            }
                        }
                    ]
                }
            ],
            "inferenceConfig": {
                "maxTokens": 100,
                "temperature": 0.7
            },
            "additionalModelRequestFields": {
                "audio": {
                    "format": "mp3",
                    "voice": "amy"
                }
            }
        }
        
        response = client.invoke_model(
            modelId='amazon.nova-sonic-v1:0',
            contentType='application/json',
            accept='application/json',
            body=json.dumps(request_body)
        )
        
        result = json.loads(response['body'].read())
        logger.info("Speech-to-speech format test successful!")
        
        return True, result
        
    except Exception as e:
        logger.error(f"Speech-to-speech test failed: {e}")
        return False, str(e)

if __name__ == "__main__":
    print("Testing Nova Sonic proper implementation...")
    
    # Test 1: Welcome trigger
    success1, result1 = test_nova_sonic_welcome_trigger()
    if success1:
        print("✓ Nova Sonic welcome trigger PASSED")
    else:
        print(f"✗ Nova Sonic welcome trigger FAILED: {result1}")
    
    # Test 2: Speech-to-speech format
    if success1:  # Only test if basic access works
        success2, result2 = test_speech_to_speech_format()
        if success2:
            print("✓ Speech-to-speech format PASSED")
        else:
            print(f"✗ Speech-to-speech format FAILED: {result2}")
    
    if success1:
        print("Nova Sonic implementation ready for IELTS assessment")
    else:
        print("Nova Sonic requires additional access configuration")