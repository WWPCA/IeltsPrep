"""
Nova Sonic Enhanced Knowledge Base Integration
RAG system providing comprehensive IELTS expertise for authentic assessments.
"""

class NovaSonicKnowledgeBase:
    """
    Enhanced RAG system for Nova Sonic with comprehensive IELTS knowledge
    """
    
    IELTS_SPEAKING_EXPERTISE = {
        "examiner_training": {
            "authentic_responses": [
                "Thank you. Now, let's talk about your studies.",
                "That's interesting. Can you tell me more about that?",
                "I see. What about your future plans?",
                "Moving on to Part 2, I'm going to give you a topic...",
                "We've been talking about [topic]. I'd like to discuss this further."
            ],
            "transition_phrases": [
                "Now I'd like to move on to talk about...",
                "Let's consider this topic from a different angle...",
                "That brings us to a broader question about...",
                "I'd like to explore this topic in more depth..."
            ]
        },
        
        "assessment_criteria_knowledge": {
            "fluency_indicators": [
                "Natural pace without long pauses",
                "Appropriate use of linking words",
                "Self-correction that doesn't impede communication",
                "Willingness to speak at length"
            ],
            "lexical_assessment": [
                "Range of vocabulary for the topic",
                "Accuracy in word choice and usage",
                "Ability to paraphrase when needed",
                "Natural collocations and expressions"
            ],
            "grammar_evaluation": [
                "Range of grammatical structures",
                "Accuracy in basic and complex forms",
                "Appropriate tense usage",
                "Error frequency and impact on meaning"
            ],
            "pronunciation_factors": [
                "Individual sounds clarity",
                "Word and sentence stress patterns",
                "Intonation and rhythm",
                "Overall intelligibility"
            ]
        },
        
        "topic_specific_knowledge": {
            "education": {
                "vocabulary": ["curriculum", "pedagogy", "assessment", "methodology", "academic achievement"],
                "questions": [
                    "How has education changed in your country?",
                    "What role should technology play in education?",
                    "How important is higher education today?"
                ]
            },
            "technology": {
                "vocabulary": ["innovation", "automation", "digital transformation", "artificial intelligence"],
                "questions": [
                    "How has technology changed the way people work?",
                    "What are the benefits and drawbacks of modern technology?",
                    "How might technology develop in the future?"
                ]
            },
            "environment": {
                "vocabulary": ["sustainability", "conservation", "climate change", "renewable energy"],
                "questions": [
                    "What environmental problems does your country face?",
                    "How can individuals help protect the environment?",
                    "What role should governments play in environmental protection?"
                ]
            }
        }
    }
    
    PROFESSIONAL_EXAMINER_RESPONSES = {
        "acknowledgments": [
            "Thank you for that response.",
            "That's a very interesting perspective.",
            "I can see you've thought about this carefully.",
            "That's a good point about..."
        ],
        
        "clarification_requests": [
            "Could you elaborate on that point?",
            "What do you mean exactly when you say...?",
            "Can you give me a specific example?",
            "How would you explain that to someone unfamiliar with the topic?"
        ],
        
        "natural_transitions": [
            "Building on what you just said...",
            "That reminds me of another question...",
            "Speaking of [topic], I'm curious about...",
            "Let's explore that idea further..."
        ]
    }
    
    @classmethod
    def get_examiner_response_patterns(cls, conversation_context):
        """
        Retrieve appropriate examiner response patterns based on conversation context
        
        Args:
            conversation_context (dict): Current conversation state and history
            
        Returns:
            dict: Contextually appropriate response patterns
        """
        
        part = conversation_context.get('part', 1)
        topic = conversation_context.get('current_topic', 'general')
        
        response_guidance = {
            'acknowledgment_style': cls.PROFESSIONAL_EXAMINER_RESPONSES['acknowledgments'],
            'transition_options': cls.PROFESSIONAL_EXAMINER_RESPONSES['natural_transitions'],
            'topic_vocabulary': cls._get_topic_vocabulary(topic),
            'assessment_focus': cls._get_assessment_focus(part)
        }
        
        return response_guidance
    
    @classmethod
    def _get_topic_vocabulary(cls, topic):
        """Get relevant vocabulary for specific topics"""
        topic_data = cls.IELTS_SPEAKING_EXPERTISE['topic_specific_knowledge']
        return topic_data.get(topic, {}).get('vocabulary', [])
    
    @classmethod
    def _get_assessment_focus(cls, part):
        """Get assessment focus areas for specific test parts"""
        if part == 1:
            return {
                'focus': 'Personal information and familiar topics',
                'expected_length': '4-5 minutes',
                'question_style': 'Direct, personal questions'
            }
        elif part == 2:
            return {
                'focus': 'Individual long turn with preparation',
                'expected_length': '3-4 minutes (1 min prep + 2 min speech)',
                'question_style': 'Cue card with structured points'
            }
        else:
            return {
                'focus': 'Abstract discussion and analysis',
                'expected_length': '4-5 minutes',
                'question_style': 'Analytical and hypothetical questions'
            }
    
    @classmethod
    def enhance_nova_sonic_prompt(cls, base_prompt, conversation_context):
        """
        Enhance Nova Sonic prompt with RAG-retrieved knowledge
        
        Args:
            base_prompt (str): Basic examiner prompt
            conversation_context (dict): Current conversation state
            
        Returns:
            str: Enhanced prompt with RAG knowledge integration
        """
        
        response_patterns = cls.get_examiner_response_patterns(conversation_context)
        assessment_focus = response_patterns['assessment_focus']
        
        enhanced_prompt = f"""{base_prompt}
        
        EXAMINER EXPERTISE INTEGRATION:
        
        Current Assessment Focus: {assessment_focus['focus']}
        Expected Duration: {assessment_focus['expected_length']}
        Question Style: {assessment_focus['question_style']}
        
        Professional Response Patterns:
        - Use natural acknowledgments like "Thank you for that response" or "That's interesting"
        - Transition smoothly with phrases like "Building on what you said..." or "Let's explore that further"
        - Ask follow-up questions that demonstrate active listening
        - Maintain authentic IELTS examiner tone throughout
        
        Assessment Awareness:
        - Monitor candidate's fluency and coherence
        - Note vocabulary range and accuracy
        - Assess grammatical variety and correctness
        - Evaluate pronunciation clarity
        
        Remember: You are conducting an official IELTS Speaking test. Be professional, encouraging, and authentic.
        """
        
        return enhanced_prompt
    
    @classmethod
    def get_contextual_follow_up_questions(cls, user_response, topic, part):
        """
        Generate contextually appropriate follow-up questions based on user response
        
        Args:
            user_response (str): What the user just said
            topic (str): Current topic being discussed
            part (int): Current test part
            
        Returns:
            list: Contextually relevant follow-up questions
        """
        
        follow_ups = []
        
        # Analyze user response for follow-up opportunities
        if 'important' in user_response.lower():
            follow_ups.append("Why do you think this is particularly important?")
        
        if 'different' in user_response.lower():
            follow_ups.append("In what ways is it different?")
            
        if 'future' in user_response.lower():
            follow_ups.append("How do you see this changing in the future?")
        
        # Add topic-specific follow-ups
        topic_questions = cls.IELTS_SPEAKING_EXPERTISE['topic_specific_knowledge'].get(topic, {}).get('questions', [])
        if topic_questions:
            follow_ups.extend(topic_questions[:2])
        
        return follow_ups[:3]  # Return maximum 3 follow-up options