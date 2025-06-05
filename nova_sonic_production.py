"""
Nova Sonic Production Implementation
Direct amazon.nova-sonic-v1:0 invocation for IELTS speech-to-speech assessments
"""

import json
import boto3
import logging
from datetime import datetime
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class NovaSonicProductionService:
    """
    Production Nova Sonic service for IELTS assessments
    """
    
    def __init__(self):
        """Initialize Nova Sonic for production use"""
        self.client = boto3.client('bedrock-runtime', region_name='us-east-1')
        self.active_conversations = {}
        logger.info("Nova Sonic production service initialized")
    
    def start_maya_conversation(self, assessment_type, part=1):
        """
        Start Maya conversation with Nova Sonic speech-to-speech
        
        Args:
            assessment_type (str): 'academic_speaking' or 'general_speaking'
            part (int): IELTS speaking part (1, 2, or 3)
            
        Returns:
            dict: Maya's welcome response with speech
        """
        try:
            conversation_id = f"maya_{assessment_type}_{part}_{datetime.now().timestamp()}"
            
            # Get authentic IELTS questions
            questions = self._get_authentic_ielts_questions(assessment_type, part)
            
            # Build Maya's prompt
            system_prompt = self._build_maya_prompt(assessment_type, part, questions)
            
            # Nova Sonic request for Maya's welcome
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
            
            # Extract Maya's text and audio
            content = result['output']['message']['content']
            maya_text = next((item['text'] for item in content if 'text' in item), "")
            maya_audio = next((item['audio'] for item in content if 'audio' in item), None)
            
            # Initialize conversation state
            self.active_conversations[conversation_id] = {
                'assessment_type': assessment_type,
                'part': part,
                'questions': questions,
                'conversation_history': [
                    {'role': 'assistant', 'content': maya_text}
                ],
                'start_time': datetime.now(),
                'current_question_index': 0
            }
            
            return {
                'success': True,
                'conversation_id': conversation_id,
                'maya_text': maya_text,
                'maya_audio': maya_audio,
                'speech_enabled': True,
                'model_used': 'amazon.nova-sonic-v1:0'
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            logger.error(f"Nova Sonic error: {error_code} - {error_message}")
            
            return {
                'success': False,
                'error': f"Nova Sonic access required: {error_code}",
                'error_details': error_message,
                'model_attempted': 'amazon.nova-sonic-v1:0',
                'requires_access': True
            }
            
        except Exception as e:
            logger.error(f"Nova Sonic initialization failed: {e}")
            return {
                'success': False,
                'error': f"Service error: {str(e)}"
            }
    
    def continue_maya_conversation(self, conversation_id, user_input):
        """
        Continue conversation with Maya using Nova Sonic
        
        Args:
            conversation_id (str): Active conversation ID
            user_input (str): User's text response
            
        Returns:
            dict: Maya's speech response
        """
        try:
            if conversation_id not in self.active_conversations:
                return {'success': False, 'error': 'Conversation not found'}
            
            conversation = self.active_conversations[conversation_id]
            
            # Add user response
            conversation['conversation_history'].append({
                'role': 'user',
                'content': user_input
            })
            
            # Build conversation context
            messages = self._build_conversation_messages(conversation)
            
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
            
            # Update conversation
            conversation['conversation_history'].append({
                'role': 'assistant',
                'content': maya_text
            })
            
            conversation['current_question_index'] += 1
            
            return {
                'success': True,
                'maya_text': maya_text,
                'maya_audio': maya_audio,
                'conversation_continues': True
            }
            
        except Exception as e:
            logger.error(f"Conversation continuation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def generate_speech_only(self, text):
        """
        Generate speech from text using Nova Sonic
        
        Args:
            text (str): Text to convert to speech
            
        Returns:
            dict: Speech generation result
        """
        try:
            request_body = {
                "messages": [
                    {
                        "role": "system",
                        "content": [{"text": f"Say this text clearly: {text}"}]
                    }
                ],
                "inferenceConfig": {
                    "maxTokens": 50,
                    "temperature": 0.5
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
            content = result['output']['message']['content']
            
            audio_data = next((item['audio'] for item in content if 'audio' in item), None)
            
            return {
                'success': True,
                'audio_data': audio_data,
                'model_used': 'amazon.nova-sonic-v1:0'
            }
            
        except Exception as e:
            logger.error(f"Speech generation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'requires_access': 'ValidationException' in str(e)
            }
    
    def _get_authentic_ielts_questions(self, assessment_type, part):
        """Get authentic IELTS questions for assessment"""
        
        # Authentic IELTS Part 1 questions
        if part == 1:
            if 'academic' in assessment_type:
                return [
                    "Let's talk about your studies. What subject are you studying?",
                    "Why did you choose this field of study?",
                    "What do you find most challenging about your studies?",
                    "How do you think your studies will help you in the future?",
                    "Now let's discuss your hometown. Where are you from?",
                    "What do you like most about your hometown?",
                    "Has your hometown changed much since you were a child?",
                    "Would you recommend your hometown to visitors? Why?"
                ]
            else:
                return [
                    "Let's talk about your work. What kind of work do you do?",
                    "How long have you been doing this job?",
                    "What do you enjoy most about your work?",
                    "What are your plans for the future regarding work?",
                    "Now let's discuss your free time. What do you like to do when you're not working?",
                    "Have your hobbies changed since you were younger?",
                    "Do you prefer spending time alone or with other people?",
                    "Is there a new hobby you would like to try?"
                ]
        
        # Authentic IELTS Part 2 cue cards
        elif part == 2:
            return [
                {
                    "topic": "Describe a book that had a significant impact on you",
                    "points": [
                        "What the book was about",
                        "When you read it", 
                        "Why it was significant to you",
                        "How it influenced your thinking"
                    ]
                },
                {
                    "topic": "Describe a place you visited that you found particularly interesting",
                    "points": [
                        "Where this place was",
                        "When you went there",
                        "What you did there",
                        "Why you found it so interesting"
                    ]
                }
            ]
        
        # Authentic IELTS Part 3 discussion questions
        else:
            return [
                "How important do you think reading is in today's digital age?",
                "What role should governments play in promoting literacy?",
                "Do you think people read less now than in the past? Why?",
                "How has technology changed the way people travel?",
                "What are the positive and negative effects of tourism on local communities?",
                "Do you think virtual travel experiences could replace real travel in the future?"
            ]
    
    def _build_maya_prompt(self, assessment_type, part, questions):
        """Build Maya's system prompt"""
        
        part_descriptions = {
            1: "Part 1: Personal questions about familiar topics (4-5 minutes)",
            2: "Part 2: Individual long turn with cue card topic (3-4 minutes)",
            3: "Part 3: Abstract discussion questions related to Part 2 (4-5 minutes)"
        }
        
        return f"""You are Maya, a certified IELTS Speaking examiner conducting an official assessment.

ASSESSMENT TYPE: {assessment_type.replace('_', ' ').title()}
CURRENT PART: {part_descriptions.get(part, f'Part {part}')}

EXAMINER INSTRUCTIONS:
- Start immediately with a warm, professional welcome
- Use clear British English pronunciation
- Follow authentic IELTS test procedures
- Ask questions naturally, one at a time
- Listen carefully and provide appropriate follow-up questions
- Maintain encouraging but professional demeanor

QUESTIONS FOR THIS PART:
{json.dumps(questions[:3], indent=2)}

Begin now with your welcome message and first question. Speak as Maya would in a real IELTS speaking test."""
    
    def _build_conversation_messages(self, conversation):
        """Build conversation messages for Nova Sonic"""
        messages = [
            {
                "role": "system",
                "content": [{"text": f"You are Maya, continuing an IELTS {conversation['assessment_type']} Part {conversation['part']} assessment. Respond naturally to the candidate's answer and ask your next appropriate question."}]
            }
        ]
        
        # Add recent conversation history
        for turn in conversation['conversation_history'][-4:]:
            messages.append({
                "role": turn['role'],
                "content": [{"text": turn['content']}]
            })
        
        return messages