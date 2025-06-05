"""
Test Nova model access after Bedrock account verification
"""

import boto3
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_nova_models():
    """Test Nova model access after account setup"""
    
    models_to_test = [
        'amazon.nova-sonic-v1:0',
        'amazon.nova-lite-v1:0', 
        'amazon.nova-micro-v1:0'
    ]
    
    try:
        client = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        for model_id in models_to_test:
            logger.info(f"Testing {model_id}...")
            
            request_body = {
                "messages": [
                    {
                        "role": "system",
                        "content": [{"text": "You are Maya, an IELTS examiner. Say hello."}]
                    }
                ],
                "inferenceConfig": {
                    "maxTokens": 50,
                    "temperature": 0.7
                }
            }
            
            response = client.invoke_model(
                modelId=model_id,
                contentType='application/json',
                accept='application/json',
                body=json.dumps(request_body)
            )
            
            result = json.loads(response['body'].read())
            text_response = result['output']['message']['content'][0]['text']
            
            print(f"✓ {model_id} working: {text_response[:100]}...")
            
    except Exception as e:
        print(f"✗ Model access issue: {e}")

def test_nova_sonic_speech():
    """Test Nova Sonic with speech capabilities"""
    
    try:
        client = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        request_body = {
            "messages": [
                {
                    "role": "system",
                    "content": [{"text": "You are Maya, an IELTS examiner. Welcome the candidate and begin Part 1."}]
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
        content = result['output']['message']['content']
        
        has_text = any('text' in item for item in content)
        has_audio = any('audio' in item for item in content)
        
        print(f"✓ Nova Sonic speech test successful")
        print(f"  Text response: {has_text}")
        print(f"  Audio response: {has_audio}")
        
        if has_text:
            text_content = next(item['text'] for item in content if 'text' in item)
            print(f"  Maya says: {text_content}")
        
        return True
        
    except Exception as e:
        print(f"✗ Nova Sonic speech test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Nova model access after Bedrock account verification...")
    test_nova_models()
    print("\nTesting Nova Sonic speech capabilities...")
    test_nova_sonic_speech()