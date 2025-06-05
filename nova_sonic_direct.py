"""
Direct Nova Sonic Implementation
Specifically invokes amazon.nova-sonic-v1:0 for speech-to-speech IELTS conversations
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

class NovaSonicDirectService:
    """
    Direct Nova Sonic service for IELTS speech-to-speech conversations
    """
    
    def __init__(self):
        """Initialize Nova Sonic client directly"""
        try:
            self.client = boto3.client('bedrock-runtime', region_name='us-east-1')
            self.question_db = IELTSQuestionDatabase()
            self.rubric_scorer = IELTSRubricScorer()
            self.knowledge_base = NovaSonicKnowledgeBase()
            self.active_conversations = {}
            logger.info("Nova Sonic direct service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Nova Sonic service: {e}")
            raise
    
    def start_maya_conversation(self, assessment_type, part=1):
        """
        Start Maya conversation using Nova Sonic speech-to-speech
        
        Args:
            assessment_type (str): 'academic_speaking' or 'general_speaking'
            part (int): IELTS speaking part (1, 2, or 3)
            
        Returns:
            dict: Maya's welcome with speech and conversation ID
        """
        try:
            conversation_id = f"nova_sonic_{assessment_type}_{part}_{datetime.now().timestamp()}"
            
            # Get authentic IELTS questions
            questions = self._get_ielts_questions(assessment_type, part)
            
            # Build Maya's system prompt for Nova Sonic
            system_prompt = self._build_maya_system_prompt(assessment_type, part, questions)
            
            # Nova Sonic request with speech output
            request_body = {
                "messages": [
                    {
                        "role": "system",
                        "content": [{"text": system_prompt}]
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
            
            # Call Nova Sonic directly
            response = self.client.invoke_model(
                modelId='amazon.nova-sonic-v1:0',
                contentType='application/json',
                accept='application/json',
                body=json.dumps(request_body)
            )
            
            result = json.loads(response['body'].read())
            
            # Extract text and audio from Nova Sonic response
            content = result['output']['message']['content']
            maya_text = next((item['text'] for item in content if 'text' in item), "")
            maya_audio = next((item['audio'] for item in content if 'audio' in item), None)
            
            # Initialize conversation state
            self.active_conversations[conversation_id] = {
                'assessment_type': assessment_type,
                'part': part,
                'questions': questions,
                'current_question_index': 0,
                'conversation_history': [
                    {'role': 'assistant', 'content': maya_text, 'timestamp': datetime.now()}
                ],
                'start_time': datetime.now(),
                'performance_scores': []
            }
            
            return {
                'success': True,
                'conversation_id': conversation_id,
                'maya_text': maya_text,
                'maya_audio': maya_audio,
                'speech_enabled': True,
                'part_info': {
                    'part': part,
                    'assessment_type': assessment_type,
                    'questions_available': len(questions)
                }
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"Nova Sonic error: {error_code} - {error_message}")
            
            return {
                'success': False,
                'error': f"Nova Sonic access issue: {error_code}",
                'error_details': error_message,
                'requires_credentials': error_code in ['AccessDeniedException', 'ValidationException']
            }
            
        except Exception as e:
            logger.error(f"Failed to start Nova Sonic conversation: {e}")
            return {
                'success': False,
                'error': f"Nova Sonic initialization failed: {str(e)}"
            }
    
    def continue_maya_conversation(self, conversation_id, user_input, input_type='text'):
        """
        Continue conversation with Maya using Nova Sonic
        
        Args:
            conversation_id (str): Active conversation ID
            user_input (str): User's response (text or base64 audio)
            input_type (str): 'text' or 'audio'
            
        Returns:
            dict: Maya's speech response from Nova Sonic
        """
        try:
            if conversation_id not in self.active_conversations:
                return {'success': False, 'error': 'Conversation session not found'}
            
            conversation = self.active_conversations[conversation_id]
            
            # Process user input
            if input_type == 'audio':
                user_text = self._process_audio_input(user_input)
            else:
                user_text = user_input
            
            # Add user response to conversation history
            conversation['conversation_history'].append({
                'role': 'user',
                'content': user_text,
                'timestamp': datetime.now()
            })
            
            # Build conversation context for Nova Sonic
            messages = self._build_conversation_context(conversation)
            
            # Add user's current response
            messages.append({
                "role": "user",
                "content": [{"text": user_text}]
            })
            
            # Nova Sonic continuation request
            request_body = {
                "messages": messages,
                "inferenceConfig": {
                    "maxTokens": 150,
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
            
            # Call Nova Sonic for response
            response = self.client.invoke_model(
                modelId='amazon.nova-sonic-v1:0',
                contentType='application/json',
                accept='application/json',
                body=json.dumps(request_body)
            )
            
            result = json.loads(response['body'].read())
            
            # Extract Maya's response
            content = result['output']['message']['content']
            maya_text = next((item['text'] for item in content if 'text' in item), "")
            maya_audio = next((item['audio'] for item in content if 'audio' in item), None)
            
            # Score user's response using IELTS rubric
            response_score = self.rubric_scorer.score_speaking_response(
                user_text,
                conversation['assessment_type'],
                conversation['part']
            )
            conversation['performance_scores'].append(response_score)
            
            # Update conversation history
            conversation['conversation_history'].append({
                'role': 'assistant',
                'content': maya_text,
                'timestamp': datetime.now()
            })
            
            conversation['current_question_index'] += 1
            
            return {
                'success': True,
                'maya_text': maya_text,
                'maya_audio': maya_audio,
                'user_score': response_score,
                'conversation_continues': conversation['current_question_index'] < len(conversation['questions']),
                'progress': {
                    'current': conversation['current_question_index'],
                    'total': len(conversation['questions'])
                }
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"Nova Sonic continuation error: {error_code}")
            
            return {
                'success': False,
                'error': f"Nova Sonic error: {error_code}",
                'requires_credentials': error_code in ['AccessDeniedException', 'ValidationException']
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
            if conversation_id not in self.active_conversations:
                return {'success': False, 'error': 'Conversation not found'}
            
            conversation = self.active_conversations[conversation_id]
            current_part = conversation['part']
            
            if current_part >= 3:
                return self.finalize_assessment(conversation_id)
            
            next_part = current_part + 1
            assessment_type = conversation['assessment_type']
            
            # Clean up current conversation
            del self.active_conversations[conversation_id]
            
            # Start new part with Nova Sonic
            return self.start_maya_conversation(assessment_type, next_part)
            
        except Exception as e:
            logger.error(f"Part transition failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def finalize_assessment(self, conversation_id):
        """Generate final IELTS assessment report"""
        try:
            if conversation_id not in self.active_conversations:
                return {'success': False, 'error': 'Conversation not found'}
            
            conversation = self.active_conversations[conversation_id]
            
            # Generate comprehensive assessment
            final_report = self.rubric_scorer.generate_comprehensive_assessment(
                conversation['conversation_history'],
                conversation['performance_scores'],
                conversation['assessment_type']
            )
            
            # Clean up
            del self.active_conversations[conversation_id]
            
            return {
                'success': True,
                'final_assessment': final_report,
                'conversation_duration': (datetime.now() - conversation['start_time']).total_seconds()
            }
            
        except Exception as e:
            logger.error(f"Assessment finalization failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _get_ielts_questions(self, assessment_type, part):
        """Get authentic IELTS questions"""
        return self.question_db.get_questions_for_assessment(assessment_type, part)
    
    def _build_maya_system_prompt(self, assessment_type, part, questions):
        """Build Maya's system prompt for Nova Sonic"""
        
        part_instructions = {
            1: "Part 1: Personal questions about familiar topics (4-5 minutes)",
            2: "Part 2: Individual long turn with cue card (3-4 minutes)",
            3: "Part 3: Abstract discussion questions (4-5 minutes)"
        }
        
        return f"""You are Maya, a certified IELTS Speaking examiner conducting an official assessment using Nova Sonic speech-to-speech technology.

ASSESSMENT: {assessment_type.replace('_', ' ').title()}
PART: {part_instructions.get(part, f'Part {part}')}

EXAMINER INSTRUCTIONS:
- Start immediately with a warm, professional welcome
- Speak clearly with British English pronunciation
- Follow authentic IELTS test procedures
- Ask questions naturally, one at a time
- Provide encouraging feedback
- Maintain professional but friendly demeanor

QUESTIONS FOR THIS PART:
{json.dumps(questions[:3], indent=2)}

Begin now with your welcome message and first question. Speak as Maya would in a real IELTS test."""
    
    def _build_conversation_context(self, conversation):
        """Build conversation context for Nova Sonic"""
        messages = [
            {
                "role": "system",
                "content": [{"text": f"You are Maya, continuing an IELTS {conversation['assessment_type']} Part {conversation['part']} assessment. Respond naturally and ask your next appropriate question."}]
            }
        ]
        
        # Add recent conversation history (last 4 exchanges)
        recent_history = conversation['conversation_history'][-4:]
        for turn in recent_history:
            messages.append({
                "role": turn['role'],
                "content": [{"text": turn['content']}]
            })
        
        return messages
    
    def _process_audio_input(self, audio_data):
        """Process audio input for Nova Sonic"""
        # In production, this would handle audio transcription
        return "[Audio input received - transcription would be handled by Nova Sonic]"