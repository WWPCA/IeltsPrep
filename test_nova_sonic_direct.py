"""
Test Direct Nova Sonic Implementation
Specifically test amazon.nova-sonic-v1:0 invocation
"""

import os
import boto3
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_direct_nova_sonic():
    """Test direct Nova Sonic invocation"""
    
    try:
        client = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        logger.info("Testing direct Nova Sonic invocation with amazon.nova-sonic-v1:0...")
        
        # Direct Nova Sonic request
        request_body = {
            "messages": [
                {
                    "role": "system",
                    "content": [{"text": "You are Maya, an IELTS examiner. Welcome the candidate and begin Part 1."}]
                }
            ],
            "inferenceConfig": {
                "maxTokens": 100,
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
        
        # Direct call to Nova Sonic
        response = client.invoke_model(
            modelId='amazon.nova-sonic-v1:0',
            contentType='application/json',
            accept='application/json',
            body=json.dumps(request_body)
        )
        
        result = json.loads(response['body'].read())
        logger.info("Nova Sonic direct call successful!")
        
        # Check response structure
        if 'output' in result and 'message' in result['output']:
            content = result['output']['message']['content']
            
            has_text = any('text' in item for item in content)
            has_audio = any('audio' in item for item in content)
            
            print("✓ Nova Sonic direct invocation successful")
            print(f"  Text response: {has_text}")
            print(f"  Audio response: {has_audio}")
            
            if has_text:
                text_content = next(item['text'] for item in content if 'text' in item)
                print(f"  Maya says: {text_content}")
            
            return True, result
        else:
            print("✗ Unexpected response structure")
            return False, result
            
    except Exception as e:
        error_message = str(e)
        print(f"✗ Nova Sonic direct invocation failed: {error_message}")
        
        if "ValidationException" in error_message:
            print("  Issue: ValidationException - Model access problem")
        elif "AccessDeniedException" in error_message:
            print("  Issue: AccessDeniedException - Credential problem")
        else:
            print(f"  Issue: {error_message}")
        
        return False, error_message

def test_maya_conversation_start():
    """Test starting Maya conversation with Nova Sonic"""
    
    try:
        from nova_sonic_direct import NovaSonicDirectService
        
        service = NovaSonicDirectService()
        result = service.start_maya_conversation('academic_speaking', 1)
        
        if result['success']:
            print("✓ Maya conversation started with Nova Sonic")
            print(f"  Conversation ID: {result['conversation_id']}")
            print(f"  Speech enabled: {result.get('speech_enabled', False)}")
            print(f"  Maya text: {result['maya_text'][:100]}...")
            
            if result.get('maya_audio'):
                print("  Maya audio: Present")
            
            return True, result
        else:
            print(f"✗ Maya conversation failed: {result['error']}")
            return False, result
            
    except Exception as e:
        print(f"✗ Service initialization failed: {e}")
        return False, str(e)

if __name__ == "__main__":
    print("Testing direct Nova Sonic implementation...")
    
    # Test 1: Direct API call
    success1, result1 = test_direct_nova_sonic()
    
    if success1:
        print("\n" + "="*50)
        print("✓ Nova Sonic API access confirmed")
        
        # Test 2: Service integration
        success2, result2 = test_maya_conversation_start()
        
        if success2:
            print("✓ Complete Nova Sonic integration working")
        else:
            print("✗ Service integration needs work")
    else:
        print("\n" + "="*50)
        print("✗ Nova Sonic API access issue")
        print("  This indicates credential or permission problems")
        print("  Contact AWS support for Nova Sonic access")