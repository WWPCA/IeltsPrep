"""
Nova Sonic Fallback Service
Implements speech-to-speech conversation with automatic fallback to working Nova models
"""

import json
import boto3
import base64
import logging
from datetime import datetime
from botocore.exceptions import ClientError
from ielts_question_database import IELTSQuestionDatabase
from ielts_rubric_scorer import IELTSRubricScorer
from nova_sonic_knowledge_base import NovaSonicKnowledgeBase

logger = logging.getLogger(__name__)

class NovaSonicFallbackService:
    """
    Speech-enabled IELTS conversation service with automatic Nova model fallback
    """
    
    def __init__(self):
        """Initialize with automatic model detection"""
        try:
            self.client = boto3.client('bedrock-runtime', region_name='us-east-1')
            self.question_db = IELTSQuestionDatabase()
            self.rubric_scorer = IELTSRubricScorer()
            self.knowledge_base = NovaSonicKnowledgeBase()
            self.conversation_state = {}
            self.speech_enabled = self._detect_speech_capabilities()
            logger.info(f"Nova service initialized - Speech enabled: {self.speech_enabled}")
        except Exception as e:
            logger.error(f"Failed to initialize Nova service: {e}")
            raise
    
    def _detect_speech_capabilities(self):
        """Detect if Nova Sonic speech capabilities are available"""
        try:
            test_request = {
                "messages": [
                    {
                        "role": "system",
                        "content": [{"text": "Test"}]
                    }
                ],
                "inferenceConfig": {
                    "maxTokens": 10,
                    "temperature": 0.5
                },
                "additionalModelRequestFields": {
                    "audio": {
                        "format": "mp3",
                        "voice": "amy"
                    }
                }
            }
            
            self.client.invoke_model(
                modelId='amazon.nova-sonic-v1:0',
                contentType='application/json',
                accept='application/json',
                body=json.dumps(test_request)
            )
            
            logger.info("Nova Sonic speech capabilities detected")
            return True
            
        except Exception as e:
            logger.info(f"Nova Sonic not available, using text mode: {e}")
            return False
    
    def start_maya_conversation(self, assessment_type, part=1):
        """
        Start Maya conversation with immediate welcome message
        
        Args:
            assessment_type (str): 'academic_speaking' or 'general_speaking'
            part (int): IELTS speaking part (1, 2, or 3)
            
        Returns:
            dict: Maya's welcome with conversation state
        """
        try:
            conversation_id = f"{assessment_type}_{part}_{datetime.now().timestamp()}"
            
            # Get authentic IELTS questions for this assessment
            questions = self.question_db.get_part_questions(assessment_type, part)
            
            # Build Maya's system prompt with IELTS context
            system_prompt = self._build_maya_system_prompt(assessment_type, part, questions)
            
            # Get Maya's welcome message
            maya_response = self._get_maya_response(system_prompt, is_welcome=True)
            
            # Initialize conversation state
            self.conversation_state[conversation_id] = {
                'assessment_type': assessment_type,
                'part': part,
                'questions': questions,
                'current_question_index': 0,
                'conversation_history': [
                    {'role': 'assistant', 'content': maya_response['text'], 'timestamp': datetime.now()}
                ],
                'start_time': datetime.now(),
                'speech_enabled': maya_response.get('has_audio', False),
                'performance_scores': []
            }
            
            return {
                'success': True,
                'conversation_id': conversation_id,
                'maya_text': maya_response['text'],
                'maya_audio': maya_response.get('audio_data'),
                'speech_enabled': maya_response.get('has_audio', False),
                'part_info': {
                    'part': part,
                    'assessment_type': assessment_type,
                    'total_questions': len(questions)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to start Maya conversation: {e}")
            return {
                'success': False,
                'error': f"Could not start conversation: {str(e)}"
            }
    
    def continue_maya_conversation(self, conversation_id, user_input, input_type='text'):
        """
        Continue conversation with Maya
        
        Args:
            conversation_id (str): Active conversation identifier
            user_input (str): User's response (text or base64 audio)
            input_type (str): 'text' or 'audio'
            
        Returns:
            dict: Maya's response with assessment feedback
        """
        try:
            if conversation_id not in self.conversation_state:
                return {'success': False, 'error': 'Conversation session not found'}
            
            conversation = self.conversation_state[conversation_id]
            
            # Process user input based on type
            if input_type == 'audio' and conversation['speech_enabled']:
                user_text = self._process_audio_input(user_input)
            else:
                user_text = user_input
            
            # Add user response to conversation history
            conversation['conversation_history'].append({
                'role': 'user', 
                'content': user_text, 
                'timestamp': datetime.now()
            })
            
            # Score the user's response using IELTS rubric
            response_score = self.rubric_scorer.score_speaking_response(
                user_text,
                conversation['assessment_type'],
                conversation['part']
            )
            conversation['performance_scores'].append(response_score)
            
            # Generate Maya's response based on conversation context
            maya_response = self._generate_maya_followup(conversation, user_text)
            
            # Update conversation history
            conversation['conversation_history'].append({
                'role': 'assistant',
                'content': maya_response['text'],
                'timestamp': datetime.now()
            })
            
            # Advance question index if appropriate
            conversation['current_question_index'] += 1
            
            return {
                'success': True,
                'maya_text': maya_response['text'],
                'maya_audio': maya_response.get('audio_data'),
                'user_score': response_score,
                'conversation_continues': conversation['current_question_index'] < len(conversation['questions']),
                'progress': {
                    'current_question': conversation['current_question_index'],
                    'total_questions': len(conversation['questions'])
                }
            }
            
        except Exception as e:
            logger.error(f"Conversation continuation failed: {e}")
            return {
                'success': False,
                'error': f"Could not continue conversation: {str(e)}"
            }
    
    def transition_to_next_part(self, conversation_id):
        """Transition to next IELTS speaking part"""
        try:
            if conversation_id not in self.conversation_state:
                return {'success': False, 'error': 'Conversation not found'}
            
            conversation = self.conversation_state[conversation_id]
            current_part = conversation['part']
            
            if current_part >= 3:
                return self.finalize_assessment(conversation_id)
            
            next_part = current_part + 1
            assessment_type = conversation['assessment_type']
            
            # Clean up current conversation
            del self.conversation_state[conversation_id]
            
            # Start new conversation for next part
            return self.start_maya_conversation(assessment_type, next_part)
            
        except Exception as e:
            logger.error(f"Part transition failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def finalize_assessment(self, conversation_id):
        """Generate comprehensive IELTS assessment report"""
        try:
            if conversation_id not in self.conversation_state:
                return {'success': False, 'error': 'Conversation not found'}
            
            conversation = self.conversation_state[conversation_id]
            
            # Generate comprehensive assessment using conversation history
            final_assessment = self.rubric_scorer.generate_comprehensive_assessment(
                conversation['conversation_history'],
                conversation['performance_scores'],
                conversation['assessment_type']
            )
            
            # Clean up conversation state
            del self.conversation_state[conversation_id]
            
            return {
                'success': True,
                'final_assessment': final_assessment,
                'conversation_duration': (datetime.now() - conversation['start_time']).total_seconds()
            }
            
        except Exception as e:
            logger.error(f"Assessment finalization failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _build_maya_system_prompt(self, assessment_type, part, questions):
        """Build comprehensive Maya system prompt"""
        
        part_descriptions = {
            1: "Part 1: Personal questions about familiar topics (4-5 minutes)",
            2: "Part 2: Individual long turn with cue card topic (3-4 minutes)",
            3: "Part 3: Abstract discussion questions (4-5 minutes)"
        }
        
        questions_preview = questions[:3] if len(questions) > 3 else questions
        
        return f"""You are Maya, a certified IELTS Speaking examiner conducting an official assessment.

CURRENT ASSESSMENT: {assessment_type.replace('_', ' ').title()}
CURRENT PART: {part_descriptions.get(part, f'Part {part}')}

EXAMINER INSTRUCTIONS:
- Start immediately with a warm, professional welcome
- Follow authentic IELTS test procedures
- Ask questions naturally, one at a time
- Listen carefully and provide appropriate follow-up questions
- Maintain British English pronunciation and vocabulary
- Be encouraging but maintain professional standards

AVAILABLE QUESTIONS FOR THIS PART:
{json.dumps(questions_preview, indent=2)}

Begin now with your welcome message and first question. Speak as Maya would in a real IELTS test."""
    
    def _get_maya_response(self, system_prompt, is_welcome=False):
        """Get Maya's response using available Nova model"""
        
        messages = [
            {
                "role": "system",
                "content": [{"text": system_prompt}]
            }
        ]
        
        # Try Nova Sonic with speech first
        if self.speech_enabled:
            try:
                request_body = {
                    "messages": messages,
                    "inferenceConfig": {
                        "maxTokens": 200 if is_welcome else 150,
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
                
                # Extract text and audio from response
                message_content = result['output']['message']['content']
                text_content = next((item['text'] for item in message_content if 'text' in item), "")
                audio_content = next((item['audio'] for item in message_content if 'audio' in item), None)
                
                return {
                    'text': text_content,
                    'audio_data': audio_content,
                    'has_audio': audio_content is not None
                }
                
            except Exception as e:
                logger.warning(f"Nova Sonic failed, falling back to Nova Lite: {e}")
                self.speech_enabled = False
        
        # Fallback to Nova Lite (text-only)
        try:
            request_body = {
                "messages": messages,
                "inferenceConfig": {
                    "maxTokens": 200 if is_welcome else 150,
                    "temperature": 0.7,
                    "topP": 0.9
                }
            }
            
            response = self.client.invoke_model(
                modelId='amazon.nova-lite-v1:0',
                contentType='application/json',
                accept='application/json',
                body=json.dumps(request_body)
            )
            
            result = json.loads(response['body'].read())
            text_content = result['output']['message']['content'][0]['text']
            
            return {
                'text': text_content,
                'has_audio': False
            }
            
        except Exception as e:
            logger.error(f"Both Nova models failed: {e}")
            raise
    
    def _generate_maya_followup(self, conversation, user_text):
        """Generate Maya's follow-up response based on conversation context"""
        
        # Build conversation context
        recent_history = conversation['conversation_history'][-4:]  # Last 4 exchanges
        
        context_prompt = f"""You are Maya, continuing an IELTS speaking assessment. 
Assessment: {conversation['assessment_type']} Part {conversation['part']}

Recent conversation:
{json.dumps([{'role': turn['role'], 'content': turn['content']} for turn in recent_history], indent=2)}

The candidate just said: "{user_text}"

Respond naturally as Maya would - acknowledge their answer and ask your next appropriate question. Keep responses concise and encouraging."""
        
        return self._get_maya_response(context_prompt, is_welcome=False)
    
    def _process_audio_input(self, audio_data):
        """Process audio input and convert to text"""
        # In production, this would use AWS Transcribe or similar
        # For now, return placeholder indicating audio was received
        return "[Audio response received - transcription would be implemented here]"