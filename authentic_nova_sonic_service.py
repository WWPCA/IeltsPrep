"""
Authentic Nova Sonic Speech-to-Speech Service
Real audio processing for IELTS conversations using Nova Sonic
"""

import json
import boto3
import logging
import base64
import io
import wave
from datetime import datetime
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class AuthenticNovaSonicService:
    """Authentic Nova Sonic service with real audio processing"""
    
    def __init__(self):
        self.bedrock_client = None
        self.polly_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize AWS clients for Nova Sonic and Polly"""
        try:
            self.bedrock_client = boto3.client(
                'bedrock-runtime',
                region_name='us-east-1'
            )
            
            self.polly_client = boto3.client(
                'polly',
                region_name='us-east-1'
            )
            
            logger.info("Authentic Nova Sonic service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Nova Sonic service: {e}")
    
    def process_speech_conversation(self, user_text, part_number=1, context=""):
        """Process speech conversation with authentic Nova Sonic"""
        try:
            # Step 1: Convert user text to audio for Nova Sonic input
            user_audio = self._generate_speech_audio(user_text)
            
            # Step 2: Get Maya's system prompt
            system_prompt = self._get_maya_prompt(part_number, context)
            
            # Step 3: Process with Nova Sonic speech-to-speech
            nova_result = self._call_nova_sonic(user_audio, system_prompt)
            
            if nova_result.get('success'):
                return {
                    "success": True,
                    "user_text": user_text,
                    "user_audio": user_audio,
                    "maya_text": nova_result.get('maya_text', ''),
                    "maya_audio": nova_result.get('maya_audio', None),
                    "service": "nova_sonic_authentic",
                    "model": "amazon.nova-sonic-v1:0",
                    "modality": "authentic_speech_to_speech",
                    "part_number": part_number,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return nova_result
                
        except Exception as e:
            logger.error(f"Speech conversation error: {e}")
            return {"success": False, "error": str(e)}
    
    def _generate_speech_audio(self, text):
        """Generate speech audio from text using AWS Polly"""
        try:
            response = self.polly_client.synthesize_speech(
                Text=text,
                OutputFormat='pcm',
                VoiceId='Matthew',  # Male voice for user input
                Engine='neural',
                SampleRate='16000'
            )
            
            # Get audio data
            audio_data = response['AudioStream'].read()
            
            # Convert to base64 for Nova Sonic
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            logger.info(f"Generated speech audio: {len(audio_data)} bytes")
            return audio_base64
            
        except Exception as e:
            logger.error(f"Speech generation error: {e}")
            raise
    
    def _call_nova_sonic(self, user_audio_base64, system_prompt):
        """Call Nova Sonic with authentic audio input"""
        try:
            # Nova Sonic request with real audio
            request_body = {
                "inputAudio": {
                    "format": "pcm",
                    "data": user_audio_base64
                },
                "systemPrompt": system_prompt,
                "inferenceConfig": {
                    "temperature": 0.7,
                    "topP": 0.9
                }
            }
            
            response = self.bedrock_client.invoke_model(
                modelId="amazon.nova-sonic-v1:0",
                contentType="application/json",
                accept="application/json",
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            
            # Extract Nova Sonic outputs
            maya_text = response_body.get('outputText', '')
            maya_audio = response_body.get('outputAudio', None)
            user_transcript = response_body.get('inputTranscript', '')
            
            logger.info("Nova Sonic speech-to-speech completed successfully")
            
            return {
                "success": True,
                "maya_text": maya_text,
                "maya_audio": maya_audio,
                "user_transcript": user_transcript
            }
            
        except Exception as e:
            logger.error(f"Nova Sonic call error: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_maya_prompt(self, part_number, context):
        """Get Maya's system prompt for IELTS speaking"""
        base_prompt = "You are Maya, a professional IELTS speaking examiner. Conduct an authentic IELTS speaking assessment with natural conversation flow."
        
        part_prompts = {
            1: "In Part 1, ask personal questions about the candidate's life, interests, and experiences. Keep questions accessible and encourage detailed responses.",
            2: "In Part 2, the candidate will present on their topic card. Listen carefully and ask one relevant follow-up question.",
            3: "In Part 3, engage in abstract discussion related to the Part 2 topic. Ask analytical questions requiring deeper thinking."
        }
        
        context_addition = f" Context: {context}" if context else ""
        
        return f"{base_prompt} {part_prompts.get(part_number, part_prompts[1])}{context_addition}"
    
    def test_nova_sonic_access(self):
        """Test Nova Sonic access with minimal request"""
        try:
            # Generate minimal test audio
            test_audio = self._generate_speech_audio("Hello Maya")
            
            # Test Nova Sonic call
            test_request = {
                "inputAudio": {
                    "format": "pcm",
                    "data": test_audio
                },
                "systemPrompt": "You are Maya, an IELTS examiner. Respond briefly."
            }
            
            response = self.bedrock_client.invoke_model(
                modelId="amazon.nova-sonic-v1:0",
                contentType="application/json",
                accept="application/json",
                body=json.dumps(test_request)
            )
            
            result = json.loads(response['body'].read())
            
            return {
                "success": True,
                "nova_sonic_available": True,
                "response_keys": list(result.keys()),
                "test_output": result.get('outputText', '')[:100]
            }
            
        except Exception as e:
            return {
                "success": False,
                "nova_sonic_available": False,
                "error": str(e)
            }

# Global authentic Nova Sonic service
authentic_nova_sonic = AuthenticNovaSonicService()

def process_authentic_speech_conversation(user_text, part_number=1, context=""):
    """Process authentic speech conversation with Nova Sonic"""
    return authentic_nova_sonic.process_speech_conversation(user_text, part_number, context)

def test_authentic_nova_sonic():
    """Test authentic Nova Sonic access"""
    return authentic_nova_sonic.test_nova_sonic_access()