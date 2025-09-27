"""
Maya Conversation Engine
Natural speaking triggers and evaluation flow for authentic IELTS examiner experience
"""

import json
import logging
import random
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum

from nova_sonic_service import get_nova_sonic_service, NovaSonicService

logger = logging.getLogger(__name__)

class ConversationStage(Enum):
    """Maya conversation stages"""
    INITIAL_GREETING = "initial_greeting"
    IDENTITY_CONFIRMATION = "identity_confirmation" 
    PART1_INTRODUCTION = "part1_introduction"
    PART1_QUESTIONS = "part1_questions"
    PART2_BRIEFING = "part2_briefing"
    PART2_PREPARATION = "part2_preparation"
    PART2_SPEAKING = "part2_speaking"
    PART2_FOLLOWUP = "part2_followup"
    PART3_INTRODUCTION = "part3_introduction"
    PART3_DISCUSSION = "part3_discussion"
    CLOSING = "closing"

class ResponseType(Enum):
    """Maya response types for natural flow"""
    ENCOURAGEMENT = "encouragement"
    CLARIFICATION = "clarification"
    TRANSITION = "transition"
    PROMPT = "prompt"
    FOLLOW_UP = "follow_up"
    TIME_CHECK = "time_check"

class MayaConversationEngine:
    """
    Maya AI Examiner Conversation Engine
    Provides natural, human-like conversation flow and evaluation triggers
    """
    
    def __init__(self):
        # Initialize Nova Sonic service for voice synthesis
        self.nova_sonic = get_nova_sonic_service()
        
        # Natural conversational responses
        self.natural_responses = {
            ConversationStage.INITIAL_GREETING: [
                "Good morning! I'm Maya, and I'll be conducting your IELTS speaking assessment today. How are you feeling?",
                "Hello there! I'm Maya, your IELTS examiner. Thank you for joining me today. Are you ready to begin?",
                "Good day! My name is Maya and I'll be your speaking examiner today. I hope you're doing well.",
            ],
            
            ConversationStage.IDENTITY_CONFIRMATION: [
                "Before we start, could you please tell me your full name?",
                "May I have your full name please, for our records?",
                "Could you confirm your name for me please?",
            ],
            
            ConversationStage.PART1_INTRODUCTION: [
                "Thank you. Now, I'd like to ask you some questions about yourself and your background. Let's begin.",
                "Excellent. In this first part, I'll ask you about familiar topics. Please give full answers, not just yes or no.",
                "Great! For the first part of our conversation, I'll ask you about yourself. Please speak naturally and give detailed responses.",
            ],
            
            ConversationStage.PART2_BRIEFING: [
                "Now we're moving to Part 2. I'm going to give you a topic card with some points to cover. You'll have one minute to prepare, and then I'd like you to talk for up to two minutes.",
                "In this next part, you'll receive a topic card. You have a minute to think about your response, then please speak for one to two minutes.",
                "For Part 2, here's your topic card. Take a moment to read it carefully - you have one minute to prepare your thoughts.",
            ],
            
            ConversationStage.PART3_INTRODUCTION: [
                "Thank you. Now for our final part, we'll discuss some more abstract ideas related to the topic you just spoke about.",
                "Excellent. In Part 3, I'd like to explore some broader themes connected to what you've just told me.",
                "Perfect. Let's now have a discussion about some wider issues related to your topic.",
            ],
            
            ConversationStage.CLOSING: [
                "That concludes our speaking assessment. Thank you very much for your participation today.",
                "Wonderful! That brings us to the end of your speaking test. Thank you for your time.",
                "Excellent work today. That's the end of your IELTS speaking assessment. Thank you!",
            ]
        }
        
        # Encouragement phrases for natural flow
        self.encouragement_phrases = [
            "That's interesting.",
            "I see.",
            "Thank you.",
            "Good.",
            "Right.",
            "Okay.",
            "Mm-hmm.",
            "That's a good point.",
            "I understand.",
            "Thank you for sharing that."
        ]
        
        # Natural transition phrases
        self.transition_phrases = [
            "Let's move on to...",
            "I'd like to ask you about...",
            "Tell me about...",
            "How about we talk about...",
            "Can you tell me...",
            "What can you say about...",
            "Let's discuss...",
            "I'm curious about..."
        ]
        
        # Time-sensitive prompts
        self.time_prompts = {
            "preparation_30sec": "You have about 30 seconds remaining to prepare.",
            "preparation_10sec": "Just a few more seconds to organize your thoughts.",
            "speaking_1min": "You're doing well - keep going.",
            "speaking_90sec": "Please continue if you have more to add.",
            "speaking_end": "Thank you, that's enough for this part."
        }
        
        # Conversation state tracking
        self.conversation_state = {
            "stage": ConversationStage.INITIAL_GREETING,
            "part1_questions_asked": 0,
            "part2_prep_time": 0,
            "part2_speaking_time": 0,
            "part3_questions_asked": 0,
            "total_time": 0,
            "user_responses": [],
            "evaluation_notes": []
        }
    
    def initialize_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize Maya conversation session"""
        try:
            session_id = session_data.get('session_id')
            assessment_type = session_data.get('assessment_type')
            questions = session_data.get('questions', {})
            
            # Reset conversation state
            self.conversation_state = {
                "session_id": session_id,
                "assessment_type": assessment_type,
                "stage": ConversationStage.INITIAL_GREETING,
                "questions": questions,
                "part1_questions_asked": 0,
                "part2_prep_time": 0,
                "part2_speaking_time": 0,
                "part3_questions_asked": 0,
                "total_time": 0,
                "started_at": datetime.utcnow().isoformat(),
                "user_responses": [],
                "evaluation_notes": []
            }
            
            # Generate initial greeting
            initial_message = self.get_stage_response(ConversationStage.INITIAL_GREETING)
            
            return {
                "success": True,
                "maya_message": initial_message,
                "stage": ConversationStage.INITIAL_GREETING.value,
                "expected_response": "user_greeting",
                "instructions": "Respond naturally to Maya's greeting. Tell her how you're feeling today."
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize Maya session: {e}")
            return {
                "success": False,
                "error": "Failed to initialize conversation"
            }
    
    def process_user_response(self, user_input: str, audio_duration: float = 0) -> Dict[str, Any]:
        """
        Process user response and generate Maya's next natural response
        
        Args:
            user_input: User's spoken text (transcribed)
            audio_duration: Duration of user's audio in seconds
            
        Returns:
            Dict with Maya's response and conversation state
        """
        try:
            current_stage = self.conversation_state["stage"]
            
            # Record user response
            response_record = {
                "timestamp": datetime.utcnow().isoformat(),
                "stage": current_stage.value,
                "text": user_input,
                "duration": audio_duration,
                "word_count": len(user_input.split()) if user_input else 0
            }
            self.conversation_state["user_responses"].append(response_record)
            
            # Generate evaluation notes
            evaluation_notes = self.evaluate_response(user_input, audio_duration, current_stage)
            self.conversation_state["evaluation_notes"].extend(evaluation_notes)
            
            # Determine next stage and response
            next_response = self.determine_next_response(user_input, current_stage)
            
            return next_response
            
        except Exception as e:
            logger.error(f"Failed to process user response: {e}")
            return {
                "success": False,
                "error": "Failed to process response"
            }
    
    def get_stage_response(self, stage: ConversationStage) -> str:
        """Get natural response for conversation stage"""
        responses = self.natural_responses.get(stage, ["Let's continue."])
        return random.choice(responses)
    
    def determine_next_response(self, user_input: str, current_stage: ConversationStage) -> Dict[str, Any]:
        """Determine Maya's next natural response based on conversation flow"""
        
        # Stage progression logic
        if current_stage == ConversationStage.INITIAL_GREETING:
            return self.handle_identity_confirmation()
            
        elif current_stage == ConversationStage.IDENTITY_CONFIRMATION:
            return self.handle_part1_start()
            
        elif current_stage == ConversationStage.PART1_INTRODUCTION:
            return self.handle_part1_questions()
            
        elif current_stage == ConversationStage.PART1_QUESTIONS:
            return self.handle_part1_progression(user_input)
            
        elif current_stage == ConversationStage.PART2_BRIEFING:
            return self.handle_part2_preparation()
            
        elif current_stage == ConversationStage.PART2_PREPARATION:
            return self.handle_part2_speaking()
            
        elif current_stage == ConversationStage.PART2_SPEAKING:
            return self.handle_part2_completion(user_input)
            
        elif current_stage == ConversationStage.PART2_FOLLOWUP:
            return self.handle_part3_start()
            
        elif current_stage == ConversationStage.PART3_INTRODUCTION:
            return self.handle_part3_questions()
            
        elif current_stage == ConversationStage.PART3_DISCUSSION:
            return self.handle_part3_progression(user_input)
            
        else:
            return self.handle_closing()
    
    def handle_identity_confirmation(self) -> Dict[str, Any]:
        """Handle identity confirmation stage"""
        self.conversation_state["stage"] = ConversationStage.IDENTITY_CONFIRMATION
        
        message = self.get_stage_response(ConversationStage.IDENTITY_CONFIRMATION)
        
        return {
            "success": True,
            "maya_message": message,
            "stage": ConversationStage.IDENTITY_CONFIRMATION.value,
            "expected_response": "full_name",
            "instructions": "Please state your full name clearly."
        }
    
    def handle_part1_start(self) -> Dict[str, Any]:
        """Handle Part 1 introduction"""
        self.conversation_state["stage"] = ConversationStage.PART1_INTRODUCTION
        
        message = self.get_stage_response(ConversationStage.PART1_INTRODUCTION)
        
        return {
            "success": True,
            "maya_message": message,
            "stage": ConversationStage.PART1_INTRODUCTION.value,
            "expected_response": "acknowledgment",
            "instructions": "Listen to Maya's instructions for Part 1."
        }
    
    def handle_part1_questions(self) -> Dict[str, Any]:
        """Handle Part 1 questions"""
        self.conversation_state["stage"] = ConversationStage.PART1_QUESTIONS
        
        # Get first Part 1 question
        part1_questions = self.conversation_state["questions"].get("speaking_part1", [])
        
        if not part1_questions:
            # Fallback question
            question_text = "Tell me about yourself and your background."
        else:
            question_text = part1_questions[0].get("content", {}).get("text", "Tell me about yourself.")
        
        self.conversation_state["part1_questions_asked"] = 1
        
        return {
            "success": True,
            "maya_message": question_text,
            "stage": ConversationStage.PART1_QUESTIONS.value,
            "expected_response": "detailed_answer",
            "instructions": "Give a detailed answer (2-3 sentences). Avoid yes/no responses."
        }
    
    def handle_part1_progression(self, user_input: str) -> Dict[str, Any]:
        """Handle progression through Part 1 questions"""
        questions_asked = self.conversation_state["part1_questions_asked"]
        part1_questions = self.conversation_state["questions"].get("speaking_part1", [])
        
        # Natural encouragement
        encouragement = random.choice(self.encouragement_phrases)
        
        # Check if we should ask more questions (typically 4-6 in Part 1)
        if questions_asked < min(6, len(part1_questions)):
            # Ask next question
            next_question = part1_questions[questions_asked]
            question_text = next_question.get("content", {}).get("text", "Tell me more about that.")
            
            self.conversation_state["part1_questions_asked"] += 1
            
            # Natural transition
            transition = random.choice(self.transition_phrases)
            full_message = f"{encouragement} {transition} {question_text}"
            
            return {
                "success": True,
                "maya_message": full_message,
                "stage": ConversationStage.PART1_QUESTIONS.value,
                "expected_response": "detailed_answer",
                "instructions": "Continue with detailed answers about your experiences and opinions."
            }
        else:
            # Move to Part 2
            return self.handle_part2_briefing()
    
    def handle_part2_briefing(self) -> Dict[str, Any]:
        """Handle Part 2 briefing and topic card presentation"""
        self.conversation_state["stage"] = ConversationStage.PART2_BRIEFING
        
        # Get Part 2 topic
        part2_questions = self.conversation_state["questions"].get("speaking_part2", [])
        if part2_questions:
            topic_card = part2_questions[0].get("content", {}).get("text", "Describe something important to you.")
        else:
            topic_card = "Describe a place that is special to you. You should say: where it is, when you go there, what you do there, and explain why this place is special to you."
        
        briefing_message = self.get_stage_response(ConversationStage.PART2_BRIEFING)
        full_message = f"{briefing_message}\n\nHere's your topic card:\n\n{topic_card}\n\nRemember, you have one minute to prepare. Your preparation time starts now."
        
        return {
            "success": True,
            "maya_message": full_message,
            "stage": ConversationStage.PART2_BRIEFING.value,
            "expected_response": "preparation",
            "instructions": "Use this minute to organize your thoughts. Make notes if needed.",
            "preparation_time": 60,  # 60 seconds preparation
            "topic_card": topic_card
        }
    
    def handle_part2_preparation(self) -> Dict[str, Any]:
        """Handle Part 2 preparation time"""
        self.conversation_state["stage"] = ConversationStage.PART2_PREPARATION
        
        return {
            "success": True,
            "maya_message": "Your preparation time is up. Please begin speaking about your topic. Remember, you should speak for 1-2 minutes.",
            "stage": ConversationStage.PART2_PREPARATION.value,
            "expected_response": "long_turn_speech",
            "instructions": "Speak for 1-2 minutes about your topic. Cover all the points on the card.",
            "speaking_time": 120  # 2 minutes maximum
        }
    
    def handle_part2_speaking(self) -> Dict[str, Any]:
        """Handle Part 2 speaking phase"""
        self.conversation_state["stage"] = ConversationStage.PART2_SPEAKING
        
        # Generate follow-up questions
        follow_up_questions = [
            "Thank you. Can you tell me a bit more about why this is important to you?",
            "That's interesting. How do you think this has influenced you?",
            "Thank you for that detailed description."
        ]
        
        follow_up = random.choice(follow_up_questions)
        
        return {
            "success": True,
            "maya_message": follow_up,
            "stage": ConversationStage.PART2_FOLLOWUP.value,
            "expected_response": "brief_elaboration",
            "instructions": "Give a brief response to Maya's follow-up question."
        }
    
    def handle_part2_completion(self, user_input: str) -> Dict[str, Any]:
        """Handle Part 2 completion"""
        self.conversation_state["stage"] = ConversationStage.PART2_FOLLOWUP
        
        return {
            "success": True,
            "maya_message": random.choice(self.encouragement_phrases),
            "stage": ConversationStage.PART2_FOLLOWUP.value,
            "transition_to_part3": True
        }
    
    def handle_part3_start(self) -> Dict[str, Any]:
        """Handle Part 3 introduction"""
        self.conversation_state["stage"] = ConversationStage.PART3_INTRODUCTION
        
        message = self.get_stage_response(ConversationStage.PART3_INTRODUCTION)
        
        return {
            "success": True,
            "maya_message": message,
            "stage": ConversationStage.PART3_INTRODUCTION.value,
            "expected_response": "acknowledgment",
            "instructions": "Part 3 involves more abstract discussion. Give thoughtful, extended answers."
        }
    
    def handle_part3_questions(self) -> Dict[str, Any]:
        """Handle Part 3 questions"""
        self.conversation_state["stage"] = ConversationStage.PART3_DISCUSSION
        
        # Get first Part 3 question
        part3_questions = self.conversation_state["questions"].get("speaking_part3", [])
        
        if part3_questions:
            question_text = part3_questions[0].get("content", {}).get("text", "What are your thoughts on this topic in general?")
        else:
            question_text = "What do you think about the role this plays in modern society?"
        
        self.conversation_state["part3_questions_asked"] = 1
        
        return {
            "success": True,
            "maya_message": question_text,
            "stage": ConversationStage.PART3_DISCUSSION.value,
            "expected_response": "analytical_response",
            "instructions": "Give detailed, analytical responses. Consider different perspectives."
        }
    
    def handle_part3_progression(self, user_input: str) -> Dict[str, Any]:
        """Handle progression through Part 3 discussion"""
        questions_asked = self.conversation_state["part3_questions_asked"]
        part3_questions = self.conversation_state["questions"].get("speaking_part3", [])
        
        # Natural encouragement
        encouragement = random.choice(self.encouragement_phrases)
        
        # Check if we should ask more questions (typically 4-5 in Part 3)
        if questions_asked < min(4, len(part3_questions)):
            # Ask next question
            next_question = part3_questions[questions_asked]
            question_text = next_question.get("content", {}).get("text", "What's your opinion on this?")
            
            self.conversation_state["part3_questions_asked"] += 1
            
            # Natural transition for abstract discussion
            transitions = [
                "That's a good point. How about this:",
                "I see your perspective. Let me ask you:",
                "Interesting. What would you say about:",
                "That raises another question:"
            ]
            transition = random.choice(transitions)
            full_message = f"{encouragement} {transition} {question_text}"
            
            return {
                "success": True,
                "maya_message": full_message,
                "stage": ConversationStage.PART3_DISCUSSION.value,
                "expected_response": "analytical_response",
                "instructions": "Continue discussing these abstract concepts in detail."
            }
        else:
            # End the assessment
            return self.handle_closing()
    
    def handle_closing(self) -> Dict[str, Any]:
        """Handle assessment closing"""
        self.conversation_state["stage"] = ConversationStage.CLOSING
        
        message = self.get_stage_response(ConversationStage.CLOSING)
        
        return {
            "success": True,
            "maya_message": message,
            "stage": ConversationStage.CLOSING.value,
            "assessment_complete": True,
            "instructions": "Your speaking assessment is now complete. Thank you!"
        }
    
    def evaluate_response(self, user_input: str, audio_duration: float, stage: ConversationStage) -> List[Dict[str, Any]]:
        """
        Evaluate user response for IELTS criteria
        
        Returns evaluation notes for band scoring
        """
        evaluation_notes = []
        
        if not user_input or len(user_input.strip()) < 3:
            evaluation_notes.append({
                "criterion": "Fluency and Coherence",
                "note": "Very brief response - limited assessment possible",
                "stage": stage.value
            })
            return evaluation_notes
        
        word_count = len(user_input.split())
        
        # Fluency and Coherence evaluation
        if audio_duration > 0:
            words_per_minute = (word_count / audio_duration) * 60
            if words_per_minute < 100:
                evaluation_notes.append({
                    "criterion": "Fluency and Coherence",
                    "note": f"Slow speech rate ({words_per_minute:.0f} wpm) - may indicate hesitation",
                    "stage": stage.value
                })
            elif words_per_minute > 200:
                evaluation_notes.append({
                    "criterion": "Fluency and Coherence",
                    "note": f"Very rapid speech ({words_per_minute:.0f} wpm) - check for coherence",
                    "stage": stage.value
                })
        
        # Lexical Resource evaluation
        unique_words = set(user_input.lower().split())
        lexical_variety = len(unique_words) / word_count if word_count > 0 else 0
        
        if lexical_variety > 0.8:
            evaluation_notes.append({
                "criterion": "Lexical Resource",
                "note": "Good vocabulary variety demonstrated",
                "stage": stage.value
            })
        elif lexical_variety < 0.5:
            evaluation_notes.append({
                "criterion": "Lexical Resource",
                "note": "Limited vocabulary range - repetitive word use",
                "stage": stage.value
            })
        
        # Response length appropriateness
        expected_lengths = {
            ConversationStage.PART1_QUESTIONS: (10, 50),  # 10-50 words
            ConversationStage.PART2_SPEAKING: (150, 300), # 150-300 words for 2 minutes
            ConversationStage.PART3_DISCUSSION: (30, 100) # 30-100 words
        }
        
        if stage in expected_lengths:
            min_words, max_words = expected_lengths[stage]
            if word_count < min_words:
                evaluation_notes.append({
                    "criterion": "Task Response",
                    "note": f"Response too brief ({word_count} words) for {stage.value}",
                    "stage": stage.value
                })
            elif word_count > max_words * 1.5:  # 50% over is concerning
                evaluation_notes.append({
                    "criterion": "Task Response", 
                    "note": f"Very lengthy response ({word_count} words) - may lack focus",
                    "stage": stage.value
                })
        
        return evaluation_notes
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get complete conversation summary for evaluation"""
        return {
            "session_id": self.conversation_state.get("session_id"),
            "assessment_type": self.conversation_state.get("assessment_type"),
            "conversation_flow": {
                "total_responses": len(self.conversation_state["user_responses"]),
                "part1_responses": len([r for r in self.conversation_state["user_responses"] if "part1" in r["stage"]]),
                "part2_responses": len([r for r in self.conversation_state["user_responses"] if "part2" in r["stage"]]),
                "part3_responses": len([r for r in self.conversation_state["user_responses"] if "part3" in r["stage"]]),
            },
            "user_responses": self.conversation_state["user_responses"],
            "evaluation_notes": self.conversation_state["evaluation_notes"],
            "completion_status": self.conversation_state["stage"] == ConversationStage.CLOSING
        }

# Global instance
_maya_engine = None

def get_maya_engine() -> MayaConversationEngine:
    """Get global Maya conversation engine instance"""
    global _maya_engine
    if _maya_engine is None:
        _maya_engine = MayaConversationEngine()
    return _maya_engine

# Export
__all__ = [
    'MayaConversationEngine',
    'ConversationStage',
    'ResponseType', 
    'get_maya_engine'
]