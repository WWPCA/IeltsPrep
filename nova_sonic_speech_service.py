"""
Nova Sonic Speech-to-Speech Service for IELTS Maya Conversations
Implements proper Nova Sonic bidirectional speech using AWS Bedrock
"""

import json
import boto3
import logging
import base64
from datetime import datetime
from botocore.exceptions import ClientError, BotoCoreError

logger = logging.getLogger(__name__)

class NovaSonicSpeechService:
    """Nova Sonic speech-to-speech service for authentic IELTS conversations"""
    
    def __init__(self):
        self.bedrock_client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize AWS Bedrock client for Nova Sonic speech"""
        try:
            self.bedrock_client = boto3.client(
                'bedrock-runtime',
                region_name='us-east-1'
            )
            logger.info("Nova Sonic speech service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Nova Sonic: {e}")
    
    def start_speech_conversation(self, part_number=1, context=""):
        """Start Nova Sonic speech-to-speech conversation"""
        try:
            if not self.bedrock_client:
                raise Exception("Nova Sonic service not initialized")
            
            # Get Maya's opening for the speaking part
            system_prompt = self._get_maya_system_prompt(part_number, context)
            opening_message = self._get_maya_opening(part_number)
            
            # Nova Sonic bidirectional speech configuration
            request_body = {
                "schemaVersion": "speech-bidirection/1.0",
                "configuration": {
                    "systemPrompt": system_prompt,
                    "inputAudioConfig": {
                        "format": "pcm",
                        "sampleRateHertz": 16000,
                        "channels": 1
                    },
                    "outputAudioConfig": {
                        "format": "pcm",
                        "sampleRateHertz": 16000,
                        "channels": 1
                    },
                    "maxTurnDurationSeconds": 30,
                    "inferenceConfig": {
                        "temperature": 0.7,
                        "topP": 0.9,
                        "maxTokens": 300
                    }
                },
                "inputText": opening_message
            }
            
            response = self.bedrock_client.invoke_model(
                modelId="amazon.nova-sonic-v1:0",
                contentType="application/json",
                accept="application/json",
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            
            # Extract Maya's opening speech
            maya_audio = None
            maya_text = ""
            
            if response_body.get('outputAudio'):
                maya_audio = response_body['outputAudio']
            
            if response_body.get('outputText'):
                maya_text = response_body['outputText']
            
            logger.info(f"Nova Sonic conversation started for Part {part_number}")
            
            return {
                "success": True,
                "conversation_id": f"nova_speech_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "maya_opening_audio": maya_audio,
                "maya_opening_text": maya_text,
                "part_number": part_number,
                "service": "nova_sonic_speech",
                "schema_version": "speech-bidirection/1.0",
                "audio_config": {
                    "format": "pcm",
                    "sample_rate": 16000,
                    "channels": 1
                }
            }
            
        except Exception as e:
            logger.error(f"Nova Sonic conversation start error: {e}")
            return {"success": False, "error": str(e)}
    
    def process_user_speech(self, audio_data, conversation_id, part_number=1):
        """Process user speech input and generate Maya's speech response"""
        try:
            if not self.bedrock_client:
                raise Exception("Nova Sonic service not initialized")
            
            # Prepare audio input for Nova Sonic
            if isinstance(audio_data, bytes):
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            else:
                audio_base64 = audio_data
            
            system_prompt = self._get_maya_system_prompt(part_number)
            
            # Nova Sonic bidirectional speech request
            request_body = {
                "schemaVersion": "speech-bidirection/1.0",
                "configuration": {
                    "systemPrompt": system_prompt,
                    "inputAudioConfig": {
                        "format": "pcm",
                        "sampleRateHertz": 16000,
                        "channels": 1
                    },
                    "outputAudioConfig": {
                        "format": "pcm",
                        "sampleRateHertz": 16000,
                        "channels": 1
                    },
                    "maxTurnDurationSeconds": 30,
                    "inferenceConfig": {
                        "temperature": 0.7,
                        "topP": 0.9,
                        "maxTokens": 300
                    }
                },
                "inputAudio": {
                    "data": audio_base64,
                    "format": "pcm"
                }
            }
            
            response = self.bedrock_client.invoke_model(
                modelId="amazon.nova-sonic-v1:0",
                contentType="application/json",
                accept="application/json",
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            
            # Extract Maya's response
            maya_audio = None
            maya_text = ""
            user_transcript = ""
            
            if response_body.get('inputTranscript'):
                user_transcript = response_body['inputTranscript']
            
            if response_body.get('outputAudio'):
                maya_audio = response_body['outputAudio']
            
            if response_body.get('outputText'):
                maya_text = response_body['outputText']
            
            logger.info(f"Nova Sonic speech processed for conversation {conversation_id}")
            
            return {
                "success": True,
                "conversation_id": conversation_id,
                "user_transcript": user_transcript,
                "maya_audio": maya_audio,
                "maya_text": maya_text,
                "part_number": part_number,
                "service": "nova_sonic_speech",
                "modality": "bidirectional_speech",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Nova Sonic speech processing error: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_maya_system_prompt(self, part_number, context=""):
        """Get Maya's system prompt for Nova Sonic"""
        base_prompt = """You are Maya, a professional IELTS speaking examiner. You conduct authentic IELTS speaking assessments with natural conversation flow. Speak clearly and professionally, asking follow-up questions that help candidates demonstrate their English proficiency."""
        
        part_specific = {
            1: "In Part 1, ask personal questions about the candidate's background, interests, and daily life. Keep questions simple and encourage detailed responses.",
            2: "In Part 2, you've given the candidate a topic card. Listen to their 1-2 minute presentation and ask one follow-up question.",
            3: "In Part 3, engage in an abstract discussion related to the Part 2 topic. Ask analytical questions that require deeper thinking and opinion expression."
        }
        
        return f"{base_prompt} {part_specific.get(part_number, part_specific[1])} {context}"
    
    def _get_maya_opening(self, part_number):
        """Get Maya's opening statement for each part"""
        openings = {
            1: "Hello, I'm Maya, your IELTS speaking examiner. Let's begin with Part 1. Can you tell me your name and where you're from?",
            2: "Now we'll move to Part 2. I'm going to give you a topic to talk about for 1-2 minutes. You'll have one minute to prepare.",
            3: "Thank you. Now let's discuss some more general questions related to what you've just talked about."
        }
        
        return openings.get(part_number, openings[1])
    
    def check_service_status(self):
        """Check Nova Sonic service availability"""
        try:
            if not self.bedrock_client:
                return {"available": False, "error": "Client not initialized"}
            
            # Test minimal Nova Sonic request
            test_request = {
                "schemaVersion": "speech-bidirection/1.0",
                "configuration": {
                    "systemPrompt": "Test prompt",
                    "inputAudioConfig": {"format": "pcm", "sampleRateHertz": 16000},
                    "outputAudioConfig": {"format": "pcm", "sampleRateHertz": 16000}
                },
                "inputText": "Test"
            }
            
            self.bedrock_client.invoke_model(
                modelId="amazon.nova-sonic-v1:0",
                contentType="application/json",
                accept="application/json",
                body=json.dumps(test_request)
            )
            
            return {"available": True, "service": "nova_sonic_speech"}
            
        except Exception as e:
            return {"available": False, "error": str(e)}

# Global Nova Sonic speech service
nova_sonic_service = NovaSonicSpeechService()

def start_nova_sonic_conversation(part_number=1, context=""):
    """Start Nova Sonic speech-to-speech conversation"""
    return nova_sonic_service.start_speech_conversation(part_number, context)

def process_nova_sonic_speech(audio_data, conversation_id, part_number=1):
    """Process speech with Nova Sonic"""
    return nova_sonic_service.process_user_speech(audio_data, conversation_id, part_number)

def check_nova_sonic_status():
    """Check Nova Sonic service status"""
    return nova_sonic_service.check_service_status()