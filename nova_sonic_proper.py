"""
Proper Nova Sonic Speech-to-Speech Implementation
Based on AWS documentation and best practices for conversation handling.
"""

import json
import boto3
import base64
import logging
from datetime import datetime
from botocore.exceptions import ClientError
from ielts_question_database import IELTSQuestionDatabase

logger = logging.getLogger(__name__)

class NovaSonicProperService:
    """
    Nova Sonic service implementing proper speech-to-speech conversations
    following AWS documentation guidelines
    """
    
    def __init__(self):
        """Initialize Nova Sonic client with proper error handling"""
        try:
            self.client = boto3.client('bedrock-runtime', region_name='us-east-1')
            logger.info("Nova Sonic client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Nova Sonic client: {e}")
            raise
    
    def start_conversation(self, assessment_type='academic_speaking', part=1):
        """
        Start a conversation using Nova Sonic with proper audio generation
        
        Args:
            assessment_type (str): Type of assessment
            part (int): Part number (1-3)
            
        Returns:
            dict: Conversation initialization with text and audio
        """
        try:
            # Build examiner prompt based on IELTS requirements
            examiner_prompt = self._build_examiner_prompt(assessment_type, part)
            
            logger.info(f"Starting Nova Sonic conversation for {assessment_type} part {part}")
            
            # Nova Sonic request with proper voice configuration
            request_body = {
                "messages": [
                    {
                        "role": "system",
                        "content": [{"text": examiner_prompt}]
                    },
                    {
                        "role": "user", 
                        "content": [{"text": "Hello, I'm ready to begin the speaking assessment."}]
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
            
            response = self.client.invoke_model(
                modelId='amazon.nova-sonic-v1:0',
                contentType='application/json',
                accept='application/json',
                body=json.dumps(request_body)
            )
            
            result = json.loads(response['body'].read())
            logger.info(f"Nova Sonic response received with keys: {list(result.keys())}")
            
            # Parse response for text and audio
            examiner_text, audio_data = self._parse_nova_response(result)
            
            if not examiner_text:
                examiner_text = "Good morning! I'm Maya, your IELTS examiner. Let's begin your speaking assessment."
            
            # Create conversation ID
            conversation_id = f"nova_conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            return {
                "success": True,
                "conversation_id": conversation_id,
                "opening_message": examiner_text,
                "audio_data": audio_data,
                "audio_url": f"data:audio/mp3;base64,{audio_data}" if audio_data else None,
                "session_active": True,
                "part_number": part,
                "assessment_type": assessment_type
            }
            
        except ClientError as e:
            logger.error(f"Nova Sonic API error: {e}")
            return {"success": False, "error": f"Nova Sonic API error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error in start_conversation: {e}")
            return {"success": False, "error": f"Conversation start failed: {str(e)}"}
    
    def continue_conversation(self, conversation_id, user_audio_data, conversation_history):
        """
        Continue conversation with Nova Sonic using speech input
        
        Args:
            conversation_id (str): Active conversation ID
            user_audio_data (str): Base64 encoded user audio
            conversation_history (list): Previous conversation turns
            
        Returns:
            dict: Maya's response with text and audio
        """
        try:
            # Build conversation context
            messages = self._build_conversation_context(conversation_history)
            
            # Add user audio input
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
            
            request_body = {
                "messages": messages,
                "inferenceConfig": {
                    "maxTokens": 300,
                    "temperature": 0.8,
                    "topP": 0.9
                },
                "additionalModelRequestFields": {
                    "audio": {
                        "format": "mp3",
                        "voice": "amy"
                    }
                }
            }
            
            logger.info("Processing Nova Sonic speech-to-speech turn")
            
            response = self.client.invoke_model(
                modelId='amazon.nova-sonic-v1:0',
                contentType='application/json',
                accept='application/json',
                body=json.dumps(request_body)
            )
            
            result = json.loads(response['body'].read())
            
            # Parse response for text, audio, and user transcription
            examiner_text, audio_data = self._parse_nova_response(result)
            user_transcription = self._extract_user_transcription(result)
            
            logger.info(f"Nova Sonic response: {examiner_text[:100]}...")
            logger.info(f"User transcription: {user_transcription[:100]}...")
            
            return {
                "success": True,
                "conversation_id": conversation_id,
                "examiner_response": examiner_text,
                "user_transcription": user_transcription,
                "audio_data": audio_data,
                "audio_url": f"data:audio/mp3;base64,{audio_data}" if audio_data else None,
                "session_active": True
            }
            
        except ClientError as e:
            logger.error(f"Nova Sonic conversation error: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected conversation error: {e}")
            return {"success": False, "error": str(e)}
    
    def _build_examiner_prompt(self, assessment_type, part):
        """Build comprehensive examiner prompt with authentic IELTS questions"""
        
        # Get authentic examiner script from database
        script, additional_data = IELTSQuestionDatabase.build_examiner_script(assessment_type, part)
        
        # Store additional questions/data for conversation flow
        self.current_questions = additional_data if isinstance(additional_data, list) else []
        self.current_part = part
        self.assessment_type = assessment_type
        
        # Enhanced system prompt with authentic IELTS structure
        base_prompt = f"""You are Maya, a certified IELTS Speaking examiner conducting an official speaking assessment.
        
        IMPORTANT GUIDELINES:
        - Follow authentic IELTS test procedures and timing
        - Ask questions naturally, one at a time
        - Listen to candidate responses and ask appropriate follow-up questions
        - Maintain professional but friendly demeanor
        - For Part 1: 4-5 minutes covering 2-3 familiar topics
        - For Part 2: Give cue card, 1 minute preparation, 1-2 minute speech
        - For Part 3: 4-5 minutes with abstract discussion questions
        
        Your opening: {script}"""
        
        return base_prompt
    
    def _build_conversation_context(self, conversation_history):
        """Build conversation context from history for Nova Sonic"""
        
        messages = [
            {
                "role": "system",
                "content": [{"text": "You are Maya, a professional IELTS Speaking examiner. Continue the conversation naturally."}]
            }
        ]
        
        # Add recent conversation history (last 5 turns for context)
        for turn in conversation_history[-5:]:
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
        
        return messages
    
    def _parse_nova_response(self, result):
        """Parse Nova Sonic response to extract text and audio"""
        
        examiner_text = ""
        audio_data = None
        
        if 'output' in result and 'message' in result['output']:
            content = result['output']['message'].get('content', [])
            for item in content:
                if isinstance(item, dict):
                    if 'text' in item:
                        examiner_text = item['text']
                    elif 'audio' in item:
                        # Nova Sonic audio format handling
                        if 'source' in item['audio'] and 'bytes' in item['audio']['source']:
                            audio_data = item['audio']['source']['bytes']
                        elif isinstance(item['audio'], str):
                            audio_data = item['audio']
        
        return examiner_text, audio_data
    
    def _extract_user_transcription(self, result):
        """Extract user speech transcription from Nova Sonic response"""
        
        user_transcription = ""
        
        if 'input' in result and 'transcription' in result['input']:
            user_transcription = result['input']['transcription']
        elif 'metadata' in result and 'inputTranscription' in result['metadata']:
            user_transcription = result['metadata']['inputTranscription']
        
        return user_transcription

    def generate_speech_only(self, text):
        """
        Generate speech from text using Nova Sonic (for backward compatibility)
        
        Args:
            text (str): Text to convert to speech
            
        Returns:
            dict: Audio data and success status
        """
        try:
            request_body = {
                "messages": [
                    {
                        "role": "user",
                        "content": [{"text": text}]
                    }
                ],
                "inferenceConfig": {
                    "maxTokens": 10,
                    "temperature": 0.7
                },
                "additionalModelRequestFields": {
                    "audio": {
                        "format": "mp3"
                    }
                }
            }
            
            response = self.client.invoke_model(
                modelId='amazon.nova-sonic-v1:0',
                contentType='application/json',
                accept='application/json',
                body=json.dumps(request_body)
            )
            
            result = json.loads(response['body'].read())
            _, audio_data = self._parse_nova_response(result)
            
            return {
                "success": True,
                "audio_data": audio_data,
                "audio_url": f"data:audio/mp3;base64,{audio_data}" if audio_data else None
            }
            
        except Exception as e:
            logger.error(f"Nova Sonic speech generation error: {e}")
            return {"success": False, "error": str(e)}

    def finalize_conversation_assessment(self, conversation_history, assessment_data):
        """
        Generate final assessment using Nova Sonic based on conversation history
        
        Args:
            conversation_history (list): Complete conversation turns
            assessment_data (dict): Assessment metadata
            
        Returns:
            dict: Final assessment results
        """
        try:
            # Build assessment prompt
            assessment_prompt = f"""
            You are Maya, an IELTS Speaking examiner. Based on the conversation history provided, 
            give a comprehensive assessment of the candidate's speaking performance.
            
            Evaluate on these criteria:
            - Fluency and Coherence (0-9)
            - Lexical Resource (0-9) 
            - Grammatical Range and Accuracy (0-9)
            - Pronunciation (0-9)
            
            Provide specific feedback and an overall band score.
            """
            
            # Build conversation summary for assessment
            conversation_text = ""
            for turn in conversation_history:
                speaker = "Candidate" if turn['speaker'].startswith('User') else "Examiner"
                conversation_text += f"{speaker}: {turn['message']}\n"
            
            request_body = {
                "messages": [
                    {
                        "role": "system",
                        "content": [{"text": assessment_prompt}]
                    },
                    {
                        "role": "user",
                        "content": [{"text": f"Please assess this conversation:\n\n{conversation_text}"}]
                    }
                ],
                "inferenceConfig": {
                    "maxTokens": 500,
                    "temperature": 0.3,
                    "topP": 0.9
                }
            }
            
            response = self.client.invoke_model(
                modelId='amazon.nova-sonic-v1:0',
                contentType='application/json',
                accept='application/json',
                body=json.dumps(request_body)
            )
            
            result = json.loads(response['body'].read())
            assessment_text, _ = self._parse_nova_response(result)
            
            return {
                "success": True,
                "assessment": assessment_text,
                "conversation_length": len(conversation_history),
                "assessment_type": assessment_data.get('assessment_type', 'speaking')
            }
            
        except Exception as e:
            logger.error(f"Nova Sonic assessment error: {e}")
            return {"success": False, "error": str(e)}