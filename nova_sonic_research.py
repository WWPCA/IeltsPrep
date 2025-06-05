"""
Nova Sonic Research and Implementation
Comprehensive testing and implementation of Nova Sonic speech-to-speech capabilities
"""

import boto3
import json
import logging
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NovaSonicResearch:
    """Research and test Nova Sonic access patterns"""
    
    def __init__(self):
        self.regions = ['us-east-1', 'us-west-2', 'eu-west-1']
        self.models_to_test = [
            'amazon.nova-sonic-v1:0',
            'amazon.nova-lite-v1:0',
            'amazon.nova-micro-v1:0'
        ]
    
    def test_all_configurations(self):
        """Test all Nova Sonic configurations comprehensively"""
        results = {
            'model_availability': {},
            'speech_capabilities': {},
            'text_capabilities': {},
            'working_configurations': []
        }
        
        for region in self.regions:
            logger.info(f"Testing region: {region}")
            results['model_availability'][region] = self._test_models_in_region(region)
            
        return results
    
    def _test_models_in_region(self, region):
        """Test all Nova models in a specific region"""
        region_results = {}
        
        try:
            client = boto3.client('bedrock-runtime', region_name=region)
            
            for model_id in self.models_to_test:
                logger.info(f"Testing {model_id} in {region}")
                region_results[model_id] = self._test_model_configurations(client, model_id)
                
        except Exception as e:
            logger.error(f"Failed to test region {region}: {e}")
            region_results['error'] = str(e)
        
        return region_results
    
    def _test_model_configurations(self, client, model_id):
        """Test different configurations for a specific model"""
        configurations = [
            ('text_only', self._create_text_only_request),
            ('speech_enabled', self._create_speech_request),
            ('conversation_format', self._create_conversation_request)
        ]
        
        results = {}
        
        for config_name, request_builder in configurations:
            try:
                request_body = request_builder()
                
                response = client.invoke_model(
                    modelId=model_id,
                    contentType='application/json',
                    accept='application/json',
                    body=json.dumps(request_body)
                )
                
                result = json.loads(response['body'].read())
                results[config_name] = {
                    'success': True,
                    'response_structure': list(result.keys()),
                    'has_audio': self._check_audio_in_response(result)
                }
                
                logger.info(f"✓ {model_id} {config_name} works")
                
            except ClientError as e:
                error_code = e.response['Error']['Code']
                results[config_name] = {
                    'success': False,
                    'error_code': error_code,
                    'error_message': e.response['Error']['Message']
                }
                logger.info(f"✗ {model_id} {config_name}: {error_code}")
                
            except Exception as e:
                results[config_name] = {
                    'success': False,
                    'error': str(e)
                }
                logger.info(f"✗ {model_id} {config_name}: {str(e)}")
        
        return results
    
    def _create_text_only_request(self):
        """Create basic text-only request"""
        return {
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
    
    def _create_speech_request(self):
        """Create speech-enabled request"""
        return {
            "messages": [
                {
                    "role": "system",
                    "content": [{"text": "You are Maya, an IELTS examiner. Say hello."}]
                }
            ],
            "inferenceConfig": {
                "maxTokens": 50,
                "temperature": 0.7
            },
            "additionalModelRequestFields": {
                "audio": {
                    "format": "mp3",
                    "voice": "amy"
                }
            }
        }
    
    def _create_conversation_request(self):
        """Create conversation-style request"""
        return {
            "messages": [
                {
                    "role": "system",
                    "content": [{"text": "You are Maya, an IELTS examiner."}]
                },
                {
                    "role": "user",
                    "content": [{"text": "Hello, I'm ready for my speaking test."}]
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
    
    def _check_audio_in_response(self, response):
        """Check if response contains audio data"""
        try:
            if 'output' in response and 'message' in response['output']:
                content = response['output']['message'].get('content', [])
                return any('audio' in item for item in content if isinstance(item, dict))
            return False
        except:
            return False
    
    def get_working_configuration(self):
        """Get the best working configuration for Nova models"""
        results = self.test_all_configurations()
        
        # Find best working configuration
        for region, models in results['model_availability'].items():
            for model_id, configs in models.items():
                if isinstance(configs, dict):
                    for config_name, config_result in configs.items():
                        if config_result.get('success'):
                            return {
                                'region': region,
                                'model_id': model_id,
                                'configuration': config_name,
                                'has_speech': config_result.get('has_audio', False)
                            }
        
        return None

def main():
    """Run comprehensive Nova Sonic research"""
    research = NovaSonicResearch()
    
    print("Running comprehensive Nova Sonic research...")
    results = research.test_all_configurations()
    
    print("\n=== NOVA SONIC RESEARCH RESULTS ===")
    
    working_configs = []
    
    for region, models in results['model_availability'].items():
        print(f"\nRegion: {region}")
        
        if 'error' in models:
            print(f"  Error: {models['error']}")
            continue
            
        for model_id, configs in models.items():
            print(f"  Model: {model_id}")
            
            if isinstance(configs, dict):
                for config_name, result in configs.items():
                    if result.get('success'):
                        status = "✓ WORKING"
                        if result.get('has_audio'):
                            status += " (with audio)"
                        working_configs.append({
                            'region': region,
                            'model': model_id,
                            'config': config_name,
                            'audio': result.get('has_audio', False)
                        })
                    else:
                        status = f"✗ FAILED ({result.get('error_code', 'Unknown')})"
                    
                    print(f"    {config_name}: {status}")
    
    print(f"\n=== SUMMARY ===")
    if working_configs:
        print("Working configurations found:")
        for config in working_configs:
            audio_status = "with speech" if config['audio'] else "text-only"
            print(f"  {config['model']} in {config['region']} ({config['config']}) - {audio_status}")
        
        # Recommend best configuration
        best_config = working_configs[0]
        for config in working_configs:
            if 'sonic' in config['model'] and config['audio']:
                best_config = config
                break
        
        print(f"\nRecommended: {best_config['model']} in {best_config['region']}")
    else:
        print("No working configurations found")
    
    return working_configs

if __name__ == "__main__":
    main()