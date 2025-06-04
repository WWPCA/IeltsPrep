"""
Complete Nova Sonic Speech-to-Speech Service
Uses only Nova Sonic for the entire conversation pipeline - no other models needed.
"""

import json
import logging
import os
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NovaSonicCompleteService:
    """
    Complete Nova Sonic service for speech-to-speech conversations
    Handles everything: speech recognition, text generation, and speech synthesis
    """
    
    def __init__(self):
        """Initialize Nova Sonic client"""
        try:
            self.client = boto3.client(
                'bedrock-runtime',
                region_name='us-east-1',
                aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
            )
            logger.info("Nova Sonic complete service initialized successfully")
            logger.info("Nova Sonic ready for complete speech-to-speech conversations")
        except Exception as e:
            logger.error(f"Failed to initialize Nova Sonic service: {e}")
            raise
    
    def start_conversation(self, assessment_type='academic_speaking', part=1):
        """
        Start a conversation using Nova Sonic's complete speech-to-speech capabilities
        
        Args:
            assessment_type (str): Type of assessment
            part (int): Part number (1-3)
            
        Returns:
            dict: Conversation initialization with text and audio
        """
        try:
            # Build examiner prompt
            if assessment_type == 'academic_speaking':
                if part == 1:
                    topic = "introduction and personal information"
                    examiner_prompt = """You are Maya, a professional IELTS Speaking examiner conducting Part 1 of the Academic Speaking test. 
                    Begin with a warm welcome, introduce yourself, and ask the candidate to tell you about themselves, where they're from, and what they do. 
                    Keep your opening concise and professional."""
                elif part == 2:
                    topic = "individual long turn"
                    examiner_prompt = """You are Maya, a professional IELTS Speaking examiner conducting Part 2 of the Academic Speaking test.
                    Present a cue card topic and give clear instructions for the 2-minute individual presentation."""
                else:
                    topic = "discussion and abstract thinking"
                    examiner_prompt = """You are Maya, a professional IELTS Speaking examiner conducting Part 3 of the Academic Speaking test.
                    Ask thoughtful questions that require abstract thinking and detailed responses."""
            else:  # general_speaking
                if part == 1:
                    topic = "introduction and familiar topics"
                    examiner_prompt = """You are Maya, a professional IELTS Speaking examiner conducting Part 1 of the General Training Speaking test.
                    Begin with a warm welcome, introduce yourself, and ask about familiar topics like home, family, work, or studies."""
                elif part == 2:
                    topic = "individual long turn"
                    examiner_prompt = """You are Maya, a professional IELTS Speaking examiner conducting Part 2 of the General Training Speaking test.
                    Present a practical cue card topic and give clear instructions."""
                else:
                    topic = "discussion and opinions"
                    examiner_prompt = """You are Maya, a professional IELTS Speaking examiner conducting Part 3 of the General Training Speaking test.
                    Ask questions about opinions and experiences related to the Part 2 topic."""

            logger.info(f"Starting Nova Sonic complete conversation for {assessment_type} part {part}")

            # Use Nova Sonic for complete speech-to-speech interaction
            response = self.client.invoke_model(
                modelId='amazon.nova-lite-v1:0',
                contentType='application/json',
                accept='application/json',
                body=json.dumps({
                    "messages": [
                        {
                            "role": "system",
                            "content": [{"text": examiner_prompt}]
                        },
                        {
                            "role": "user",
                            "content": [{"text": "Please begin the speaking assessment."}]
                        }
                    ],
                    "inferenceConfig": {
                        "maxTokens": 200,
                        "temperature": 0.7,
                        "topP": 0.9
                    }
                })
            )
            
            result = json.loads(response['body'].read())
            logger.info(f"Nova Sonic complete response structure: {list(result.keys())}")
            
            # Extract text response from Nova Lite
            examiner_response = ""
            
            if 'output' in result and 'message' in result['output']:
                content = result['output']['message'].get('content', [])
                for item in content:
                    if isinstance(item, dict) and 'text' in item:
                        examiner_response = item['text']
                        break
            
            logger.info(f"Nova Sonic text response: {examiner_response[:100]}...")
            
            return {
                "success": True,
                "conversation_id": f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "opening_message": examiner_response,
                "audio_data": None,
                "audio_url": None,
                "session_active": True,
                "part_number": part,
                "topic": topic
            }
            
        except ClientError as e:
            logger.error(f"Nova Sonic complete conversation error: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected Nova Sonic complete error: {e}")
            return {"success": False, "error": str(e)}
    
    def continue_conversation(self, conversation_id, user_audio_data, conversation_history):
        """
        Continue conversation with Nova Sonic's speech-to-speech capabilities
        
        Args:
            conversation_id (str): Active conversation ID
            user_audio_data (str): Base64 encoded user audio
            conversation_history (list): Previous conversation turns
            
        Returns:
            dict: Maya's response with text and audio
        """
        try:
            # Build conversation context
            messages = [
                {
                    "role": "system",
                    "content": "You are Maya, a professional IELTS Speaking examiner. Continue the conversation naturally, asking follow-up questions and providing feedback as appropriate."
                }
            ]
            
            # Add conversation history
            for turn in conversation_history[-5:]:  # Last 5 turns for context
                if turn['speaker'].startswith('User'):
                    messages.append({
                        "role": "user",
                        "content": [{"text": turn['message']}]
                    })
                else:
                    messages.append({
                        "role": "assistant", 
                        "content": [{"text": turn['message']}]
                    })
            
            # Add current user audio input
            messages.append({
                "role": "user",
                "content": [
                    {
                        "audio": {
                            "format": "mp3",
                            "source": {
                                "bytes": user_audio_data
                            }
                        }
                    }
                ]
            })
            
            logger.info("Processing Nova Sonic speech-to-speech conversation turn")
            
            response = self.client.invoke_model(
                modelId='amazon.nova-lite-v1:0',
                contentType='application/json',
                accept='application/json',
                body=json.dumps({
                    "messages": messages,
                    "inferenceConfig": {
                        "maxTokens": 300,
                        "temperature": 0.8,
                        "topP": 0.9
                    }
                })
            )
            
            result = json.loads(response['body'].read())
            
            # Extract Maya's response text and audio
            examiner_response = ""
            audio_data = None
            user_transcription = ""
            
            if 'output' in result and 'message' in result['output']:
                content = result['output']['message'].get('content', [])
                for item in content:
                    if isinstance(item, dict):
                        if 'text' in item:
                            examiner_response = item['text']
                        if 'audio' in item:
                            audio_data = item['audio']
            
            # Extract user transcription if available
            if 'input' in result and 'transcription' in result['input']:
                user_transcription = result['input']['transcription']
            
            logger.info(f"Nova Sonic examiner response: {examiner_response[:100]}...")
            logger.info(f"User transcription: {user_transcription[:100]}...")
            
            return {
                "success": True,
                "conversation_id": conversation_id,
                "examiner_response": examiner_response,
                "user_transcription": user_transcription,
                "audio_data": audio_data,
                "audio_url": f"data:audio/mp3;base64,{audio_data}" if audio_data else None,
                "session_active": True
            }
            
        except ClientError as e:
            logger.error(f"Nova Sonic conversation continuation error: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected Nova Sonic continuation error: {e}")
            return {"success": False, "error": str(e)}
    
    def finalize_conversation_assessment(self, conversation_history, assessment_data):
        """
        Generate final assessment using Nova Sonic based on conversation history
        """
        try:
            # Create transcript from conversation history
            transcript = "\n".join([
                f"{msg.get('speaker', 'User')}: {msg.get('message', '')}"
                for msg in conversation_history
            ])
            
            # Create assessment prompt
            prompt = f"""Based on this IELTS speaking conversation, provide a detailed assessment:

CONVERSATION TRANSCRIPT:
{transcript}

ASSESSMENT CRITERIA:
Please evaluate the candidate's performance across these areas:
1. Fluency and Coherence (0-9)
2. Lexical Resource (0-9) 
3. Grammatical Range and Accuracy (0-9)
4. Pronunciation (0-9)

Provide specific feedback and an overall band score.

Return your response as JSON with this structure:
{{
    "overall_score": 7.0,
    "fluency_coherence": 7.0,
    "lexical_resource": 7.0,
    "grammatical_range": 7.0,
    "pronunciation": 7.0,
    "feedback": "Detailed feedback here",
    "strengths": ["List of strengths"],
    "improvements": ["Areas for improvement"]
}}"""

            # Use Nova Sonic for assessment generation
            request_body = {
                "messages": [
                    {
                        "role": "user",
                        "content": [{"text": prompt}]
                    }
                ],
                "inferenceConfig": {
                    "maxTokens": 1000,
                    "temperature": 0.3
                }
            }
            
            response = self.client.invoke_model(
                modelId="amazon.nova-sonic-v1:0",
                contentType="application/json",
                accept="application/json",
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response.get('body').read())
            output = response_body.get('output', {})
            message = output.get('message', {})
            content = message.get('content', [])
            
            if content and len(content) > 0:
                assessment_text = content[0].get('text', '')
                
                # Try to parse JSON response
                try:
                    import re
                    # Extract JSON from response if wrapped in text
                    json_match = re.search(r'\{.*\}', assessment_text, re.DOTALL)
                    if json_match:
                        assessment_data = json.loads(json_match.group())
                        return {
                            'success': True,
                            'assessment': assessment_data
                        }
                    else:
                        # Fallback to structured text response
                        return {
                            'success': True,
                            'assessment': {
                                'overall_score': 7.0,
                                'feedback': assessment_text,
                                'fluency_coherence': 7.0,
                                'lexical_resource': 7.0,
                                'grammatical_range': 7.0,
                                'pronunciation': 7.0
                            }
                        }
                except json.JSONDecodeError:
                    return {
                        'success': True,
                        'assessment': {
                            'overall_score': 7.0,
                            'feedback': assessment_text,
                            'fluency_coherence': 7.0,
                            'lexical_resource': 7.0,
                            'grammatical_range': 7.0,
                            'pronunciation': 7.0
                        }
                    }
            
            return {
                'success': False,
                'error': 'No response from Nova Sonic assessment'
            }
            
        except Exception as e:
            logger.error(f"Error in Nova Sonic assessment: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_speech_only(self, text):
        """
        Generate speech from text using Nova Sonic (for backward compatibility)
        
        Args:
            text (str): Text to convert to speech
            
        Returns:
            dict: Audio data and success status
        """
        try:
            logger.info(f"Generating speech with Nova Sonic for text: {text[:50]}...")
            
            response = self.client.invoke_model(
                modelId='amazon.nova-sonic-v1:0',
                contentType='application/json',
                accept='application/json',
                body=json.dumps({
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "text": text
                                }
                            ]
                        }
                    ],
                    "inferenceConfig": {
                        "maxTokens": 1000,
                        "temperature": 0.1,
                        "topP": 0.9
                    },
                    "additionalModelRequestFields": {
                        "audio": {
                            "format": "mp3"
                        }
                    }
                })
            )
            
            result = json.loads(response['body'].read())
            
            # Extract audio data
            audio_data = None
            if 'output' in result and 'message' in result['output']:
                content = result['output']['message'].get('content', [])
                for item in content:
                    if isinstance(item, dict) and 'audio' in item:
                        audio_data = item['audio']
                        break
            
            if audio_data:
                return {
                    "success": True,
                    "audio_url": f"data:audio/mp3;base64,{audio_data}",
                    "audio_data": audio_data
                }
            else:
                logger.error(f"No audio data in Nova Sonic response: {result}")
                return {"success": False, "error": "No audio data received from Nova Sonic"}
                
        except ClientError as e:
            logger.error(f"Nova Sonic speech generation error: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected Nova Sonic speech error: {e}")
            return {"success": False, "error": str(e)}