"""
Nova Conversation Service for IELTS Assessments
Provides speech-enabled conversation with fallback to text-based interaction
"""

import os
import boto3
import json
import logging
import base64
from datetime import datetime
from botocore.exceptions import ClientError
from ielts_question_database import IELTSQuestionDatabase
from ielts_rubric_scorer import IELTSRubricScorer
from nova_sonic_knowledge_base import NovaSonicKnowledgeBase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NovaConversationService:
    """Enhanced conversation service with speech capabilities"""
    
    def __init__(self):
        self.client = boto3.client('bedrock-runtime', region_name='us-east-1')
        self.question_db = IELTSQuestionDatabase()
        self.rubric_scorer = IELTSRubricScorer()
        self.knowledge_base = NovaSonicKnowledgeBase()
        self.active_conversations = {}
        
    def start_maya_conversation(self, assessment_type, part=1):
        """
        Start Maya conversation with immediate welcome message
        
        Args:
            assessment_type (str): 'academic_speaking' or 'general_speaking'
            part (int): IELTS speaking part (1, 2, or 3)
            
        Returns:
            dict: Maya's welcome response with conversation ID
        """
        try:
            conversation_id = f"{assessment_type}_{part}_{datetime.now().timestamp()}"
            
            # Get authentic IELTS questions for this part
            questions_data = self.question_db.get_questions_for_part(assessment_type, part)
            
            # Build Maya's system prompt
            system_prompt = self._build_maya_prompt(assessment_type, part, questions_data)
            
            # Try Nova Sonic first, fallback to Nova Lite
            response = self._get_maya_welcome(system_prompt)
            
            # Store conversation state
            self.active_conversations[conversation_id] = {
                'assessment_type': assessment_type,
                'part': part,
                'questions': questions_data,
                'history': [{'role': 'assistant', 'content': response['text']}],
                'start_time': datetime.now(),
                'audio_enabled': response.get('audio_enabled', False)
            }
            
            return {
                'success': True,
                'conversation_id': conversation_id,
                'maya_text': response['text'],
                'maya_audio': response.get('audio'),
                'audio_enabled': response.get('audio_enabled', False),
                'part': part,
                'assessment_type': assessment_type
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
            dict: Maya's response with assessment scoring
        """
        try:
            if conversation_id not in self.active_conversations:
                return {'success': False, 'error': 'Conversation not found'}
            
            conversation = self.active_conversations[conversation_id]
            
            # Process user input
            if input_type == 'audio':
                # Convert audio to text (would use speech recognition service)
                user_text = self._convert_audio_to_text(user_input)
            else:
                user_text = user_input
            
            # Add user response to history
            conversation['history'].append({'role': 'user', 'content': user_text})
            
            # Get Maya's response
            maya_response = self._get_maya_response(conversation, user_text)
            
            # Score the user's response
            scoring = self.rubric_scorer.score_response(
                user_text,
                conversation['assessment_type'],
                conversation['part']
            )
            
            # Update conversation history
            conversation['history'].append({'role': 'assistant', 'content': maya_response['text']})
            
            return {
                'success': True,
                'maya_text': maya_response['text'],
                'maya_audio': maya_response.get('audio'),
                'scoring': scoring,
                'conversation_continues': True
            }
            
        except Exception as e:
            logger.error(f"Conversation continuation failed: {e}")
            return {
                'success': False,
                'error': f"Conversation error: {str(e)}"
            }
    
    def transition_to_next_part(self, conversation_id):
        """Transition to next IELTS speaking part"""
        try:
            if conversation_id not in self.active_conversations:
                return {'success': False, 'error': 'Conversation not found'}
            
            conversation = self.active_conversations[conversation_id]
            current_part = conversation['part']
            
            if current_part >= 3:
                return {'success': False, 'error': 'Already at final part'}
            
            next_part = current_part + 1
            assessment_type = conversation['assessment_type']
            
            # Start new conversation for next part
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
            final_assessment = self.rubric_scorer.generate_final_assessment(
                conversation['history'],
                conversation['assessment_type']
            )
            
            # Clean up conversation
            del self.active_conversations[conversation_id]
            
            return {
                'success': True,
                'final_assessment': final_assessment
            }
            
        except Exception as e:
            logger.error(f"Assessment finalization failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _build_maya_prompt(self, assessment_type, part, questions_data):
        """Build Maya's system prompt with IELTS context"""
        
        part_instructions = {
            1: "Part 1: Personal questions (4-5 minutes). Ask about familiar topics like home, work, studies, hobbies.",
            2: "Part 2: Individual long turn (3-4 minutes). Give a cue card topic, allow 1 minute preparation, then 1-2 minute speech.",
            3: "Part 3: Discussion (4-5 minutes). Ask abstract questions related to Part 2 topic."
        }
        
        base_prompt = f"""You are Maya, a certified IELTS Speaking examiner conducting an official assessment.

CURRENT TASK: {part_instructions.get(part, 'Speaking assessment')}
ASSESSMENT TYPE: {assessment_type.replace('_', ' ').title()}

INSTRUCTIONS:
- Start immediately with a warm welcome and your first question
- Follow authentic IELTS procedures and timing
- Ask questions naturally, one at a time
- Listen carefully and ask appropriate follow-up questions
- Maintain professional but friendly demeanor
- Use British English pronunciation and vocabulary

AVAILABLE QUESTIONS: {json.dumps(questions_data[:3])}

Begin now with your welcome and first question."""

        return base_prompt
    
    def _get_maya_welcome(self, system_prompt):
        """Get Maya's welcome message, trying speech-enabled first"""
        
        # Try Nova Sonic first (speech-to-speech)
        try:
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
            
            response = self.client.invoke_model(
                modelId='amazon.nova-sonic-v1:0',
                contentType='application/json',
                accept='application/json',
                body=json.dumps(request_body)
            )
            
            result = json.loads(response['body'].read())
            
            return {
                'text': result['output']['message']['content'][0]['text'],
                'audio': result['output']['message']['content'][1]['audio'] if len(result['output']['message']['content']) > 1 else None,
                'audio_enabled': True
            }
            
        except Exception as e:
            logger.warning(f"Nova Sonic failed, using Nova Lite: {e}")
            
            # Fallback to Nova Lite (text-only)
            try:
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
                    }
                }
                
                response = self.client.invoke_model(
                    modelId='amazon.nova-lite-v1:0',
                    contentType='application/json',
                    accept='application/json',
                    body=json.dumps(request_body)
                )
                
                result = json.loads(response['body'].read())
                
                return {
                    'text': result['output']['message']['content'][0]['text'],
                    'audio_enabled': False
                }
                
            except Exception as e2:
                logger.error(f"Both Nova models failed: {e2}")
                raise e2
    
    def _get_maya_response(self, conversation, user_text):
        """Get Maya's response to user input"""
        
        # Build conversation context
        messages = [
            {
                "role": "system",
                "content": [{"text": f"You are Maya, continuing an IELTS assessment. Respond naturally to the candidate's answer and ask your next question. Assessment type: {conversation['assessment_type']}, Part: {conversation['part']}"}]
            }
        ]
        
        # Add recent conversation history
        for turn in conversation['history'][-4:]:  # Last 4 turns for context
            messages.append({
                "role": turn['role'],
                "content": [{"text": turn['content']}]
            })
        
        # Try Nova Sonic first, fallback to Nova Lite
        try:
            if conversation.get('audio_enabled'):
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
                
                response = self.client.invoke_model(
                    modelId='amazon.nova-sonic-v1:0',
                    contentType='application/json',
                    accept='application/json',
                    body=json.dumps(request_body)
                )
                
                result = json.loads(response['body'].read())
                
                return {
                    'text': result['output']['message']['content'][0]['text'],
                    'audio': result['output']['message']['content'][1]['audio'] if len(result['output']['message']['content']) > 1 else None
                }
            else:
                raise Exception("Audio not enabled, using text mode")
                
        except Exception:
            # Fallback to Nova Lite
            request_body = {
                "messages": messages,
                "inferenceConfig": {
                    "maxTokens": 150,
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
            
            return {
                'text': result['output']['message']['content'][0]['text']
            }
    
    def _convert_audio_to_text(self, audio_data):
        """Convert base64 audio to text (placeholder for speech recognition)"""
        # In production, this would use AWS Transcribe or similar service
        return "[Audio transcription would be implemented here]"