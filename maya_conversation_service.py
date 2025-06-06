"""
Maya Conversation Service
Handles Nova Sonic speech-to-speech conversations with Maya as the IELTS examiner
"""

import json
import boto3
import logging
from datetime import datetime
from botocore.exceptions import ClientError, BotoCoreError

logger = logging.getLogger(__name__)

class MayaConversationService:
    """Maya conversation service using Nova Sonic for speech-to-speech IELTS speaking assessments"""
    
    def __init__(self):
        self.bedrock_client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize AWS Bedrock client for Nova Sonic"""
        try:
            self.bedrock_client = boto3.client(
                'bedrock-runtime',
                region_name='us-east-1'
            )
            logger.info("Maya conversation service initialized with Nova Sonic")
        except Exception as e:
            logger.error(f"Failed to initialize Maya service: {e}")
    
    def start_conversation(self, user_message, part_number=1, context=""):
        """Start or continue conversation with Maya using Nova Sonic"""
        try:
            if not self.bedrock_client:
                return self._error_response("Maya conversation service unavailable")
            
            # Get Maya's conversation prompt for the specific speaking part
            maya_prompt = self._get_maya_prompt(part_number, context)
            
            # Nova Sonic conversation request
            response = self.bedrock_client.converse(
                modelId="amazon.nova-sonic-v1:0",
                messages=[
                    {
                        "role": "system",
                        "content": [{"text": maya_prompt}]
                    },
                    {
                        "role": "user",
                        "content": [{"text": user_message}]
                    }
                ],
                inferenceConfig={
                    "temperature": 0.7,
                    "maxTokens": 300
                },
                additionalModelRequestFields={
                    "audio": {
                        "voice": "amy",  # British English for IELTS
                        "format": "mp3"
                    }
                }
            )
            
            if response.get('output') and response['output'].get('message'):
                maya_response = response['output']['message']['content'][0]['text']
                
                logger.info(f"Maya conversation completed for Part {part_number}")
                return {
                    "success": True,
                    "maya_response": maya_response,
                    "audio_available": True,
                    "part_number": part_number,
                    "conversation_context": context,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            return self._error_response("Invalid response from Maya")
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'AccessDeniedException':
                logger.error("Nova Sonic access denied - Maya conversations unavailable")
                return self._error_response("Maya conversation access denied - please check Nova Sonic permissions")
            else:
                logger.error(f"Maya conversation client error: {e}")
                return self._error_response(f"Maya service error: {error_code}")
        
        except Exception as e:
            logger.error(f"Unexpected Maya conversation error: {e}")
            return self._error_response(f"Maya conversation error: {str(e)}")
    
    def _get_maya_prompt(self, part_number, context=""):
        """Get Maya's conversation prompt for each IELTS speaking part"""
        base_prompt = """
        You are Maya, a friendly and professional IELTS Speaking examiner with a warm British accent. 
        You conduct natural, encouraging conversations while maintaining IELTS test standards.
        
        Guidelines:
        - Ask follow-up questions naturally and conversationally
        - Show genuine interest in the candidate's responses
        - Maintain appropriate formality but be warm and supportive
        - Keep responses conversational yet exam-focused
        - Provide gentle guidance if the candidate seems stuck
        - Use natural British expressions and intonation
        """
        
        if part_number == 1:
            return base_prompt + """
            This is Part 1: Introduction and Interview (4-5 minutes)
            
            Topics include: Home, family, work, studies, hobbies, interests, daily routines
            - Start with basic introductory questions
            - Ask personal questions that encourage elaboration
            - Help the candidate feel comfortable and confident
            - Follow up on their answers with natural questions
            """
        elif part_number == 2:
            return base_prompt + f"""
            This is Part 2: Long Turn (3-4 minutes)
            
            Context: {context}
            - Present the cue card topic clearly and encouragingly
            - Give the candidate 1 minute to prepare their notes
            - Guide them through their 2-minute talk
            - Encourage them to cover all points on the cue card
            - Ask one or two follow-up questions after their talk
            """
        else:  # Part 3
            return base_prompt + f"""
            This is Part 3: Discussion (4-5 minutes)
            
            Context: {context}
            - Engage in abstract discussion related to the Part 2 topic
            - Ask thought-provoking questions about broader themes
            - Encourage analysis, evaluation, and speculation
            - Discuss social issues, trends, and hypothetical situations
            - Help develop complex ideas and arguments
            """
    
    def _error_response(self, error_message):
        """Generate standardized error response"""
        return {
            'success': False,
            'error': error_message,
            'maya_available': False,
            'timestamp': datetime.utcnow().isoformat()
        }

# Global instance for easy import
maya_conversation_service = MayaConversationService()

# Convenience functions
def start_maya_conversation(user_message, part_number=1, context=""):
    """Start conversation with Maya"""
    return maya_conversation_service.start_conversation(user_message, part_number, context)