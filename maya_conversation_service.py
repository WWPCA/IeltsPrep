"""
Maya Conversation Service for IELTS Assessments
Comprehensive speech-enabled IELTS conversation system with automatic model detection
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

class MayaConversationService:
    """
    Maya conversation service with automatic model detection and speech capabilities
    """
    
    def __init__(self):
        """Initialize Maya conversation service"""
        try:
            self.client = boto3.client('bedrock-runtime', region_name='us-east-1')
            self.question_db = IELTSQuestionDatabase()
            self.rubric_scorer = IELTSRubricScorer()
            self.knowledge_base = NovaSonicKnowledgeBase()
            
            # Detect available models and capabilities
            self.available_models = self._detect_available_models()
            self.best_model = self._select_best_model()
            self.speech_enabled = self._test_speech_capabilities()
            
            # Conversation state management
            self.active_conversations = {}
            
            logger.info(f"Maya service initialized - Model: {self.best_model}, Speech: {self.speech_enabled}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Maya service: {e}")
            # Fallback to OpenAI if AWS fails
            self.best_model = 'openai'
            self.speech_enabled = False
            logger.info("Using OpenAI fallback for Maya conversations")
    
    def _detect_available_models(self):
        """Detect which Nova models are available"""
        models_to_test = [
            'amazon.nova-sonic-v1:0',
            'amazon.nova-lite-v1:0',
            'amazon.nova-micro-v1:0'
        ]
        
        available = []
        
        for model_id in models_to_test:
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
                    }
                }
                
                self.client.invoke_model(
                    modelId=model_id,
                    contentType='application/json',
                    accept='application/json',
                    body=json.dumps(test_request)
                )
                
                available.append(model_id)
                logger.info(f"Model {model_id} available")
                
            except Exception:
                logger.info(f"Model {model_id} not available")
        
        return available
    
    def _select_best_model(self):
        """Select the best available model for Maya conversations"""
        # Priority order: Nova Sonic > Nova Lite > Nova Micro > OpenAI
        if 'amazon.nova-sonic-v1:0' in self.available_models:
            return 'amazon.nova-sonic-v1:0'
        elif 'amazon.nova-lite-v1:0' in self.available_models:
            return 'amazon.nova-lite-v1:0'
        elif 'amazon.nova-micro-v1:0' in self.available_models:
            return 'amazon.nova-micro-v1:0'
        else:
            return 'openai'
    
    def _test_speech_capabilities(self):
        """Test if speech capabilities are available"""
        if self.best_model == 'openai' or 'sonic' not in self.best_model:
            return False
        
        try:
            test_request = {
                "messages": [
                    {
                        "role": "system",
                        "content": [{"text": "Test speech"}]
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
                modelId=self.best_model,
                contentType='application/json',
                accept='application/json',
                body=json.dumps(test_request)
            )
            
            return True
            
        except Exception:
            return False
    
    def start_maya_conversation(self, assessment_type, part=1):
        """
        Start Maya conversation with immediate welcome
        
        Args:
            assessment_type (str): 'academic_speaking' or 'general_speaking'
            part (int): IELTS speaking part (1, 2, or 3)
            
        Returns:
            dict: Maya's welcome response with conversation ID
        """
        try:
            conversation_id = f"maya_{assessment_type}_{part}_{datetime.now().timestamp()}"
            
            # Get authentic IELTS questions for this part
            questions = self._get_ielts_questions(assessment_type, part)
            
            # Build Maya's system prompt
            system_prompt = self._build_maya_prompt(assessment_type, part, questions)
            
            # Get Maya's welcome message
            maya_response = self._get_maya_response(system_prompt, is_welcome=True)
            
            # Initialize conversation state
            self.active_conversations[conversation_id] = {
                'assessment_type': assessment_type,
                'part': part,
                'questions': questions,
                'current_question_index': 0,
                'conversation_history': [
                    {'role': 'assistant', 'content': maya_response['text'], 'timestamp': datetime.now()}
                ],
                'start_time': datetime.now(),
                'performance_tracking': [],
                'speech_enabled': maya_response.get('has_audio', False)
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
                    'questions_available': len(questions)
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
            conversation_id (str): Active conversation ID
            user_input (str): User's response (text or base64 audio)
            input_type (str): 'text' or 'audio'
            
        Returns:
            dict: Maya's response with scoring
        """
        try:
            if conversation_id not in self.active_conversations:
                return {'success': False, 'error': 'Conversation not found'}
            
            conversation = self.active_conversations[conversation_id]
            
            # Process user input
            if input_type == 'audio':
                user_text = self._transcribe_audio(user_input)
            else:
                user_text = user_input
            
            # Add user response to history
            conversation['conversation_history'].append({
                'role': 'user',
                'content': user_text,
                'timestamp': datetime.now()
            })
            
            # Score user's response
            response_score = self._score_user_response(
                user_text,
                conversation['assessment_type'],
                conversation['part']
            )
            conversation['performance_tracking'].append(response_score)
            
            # Generate Maya's response
            maya_response = self._generate_maya_followup(conversation, user_text)
            
            # Update conversation history
            conversation['conversation_history'].append({
                'role': 'assistant',
                'content': maya_response['text'],
                'timestamp': datetime.now()
            })
            
            # Update question index
            conversation['current_question_index'] += 1
            
            return {
                'success': True,
                'maya_text': maya_response['text'],
                'maya_audio': maya_response.get('audio_data'),
                'user_score': response_score,
                'conversation_continues': conversation['current_question_index'] < len(conversation['questions']),
                'progress': {
                    'current': conversation['current_question_index'],
                    'total': len(conversation['questions'])
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
            
            # Start new part
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
            final_report = self._generate_final_assessment(conversation)
            
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
        """Get authentic IELTS questions for assessment"""
        # Use question database to get real IELTS questions
        return self.question_db.get_questions_by_type_and_part(assessment_type, part)
    
    def _build_maya_prompt(self, assessment_type, part, questions):
        """Build Maya's system prompt with IELTS context"""
        
        part_instructions = {
            1: "Part 1: Personal questions about familiar topics (4-5 minutes)",
            2: "Part 2: Individual long turn with cue card (3-4 minutes)",
            3: "Part 3: Abstract discussion questions (4-5 minutes)"
        }
        
        return f"""You are Maya, a certified IELTS Speaking examiner conducting an official assessment.

ASSESSMENT: {assessment_type.replace('_', ' ').title()}
PART: {part_instructions.get(part, f'Part {part}')}

INSTRUCTIONS:
- Start immediately with a warm, professional welcome
- Follow authentic IELTS test procedures
- Ask questions naturally, one at a time
- Provide encouraging but honest feedback
- Use British English pronunciation and vocabulary

QUESTIONS FOR THIS PART:
{json.dumps(questions[:3], indent=2)}

Begin now with your welcome and first question."""
    
    def _get_maya_response(self, prompt, is_welcome=False):
        """Get Maya's response using best available model"""
        
        if self.best_model == 'openai':
            return self._get_openai_response(prompt, is_welcome)
        else:
            return self._get_nova_response(prompt, is_welcome)
    
    def _get_nova_response(self, prompt, is_welcome=False):
        """Get response from Nova model"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": [{"text": prompt}]
                }
            ]
            
            request_body = {
                "messages": messages,
                "inferenceConfig": {
                    "maxTokens": 200 if is_welcome else 150,
                    "temperature": 0.7,
                    "topP": 0.9
                }
            }
            
            # Add speech configuration if available
            if self.speech_enabled:
                request_body["additionalModelRequestFields"] = {
                    "audio": {
                        "format": "mp3",
                        "voice": "amy"
                    }
                }
            
            response = self.client.invoke_model(
                modelId=self.best_model,
                contentType='application/json',
                accept='application/json',
                body=json.dumps(request_body)
            )
            
            result = json.loads(response['body'].read())
            content = result['output']['message']['content']
            
            # Extract text and audio
            text_content = next((item['text'] for item in content if 'text' in item), "")
            audio_content = next((item['audio'] for item in content if 'audio' in item), None)
            
            return {
                'text': text_content,
                'audio_data': audio_content,
                'has_audio': audio_content is not None
            }
            
        except Exception as e:
            logger.error(f"Nova response failed: {e}")
            # Fallback to OpenAI
            return self._get_openai_response(prompt, is_welcome)
    
    def _get_openai_response(self, prompt, is_welcome=False):
        """Get response from OpenAI as fallback"""
        try:
            import openai
            import os
            
            client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
            
            response = client.chat.completions.create(
                model='gpt-4o',
                messages=[
                    {'role': 'system', 'content': prompt}
                ],
                max_tokens=200 if is_welcome else 150,
                temperature=0.7
            )
            
            return {
                'text': response.choices[0].message.content,
                'has_audio': False
            }
            
        except Exception as e:
            logger.error(f"OpenAI fallback failed: {e}")
            return {
                'text': "Hello! I'm Maya, your IELTS examiner. Let's begin your speaking assessment.",
                'has_audio': False
            }
    
    def _generate_maya_followup(self, conversation, user_text):
        """Generate Maya's follow-up response"""
        
        # Build context from recent conversation
        recent_turns = conversation['conversation_history'][-4:]
        
        context_prompt = f"""You are Maya, continuing an IELTS speaking assessment.

Assessment: {conversation['assessment_type']} Part {conversation['part']}

Recent conversation:
{json.dumps([{'role': turn['role'], 'content': turn['content']} for turn in recent_turns], indent=2)}

The candidate just said: "{user_text}"

Respond naturally as Maya - acknowledge their answer and ask your next appropriate question. Be encouraging but maintain professional standards."""
        
        return self._get_maya_response(context_prompt, is_welcome=False)
    
    def _score_user_response(self, user_text, assessment_type, part):
        """Score user's response using IELTS rubric"""
        return self.rubric_scorer.score_response(user_text, assessment_type, part)
    
    def _generate_final_assessment(self, conversation):
        """Generate comprehensive final assessment"""
        return self.rubric_scorer.generate_final_report(
            conversation['conversation_history'],
            conversation['performance_tracking'],
            conversation['assessment_type']
        )
    
    def _transcribe_audio(self, audio_data):
        """Transcribe audio input to text"""
        # Placeholder for audio transcription service
        return "[Audio transcription would be implemented here]"