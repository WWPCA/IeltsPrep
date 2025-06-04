"""
Test Nova Sonic API trigger to verify model references and functionality
"""

import os
import boto3
import json
import logging
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_nova_sonic_trigger():
    """Test Nova Sonic API with correct model ID"""
    
    try:
        # Initialize Nova Sonic client
        client = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        logger.info("Testing Nova Sonic API with amazon.nova-sonic-v1:0 model...")
        
        # Test conversation trigger (same as page load trigger)
        request_body = {
            "messages": [
                {
                    "role": "system",
                    "content": [{"text": "You are Maya, a certified IELTS Speaking examiner conducting an official speaking assessment."}]
                },
                {
                    "role": "user", 
                    "content": [{"text": "The assessment page has loaded and I'm ready to begin."}]
                }
            ],
            "inferenceConfig": {
                "maxTokens": 200,
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
        
        # Call Nova Sonic API
        response = client.invoke_model(
            modelId='amazon.nova-sonic-v1:0',
            contentType='application/json',
            accept='application/json',
            body=json.dumps(request_body)
        )
        
        result = json.loads(response['body'].read())
        logger.info("Nova Sonic API call successful!")
        logger.info(f"Response keys: {list(result.keys())}")
        
        # Check for expected response structure
        if 'output' in result:
            logger.info("Response contains 'output' field - API working correctly")
        else:
            logger.warning(f"Unexpected response structure: {result}")
            
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        logger.error(f"Nova Sonic API error: {error_code} - {error_message}")
        
        if error_code == 'AccessDeniedException':
            logger.error("Access denied - AWS credentials may need updating")
        elif error_code == 'ValidationException':
            logger.error("Validation error - model ID or request format issue")
        elif error_code == 'ThrottlingException':
            logger.error("Rate limiting - too many requests")
        else:
            logger.error(f"Unexpected error: {e}")
            
        return False
        
    except Exception as e:
        logger.error(f"Unexpected error testing Nova Sonic: {e}")
        return False

if __name__ == "__main__":
    success = test_nova_sonic_trigger()
    if success:
        print("✓ Nova Sonic trigger test PASSED")
    else:
        print("✗ Nova Sonic trigger test FAILED")