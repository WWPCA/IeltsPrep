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
from ielts_rubric_scorer import IELTSRubricScorer
from nova_sonic_knowledge_base import NovaSonicKnowledgeBase

logger = logging.getLogger(__name__)

class NovaSonicProperService:
    """
    Nova Sonic service implementing proper speech-to-speech conversations
    following AWS documentation guidelines
    """
    
    def __init__(self):
        """Initialize Nova Sonic client with conversation state management"""
        try:
            self.client = boto3.client('bedrock-runtime', region_name='us-east-1')
            self.conversation_state = {}
            self.performance_tracker = {}
            self.current_questions = []
            self.question_index = 0
            logger.info("Nova Sonic client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Nova Sonic client: {e}")
            raise
    
    def start_conversation(self, assessment_type='academic_speaking', part=1):
        """
        Auto-start conversation when assessment page loads with Maya's introduction
        
        Args:
            assessment_type (str): Type of assessment
            part (int): Part number (1-3)
            
        Returns:
            dict: Conversation initialization with text and audio
        """
        try:
            # Build examiner prompt based on IELTS requirements
            examiner_prompt = self._build_examiner_prompt(assessment_type, part)
            
            logger.info(f"Auto-starting Nova Sonic conversation for {assessment_type} part {part}")
            
            # Nova Sonic initiates first with welcome message (following AWS documentation)
            request_body = {
                "messages": [
                    {
                        "role": "system",
                        "content": [{"text": examiner_prompt}]
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
            
            # Create conversation ID and initialize state
            conversation_id = f"nova_conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Initialize conversation state for intelligent flow management
            self.conversation_state[conversation_id] = {
                'part': part,
                'assessment_type': assessment_type,
                'start_time': datetime.now(),
                'questions_asked': 0,
                'current_topic': None,
                'next_question_ready': True
            }
            
            # Initialize performance tracking
            self.performance_tracker[conversation_id] = {
                'responses': [],
                'current_scores': {'fluency': 0, 'lexical': 0, 'grammar': 0, 'pronunciation': 0},
                'assessment_notes': []
            }
            
            return {
                "success": True,
                "conversation_id": conversation_id,
                "opening_message": examiner_text,
                "audio_data": audio_data,
                "audio_url": f"data:audio/mp3;base64,{audio_data}" if audio_data else None,
                "session_active": True,
                "part_number": part,
                "assessment_type": assessment_type,
                "conversation_guidance": "Nova Sonic will automatically ask the next question when you finish speaking"
            }
            
        except ClientError as e:
            logger.error(f"Nova Sonic API error: {e}")
            return {"success": False, "error": f"Nova Sonic API error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error in start_conversation: {e}")
            return {"success": False, "error": f"Conversation start failed: {str(e)}"}
    
    def continue_conversation(self, conversation_id, user_audio_data, conversation_history):
        """
        Continue conversation with Nova Sonic using speech-to-speech pattern
        
        Args:
            conversation_id (str): Active conversation ID
            user_audio_data (str): Base64 encoded user audio
            conversation_history (list): Previous conversation turns
            
        Returns:
            dict: Maya's response with text and audio
        """
        try:
            # Build conversation context following AWS Nova Sonic documentation
            messages = self._build_conversation_context(conversation_history)
            
            # Add user audio input using correct Nova Sonic format
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
            
            # Perform real-time IELTS assessment on user response
            assessment_data = None
            if user_transcription:
                conv_state = self.conversation_state.get(conversation_id, {})
                assessment_data = IELTSRubricScorer.analyze_response(
                    user_transcription, 
                    {
                        'topic': conv_state.get('current_topic', 'general'),
                        'part': conv_state.get('part', 1),
                        'assessment_type': conv_state.get('assessment_type', 'academic')
                    }
                )
                
                # Update performance tracking
                if conversation_id not in self.performance_tracker:
                    self.performance_tracker[conversation_id] = {
                        'responses': [],
                        'current_scores': {'fluency': 0, 'lexical': 0, 'grammar': 0, 'pronunciation': 0},
                        'assessment_notes': []
                    }
                
                perf_tracker = self.performance_tracker[conversation_id]
                perf_tracker['responses'].append({
                    'timestamp': datetime.now().isoformat(),
                    'user_text': user_transcription,
                    'assessment': assessment_data,
                    'question_number': conv_state.get('questions_asked', 0) + 1
                })
                
                # Update current scores
                perf_tracker['current_scores'] = {
                    'fluency': assessment_data.get('fluency_coherence', 0),
                    'lexical': assessment_data.get('lexical_resource', 0),
                    'grammar': assessment_data.get('grammar_accuracy', 0),
                    'pronunciation': assessment_data.get('pronunciation', 6)
                }
                
                # Add assessment notes
                perf_tracker['assessment_notes'].extend(
                    assessment_data.get('detailed_feedback', [])
                )
                
                # Update conversation state
                if conversation_id in self.conversation_state:
                    self.conversation_state[conversation_id]['questions_asked'] = \
                        self.conversation_state[conversation_id].get('questions_asked', 0) + 1
                    self.conversation_state[conversation_id]['last_interaction'] = datetime.now()
                    
                    # Check if Part 1 is complete (4-5 minutes or sufficient questions)
                    elapsed_time = (datetime.now() - self.conversation_state[conversation_id]['start_time']).seconds // 60
                    questions_asked = self.conversation_state[conversation_id]['questions_asked']
                    current_part = self.conversation_state[conversation_id]['part']
                    
                    if current_part == 1 and (elapsed_time >= 4 or questions_asked >= 6):
                        # Mark Part 1 as complete and suggest Part 2
                        self.conversation_state[conversation_id]['part_1_complete'] = True

            # Check if this is the end of Part 1 and add transition guidance
            part_completion_guidance = ""
            show_part2_button = False
            
            if conversation_id in self.conversation_state:
                conv_state = self.conversation_state[conversation_id]
                if conv_state.get('part_1_complete') and conv_state['part'] == 1:
                    part_completion_guidance = "Thank you for completing Part 1. When you're ready to move to Part 2, please click the 'Start Part 2' button at the bottom of the screen."
                    show_part2_button = True
                    # Add polite transition to examiner response
                    examiner_text += " " + part_completion_guidance

            return {
                "success": True,
                "conversation_id": conversation_id,
                "examiner_response": examiner_text,
                "user_transcription": user_transcription,
                "audio_data": audio_data,
                "audio_url": f"data:audio/mp3;base64,{audio_data}" if audio_data else None,
                "session_active": True,
                "assessment_feedback": assessment_data if user_transcription else None,
                "current_performance": self.performance_tracker.get(conversation_id, {}).get('current_scores', {}),
                "questions_completed": self.conversation_state.get(conversation_id, {}).get('questions_asked', 0),
                "conversation_guidance": "Nova Sonic automatically listens for your response and asks the next question",
                "part_complete": self.conversation_state.get(conversation_id, {}).get('part_1_complete', False),
                "show_part2_button": show_part2_button,
                "transition_message": part_completion_guidance if show_part2_button else None
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
        
        # Enhanced system prompt with authentic IELTS structure and Nova Sonic trigger pattern
        base_prompt = f"""You are Maya, a certified IELTS Speaking examiner. Start the conversation immediately with a warm welcome and your first question.
        
        IMPORTANT GUIDELINES:
        - Begin speaking immediately when triggered
        - Follow authentic IELTS test procedures and timing
        - Ask questions naturally, one at a time
        - Listen to candidate responses and ask appropriate follow-up questions
        - Maintain professional but friendly demeanor
        - For Part 1: 4-5 minutes covering 2-3 familiar topics
        - For Part 2: Give cue card, 1 minute preparation, 1-2 minute speech
        - For Part 3: 4-5 minutes with abstract discussion questions
        
        Start now with: {script}"""
        
        # Enhance prompt with comprehensive knowledge base
        conversation_context = {
            'part': part,
            'assessment_type': assessment_type,
            'current_topic': None
        }
        
        enhanced_prompt = NovaSonicKnowledgeBase.enhance_nova_sonic_prompt(base_prompt, conversation_context)
        
        return enhanced_prompt
    
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
    
    def finalize_conversation_assessment(self, conversation_id):
        """
        Generate comprehensive final assessment using conversation performance data
        
        Args:
            conversation_id (str): The conversation to assess
            
        Returns:
            dict: Complete IELTS assessment with band scores and feedback
        """
        try:
            # Get performance data for this conversation
            perf_data = self.performance_tracker.get(conversation_id, {})
            conv_state = self.conversation_state.get(conversation_id, {})
            
            if not perf_data.get('responses'):
                return {
                    "success": False,
                    "error": "No conversation data available for assessment"
                }
            
            # Calculate overall performance metrics
            all_responses = perf_data['responses']
            total_responses = len(all_responses)
            
            # Average scores across all responses
            avg_fluency = sum(r['assessment'].get('fluency_coherence', 0) for r in all_responses) / total_responses
            avg_lexical = sum(r['assessment'].get('lexical_resource', 0) for r in all_responses) / total_responses
            avg_grammar = sum(r['assessment'].get('grammar_accuracy', 0) for r in all_responses) / total_responses
            avg_pronunciation = sum(r['assessment'].get('pronunciation', 6) for r in all_responses) / total_responses
            
            # Calculate overall band score
            overall_band = (avg_fluency + avg_lexical + avg_grammar + avg_pronunciation) / 4
            overall_band = round(overall_band * 2) / 2  # Round to nearest 0.5
            
            # Generate comprehensive feedback
            assessment_duration = (datetime.now() - conv_state.get('start_time', datetime.now())).seconds // 60
            
            # Collect all feedback notes
            all_feedback = []
            for response in all_responses:
                all_feedback.extend(response['assessment'].get('detailed_feedback', []))
            
            # Remove duplicates and create unique feedback
            unique_feedback = list(set(all_feedback))
            
            # Generate performance summary
            performance_summary = {
                'total_questions': conv_state.get('questions_asked', 0),
                'assessment_duration_minutes': assessment_duration,
                'part_completed': conv_state.get('part', 1),
                'assessment_type': conv_state.get('assessment_type', 'academic_speaking')
            }
            
            # Create detailed band descriptor feedback
            band_feedback = {
                'fluency_coherence': {
                    'score': round(avg_fluency),
                    'descriptor': IELTSRubricScorer.FLUENCY_COHERENCE.get(round(avg_fluency), "Assessment unavailable")
                },
                'lexical_resource': {
                    'score': round(avg_lexical),
                    'descriptor': IELTSRubricScorer.LEXICAL_RESOURCE.get(round(avg_lexical), "Assessment unavailable")
                },
                'grammar_accuracy': {
                    'score': round(avg_grammar),
                    'descriptor': IELTSRubricScorer.GRAMMAR_ACCURACY.get(round(avg_grammar), "Assessment unavailable")
                },
                'pronunciation': {
                    'score': round(avg_pronunciation),
                    'descriptor': IELTSRubricScorer.PRONUNCIATION.get(round(avg_pronunciation), "Assessment unavailable")
                }
            }
            
            logger.info(f"Final assessment completed for conversation {conversation_id}")
            
            return {
                "success": True,
                "conversation_id": conversation_id,
                "overall_band_score": overall_band,
                "individual_scores": {
                    "fluency_coherence": round(avg_fluency),
                    "lexical_resource": round(avg_lexical), 
                    "grammar_accuracy": round(avg_grammar),
                    "pronunciation": round(avg_pronunciation)
                },
                "band_descriptors": band_feedback,
                "performance_summary": performance_summary,
                "improvement_recommendations": unique_feedback[:5],  # Top 5 recommendations
                "conversation_complete": True,
                "assessment_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Assessment finalization error: {e}")
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