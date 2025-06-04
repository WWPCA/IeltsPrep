"""
Nova Fallback Service for IELTS Assessment
Uses working Nova models when Nova Sonic is not accessible
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

class NovaFallbackService:
    """
    Fallback service using available Nova models for IELTS assessment
    """
    
    def __init__(self):
        """Initialize Nova fallback service with working models"""
        try:
            self.client = boto3.client('bedrock-runtime', region_name='us-east-1')
            self.conversation_state = {}
            self.performance_tracker = {}
            self.current_questions = []
            self.question_index = 0
            
            # Use working Nova model for text generation
            self.working_model = 'amazon.nova-lite-v1:0'
            logger.info(f"Nova fallback service initialized with {self.working_model}")
        except Exception as e:
            logger.error(f"Failed to initialize Nova fallback service: {e}")
            raise
    
    def start_conversation(self, assessment_type='academic_speaking', part=1):
        """
        Start conversation using working Nova model
        """
        try:
            # Build examiner prompt
            examiner_prompt = self._build_examiner_prompt(assessment_type, part)
            
            logger.info(f"Starting Nova conversation for {assessment_type} part {part}")
            
            # Request using working Nova model
            request_body = {
                "messages": [
                    {
                        "role": "system",
                        "content": [{"text": examiner_prompt}]
                    },
                    {
                        "role": "user", 
                        "content": [{"text": "The assessment page has loaded and I'm ready to begin."}]
                    }
                ],
                "inferenceConfig": {
                    "maxTokens": 200,
                    "temperature": 0.7,
                    "topP": 0.9
                }
            }
            
            response = self.client.invoke_model(
                modelId=self.working_model,
                contentType='application/json',
                accept='application/json',
                body=json.dumps(request_body)
            )
            
            result = json.loads(response['body'].read())
            
            # Extract examiner text from response
            examiner_text = self._extract_text_response(result)
            
            if not examiner_text:
                examiner_text = "Good morning! I'm Maya, your IELTS examiner. Let's begin your speaking assessment."
            
            # Initialize conversation state
            conversation_id = f"nova_conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            self.conversation_state[conversation_id] = {
                'part': part,
                'assessment_type': assessment_type,
                'start_time': datetime.now(),
                'questions_asked': 0,
                'current_topic': None,
                'next_question_ready': True
            }
            
            self.performance_tracker[conversation_id] = {
                'responses': [],
                'current_scores': {'fluency': 0, 'lexical': 0, 'grammar': 0, 'pronunciation': 0},
                'assessment_notes': []
            }
            
            return {
                "success": True,
                "conversation_id": conversation_id,
                "opening_message": examiner_text,
                "audio_data": None,  # No audio generation available
                "audio_url": None,
                "session_active": True,
                "part_number": part,
                "assessment_type": assessment_type,
                "conversation_guidance": "Please type your responses or speak aloud - Maya will continue with the next question",
                "fallback_mode": True,
                "working_model": self.working_model
            }
            
        except ClientError as e:
            logger.error(f"Nova conversation error: {e}")
            return {"success": False, "error": f"Conversation error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error in start_conversation: {e}")
            return {"success": False, "error": f"Conversation start failed: {str(e)}"}
    
    def continue_conversation(self, conversation_id, user_text_input, conversation_history):
        """
        Continue conversation using text input instead of audio
        """
        try:
            # Get conversation state
            conv_state = self.conversation_state.get(conversation_id, {})
            perf_tracker = self.performance_tracker.get(conversation_id, {})
            
            # Perform IELTS assessment on user text
            assessment_data = None
            if user_text_input:
                assessment_data = IELTSRubricScorer.analyze_response(
                    user_text_input, 
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
                    'user_text': user_text_input,
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
                
                # Update conversation state
                if conversation_id in self.conversation_state:
                    self.conversation_state[conversation_id]['questions_asked'] = \
                        self.conversation_state[conversation_id].get('questions_asked', 0) + 1
                    self.conversation_state[conversation_id]['last_interaction'] = datetime.now()
            
            # Generate Maya's next response
            context = self._build_conversation_context(conversation_history)
            
            examiner_response = self._generate_next_question(conv_state, user_text_input)
            
            # Check for part completion
            elapsed_time = (datetime.now() - conv_state.get('start_time', datetime.now())).seconds // 60
            questions_asked = conv_state.get('questions_asked', 0)
            current_part = conv_state.get('part', 1)
            
            part_completion_guidance = ""
            show_part2_button = False
            
            if current_part == 1 and (elapsed_time >= 4 or questions_asked >= 6):
                self.conversation_state[conversation_id]['part_1_complete'] = True
                part_completion_guidance = "Thank you for completing Part 1. When you're ready to move to Part 2, please click the 'Start Part 2' button at the bottom of the screen."
                show_part2_button = True
                examiner_response += " " + part_completion_guidance
            
            return {
                "success": True,
                "conversation_id": conversation_id,
                "examiner_response": examiner_response,
                "user_transcription": user_text_input,
                "audio_data": None,
                "audio_url": None,
                "session_active": True,
                "assessment_feedback": assessment_data if user_text_input else None,
                "current_performance": self.performance_tracker.get(conversation_id, {}).get('current_scores', {}),
                "questions_completed": self.conversation_state.get(conversation_id, {}).get('questions_asked', 0),
                "conversation_guidance": "Please type your response - Maya will ask the next question",
                "part_complete": self.conversation_state.get(conversation_id, {}).get('part_1_complete', False),
                "show_part2_button": show_part2_button,
                "transition_message": part_completion_guidance if show_part2_button else None,
                "fallback_mode": True
            }
            
        except Exception as e:
            logger.error(f"Conversation continuation error: {e}")
            return {"success": False, "error": str(e)}
    
    def _build_examiner_prompt(self, assessment_type, part):
        """Build examiner prompt with authentic IELTS questions"""
        script, additional_data = IELTSQuestionDatabase.build_examiner_script(assessment_type, part)
        
        self.current_questions = additional_data if isinstance(additional_data, list) else []
        self.current_part = part
        self.assessment_type = assessment_type
        
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
        
        conversation_context = {
            'part': part,
            'assessment_type': assessment_type,
            'current_topic': None
        }
        
        enhanced_prompt = NovaSonicKnowledgeBase.enhance_nova_sonic_prompt(base_prompt, conversation_context)
        return enhanced_prompt
    
    def _extract_text_response(self, result):
        """Extract text from Nova model response"""
        try:
            if 'output' in result and 'message' in result['output']:
                content = result['output']['message'].get('content', [])
                if content and isinstance(content, list):
                    return content[0].get('text', '')
            return ""
        except Exception as e:
            logger.error(f"Error extracting text response: {e}")
            return ""
    
    def _build_conversation_context(self, conversation_history):
        """Build conversation context from history"""
        context = "Previous conversation:\n"
        for turn in conversation_history[-3:]:
            speaker = turn.get('speaker', 'Unknown')
            message = turn.get('message', '')
            context += f"{speaker}: {message}\n"
        return context
    
    def _generate_next_question(self, conv_state, user_response):
        """Generate appropriate next question based on conversation state"""
        part = conv_state.get('part', 1)
        questions_asked = conv_state.get('questions_asked', 0)
        
        if part == 1:
            if questions_asked < len(self.current_questions):
                return self.current_questions[questions_asked]
            else:
                return "Thank you. Could you tell me more about your future plans?"
        elif part == 2:
            return "Now please begin your presentation. You have 1-2 minutes to speak."
        else:
            return "That's interesting. How do you think this will change in the future?"
    
    def finalize_conversation_assessment(self, conversation_id):
        """Generate final assessment using tracked performance data"""
        try:
            perf_data = self.performance_tracker.get(conversation_id, {})
            conv_state = self.conversation_state.get(conversation_id, {})
            
            if not perf_data.get('responses'):
                return {
                    "success": False,
                    "error": "No conversation data available for assessment"
                }
            
            all_responses = perf_data['responses']
            total_responses = len(all_responses)
            
            # Calculate average scores
            avg_fluency = sum(r['assessment'].get('fluency_coherence', 0) for r in all_responses) / total_responses
            avg_lexical = sum(r['assessment'].get('lexical_resource', 0) for r in all_responses) / total_responses
            avg_grammar = sum(r['assessment'].get('grammar_accuracy', 0) for r in all_responses) / total_responses
            avg_pronunciation = sum(r['assessment'].get('pronunciation', 6) for r in all_responses) / total_responses
            
            overall_band = (avg_fluency + avg_lexical + avg_grammar + avg_pronunciation) / 4
            overall_band = round(overall_band * 2) / 2
            
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
                "performance_summary": {
                    'total_questions': conv_state.get('questions_asked', 0),
                    'assessment_duration_minutes': (datetime.now() - conv_state.get('start_time', datetime.now())).seconds // 60,
                    'part_completed': conv_state.get('part', 1),
                    'assessment_type': conv_state.get('assessment_type', 'academic_speaking')
                },
                "conversation_complete": True,
                "assessment_timestamp": datetime.now().isoformat(),
                "fallback_mode": True,
                "model_used": self.working_model
            }
            
        except Exception as e:
            logger.error(f"Assessment finalization error: {e}")
            return {"success": False, "error": str(e)}