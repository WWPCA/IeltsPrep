"""
Investigate Nova Sonic Access Requirements
Research proper configuration and access patterns for Nova Sonic
"""

import boto3
import json
import logging
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_bedrock_models_detailed():
    """Check all available Bedrock models with detailed information"""
    try:
        client = boto3.client('bedrock', region_name='us-east-1')
        
        logger.info("Checking detailed model information...")
        
        response = client.list_foundation_models()
        
        nova_models = []
        for model in response['modelSummaries']:
            if 'nova' in model['modelId'].lower():
                nova_models.append({
                    'modelId': model['modelId'],
                    'modelName': model.get('modelName', 'N/A'),
                    'providerName': model.get('providerName', 'N/A'),
                    'inputModalities': model.get('inputModalities', []),
                    'outputModalities': model.get('outputModalities', []),
                    'responseStreamingSupported': model.get('responseStreamingSupported', False)
                })
        
        logger.info(f"Found {len(nova_models)} Nova models:")
        for model in nova_models:
            logger.info(f"Model: {model['modelId']}")
            logger.info(f"  Input: {model['inputModalities']}")
            logger.info(f"  Output: {model['outputModalities']}")
            logger.info(f"  Streaming: {model['responseStreamingSupported']}")
            logger.info("---")
        
        return nova_models
        
    except Exception as e:
        logger.error(f"Failed to check models: {e}")
        return []

def test_nova_sonic_regions():
    """Test Nova Sonic access in different regions"""
    regions = ['us-east-1', 'us-west-2', 'eu-west-1']
    
    for region in regions:
        try:
            logger.info(f"Testing Nova Sonic in region: {region}")
            
            client = boto3.client('bedrock-runtime', region_name=region)
            
            request_body = {
                "messages": [
                    {
                        "role": "system",
                        "content": [{"text": "Say hello"}]
                    }
                ],
                "inferenceConfig": {
                    "maxTokens": 50,
                    "temperature": 0.7
                }
            }
            
            response = client.invoke_model(
                modelId='amazon.nova-sonic-v1:0',
                contentType='application/json',
                accept='application/json',
                body=json.dumps(request_body)
            )
            
            logger.info(f"✓ Nova Sonic works in {region}")
            return region
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.info(f"✗ {region}: {error_code}")
        except Exception as e:
            logger.info(f"✗ {region}: {str(e)}")
    
    return None

def test_nova_sonic_without_audio():
    """Test Nova Sonic without audio configuration"""
    try:
        client = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        logger.info("Testing Nova Sonic without audio configuration...")
        
        request_body = {
            "messages": [
                {
                    "role": "system",
                    "content": [{"text": "You are Maya, an IELTS examiner. Say hello and introduce yourself."}]
                }
            ],
            "inferenceConfig": {
                "maxTokens": 100,
                "temperature": 0.7,
                "topP": 0.9
            }
        }
        
        response = client.invoke_model(
            modelId='amazon.nova-sonic-v1:0',
            contentType='application/json',
            accept='application/json',
            body=json.dumps(request_body)
        )
        
        result = json.loads(response['body'].read())
        logger.info("✓ Nova Sonic text-only mode works!")
        logger.info(f"Response: {result}")
        
        return True, result
        
    except Exception as e:
        logger.error(f"Nova Sonic text-only failed: {e}")
        return False, str(e)

def check_nova_sonic_permissions():
    """Check specific Nova Sonic permissions and requirements"""
    try:
        client = boto3.client('bedrock', region_name='us-east-1')
        
        # Check model access
        response = client.get_foundation_model(modelIdentifier='amazon.nova-sonic-v1:0')
        
        logger.info("Nova Sonic model details:")
        logger.info(f"Model ID: {response['modelDetails']['modelId']}")
        logger.info(f"Input Modalities: {response['modelDetails']['inputModalities']}")
        logger.info(f"Output Modalities: {response['modelDetails']['outputModalities']}")
        
        return True, response['modelDetails']
        
    except ClientError as e:
        logger.error(f"Permission check failed: {e}")
        return False, str(e)

if __name__ == "__main__":
    print("Investigating Nova Sonic access requirements...")
    
    # Check model details
    models = check_bedrock_models_detailed()
    
    # Check permissions
    has_access, details = check_nova_sonic_permissions()
    if has_access:
        print("✓ Nova Sonic model is accessible")
    else:
        print(f"✗ Nova Sonic access issue: {details}")
    
    # Test different regions
    working_region = test_nova_sonic_regions()
    if working_region:
        print(f"✓ Nova Sonic works in region: {working_region}")
    else:
        print("✗ Nova Sonic not accessible in tested regions")
    
    # Test text-only mode
    text_works, text_result = test_nova_sonic_without_audio()
    if text_works:
        print("✓ Nova Sonic text mode accessible")
    else:
        print(f"✗ Nova Sonic text mode failed: {text_result}")