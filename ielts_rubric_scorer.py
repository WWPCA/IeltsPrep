"""
IELTS Speaking Assessment Rubric and Scoring System
Official IELTS band descriptors for authentic assessment scoring.
"""

class IELTSRubricScorer:
    """Official IELTS Speaking band descriptors and scoring logic"""
    
    FLUENCY_COHERENCE = {
        9: "speaks fluently with only rare repetition or self-correction; any hesitation is content-related rather than to find words or grammar",
        8: "speaks fluently with only occasional repetition or self-correction; hesitation is usually content-related",
        7: "speaks at length without noticeable effort or loss of coherence; may demonstrate language-related hesitation at times",
        6: "is willing to speak at length, though may lose coherence at times due to occasional repetition, self-correction or hesitation",
        5: "usually maintains flow of speech but uses repetition, self-correction and/or slow speech to keep going",
        4: "cannot respond without noticeable pauses and may speak slowly, with frequent repetition and self-correction",
        3: "speaks with long pauses; has limited ability to link simple sentences",
        2: "lengthy pauses before most words; little communication possible",
        1: "no communication possible; no rateable language"
    }
    
    LEXICAL_RESOURCE = {
        9: "uses vocabulary with complete flexibility and precise usage in all contexts",
        8: "uses a wide range of vocabulary fluently and flexibly to convey precise meanings",
        7: "uses vocabulary resource flexibly to discuss a variety of topics; uses some less common and idiomatic vocabulary",
        6: "has a wide enough vocabulary to discuss topics at length and make meaning clear in spite of inappropriacies",
        5: "manages to talk about familiar and unfamiliar topics but uses vocabulary with limited flexibility",
        4: "is able to talk about familiar topics but can only convey basic meaning on unfamiliar topics",
        3: "uses simple vocabulary to convey personal information; has insufficient vocabulary for less familiar topics",
        2: "uses an extremely limited range of vocabulary; essentially no control of word formation",
        1: "no communication possible; no rateable language"
    }
    
    GRAMMAR_ACCURACY = {
        9: "uses a full range of structures naturally and appropriately; produces consistently accurate structures",
        8: "uses a wide range of structures flexibly; produces a majority of error-free sentences",
        7: "uses a range of complex structures with some flexibility; frequently produces error-free sentences",
        6: "uses a mix of simple and complex structures, but with limited flexibility; may make frequent mistakes",
        5: "produces basic sentence forms with reasonable accuracy; uses a limited range of more complex structures",
        4: "produces basic sentence forms and some correct simple sentences but subordinate structures are rare",
        3: "attempts basic sentence forms but with limited success, or relies on apparently memorised utterances",
        2: "cannot produce basic sentence forms except in memorised utterances",
        1: "no communication possible; no rateable language"
    }
    
    PRONUNCIATION = {
        9: "uses a full range of pronunciation features with precision and subtlety; sustains flexible use of features",
        8: "uses a wide range of pronunciation features; sustains flexible use of features with only occasional lapses",
        7: "shows all the positive features of Band 6 and some, but not all, of the positive features of Band 8",
        6: "uses a range of pronunciation features with mixed control; shows some effective use of features",
        5: "shows all the positive features of Band 4 and some, but not all, of the positive features of Band 6",
        4: "uses a limited range of pronunciation features; attempts to control features but lapses are noticeable",
        3: "shows some of the features of Band 2 and some, but not all, of the positive features of Band 4",
        2: "speech is often unintelligible",
        1: "no communication possible; no rateable language"
    }
    
    @classmethod
    def analyze_response(cls, user_response, assessment_criteria):
        """
        Analyze user response against IELTS criteria
        
        Args:
            user_response (str): User's spoken response
            assessment_criteria (dict): Specific criteria to assess
            
        Returns:
            dict: Detailed scoring breakdown
        """
        
        # Basic analysis indicators
        response_length = len(user_response.split())
        
        # Fluency analysis
        fluency_indicators = {
            'hesitation_markers': user_response.count('um') + user_response.count('uh') + user_response.count('er'),
            'repetition_count': cls._count_repetitions(user_response),
            'response_length': response_length,
            'self_corrections': user_response.count('I mean') + user_response.count('actually')
        }
        
        # Lexical analysis
        lexical_indicators = {
            'vocabulary_range': len(set(user_response.lower().split())),
            'academic_words': cls._count_academic_vocabulary(user_response),
            'topic_specific_vocab': cls._assess_topic_vocabulary(user_response, assessment_criteria.get('topic', '')),
            'word_repetition_ratio': cls._calculate_repetition_ratio(user_response)
        }
        
        # Grammar analysis
        grammar_indicators = {
            'sentence_complexity': cls._assess_sentence_complexity(user_response),
            'tense_usage': cls._assess_tense_variety(user_response),
            'error_density': cls._estimate_error_density(user_response)
        }
        
        return {
            'fluency_coherence': cls._score_fluency(fluency_indicators),
            'lexical_resource': cls._score_lexical(lexical_indicators),
            'grammar_accuracy': cls._score_grammar(grammar_indicators),
            'pronunciation': 6,  # Default - would need audio analysis
            'overall_performance': cls._calculate_overall_band(fluency_indicators, lexical_indicators, grammar_indicators),
            'detailed_feedback': cls._generate_feedback(fluency_indicators, lexical_indicators, grammar_indicators)
        }
    
    @classmethod
    def _count_repetitions(cls, text):
        """Count word repetitions as fluency indicator"""
        words = text.lower().split()
        repetitions = 0
        for i in range(len(words) - 1):
            if words[i] == words[i + 1]:
                repetitions += 1
        return repetitions
    
    @classmethod
    def _count_academic_vocabulary(cls, text):
        """Count academic/sophisticated vocabulary usage"""
        academic_words = ['furthermore', 'consequently', 'nevertheless', 'significant', 'substantial', 
                         'demonstrate', 'establish', 'contribute', 'analyze', 'concept', 'perspective']
        
        words = text.lower().split()
        return sum(1 for word in words if word in academic_words)
    
    @classmethod
    def _assess_topic_vocabulary(cls, text, topic):
        """Assess use of topic-specific vocabulary"""
        # Simplified topic vocabulary assessment
        return min(6, len(set(text.lower().split())) // 10)
    
    @classmethod
    def _calculate_repetition_ratio(cls, text):
        """Calculate vocabulary repetition ratio"""
        words = text.lower().split()
        unique_words = set(words)
        return len(unique_words) / len(words) if words else 0
    
    @classmethod
    def _assess_sentence_complexity(cls, text):
        """Assess grammatical complexity"""
        complex_markers = ['which', 'that', 'although', 'because', 'since', 'while', 'whereas']
        sentences = text.split('.')
        
        complex_count = 0
        for sentence in sentences:
            if any(marker in sentence.lower() for marker in complex_markers):
                complex_count += 1
        
        return complex_count / len(sentences) if sentences else 0
    
    @classmethod
    def _assess_tense_variety(cls, text):
        """Assess variety of tense usage"""
        past_markers = ['was', 'were', 'had', 'did', 'went']
        present_markers = ['is', 'are', 'do', 'does', 'have']
        future_markers = ['will', 'going to', 'shall']
        
        tense_types = 0
        if any(marker in text.lower() for marker in past_markers):
            tense_types += 1
        if any(marker in text.lower() for marker in present_markers):
            tense_types += 1
        if any(marker in text.lower() for marker in future_markers):
            tense_types += 1
            
        return tense_types
    
    @classmethod
    def _estimate_error_density(cls, text):
        """Estimate grammatical error density"""
        # Simplified error estimation based on common patterns
        potential_errors = 0
        
        # Check for basic subject-verb agreement issues
        if 'he are' in text.lower() or 'she are' in text.lower():
            potential_errors += 1
        if 'they is' in text.lower():
            potential_errors += 1
            
        return potential_errors / len(text.split()) if text.split() else 0
    
    @classmethod
    def _score_fluency(cls, indicators):
        """Score fluency and coherence based on indicators"""
        base_score = 6
        
        # Adjust for hesitation markers
        if indicators['hesitation_markers'] > 5:
            base_score -= 1
        elif indicators['hesitation_markers'] < 2:
            base_score += 0.5
            
        # Adjust for response length
        if indicators['response_length'] > 50:
            base_score += 0.5
        elif indicators['response_length'] < 20:
            base_score -= 1
            
        return min(9, max(1, int(base_score)))
    
    @classmethod
    def _score_lexical(cls, indicators):
        """Score lexical resource based on indicators"""
        base_score = 6
        
        # Adjust for vocabulary range
        if indicators['vocabulary_range'] > 30:
            base_score += 1
        elif indicators['vocabulary_range'] < 15:
            base_score -= 1
            
        # Adjust for academic vocabulary
        if indicators['academic_words'] > 2:
            base_score += 0.5
            
        return min(9, max(1, int(base_score)))
    
    @classmethod
    def _score_grammar(cls, indicators):
        """Score grammar and accuracy based on indicators"""
        base_score = 6
        
        # Adjust for complexity
        if indicators['sentence_complexity'] > 0.3:
            base_score += 1
        elif indicators['sentence_complexity'] < 0.1:
            base_score -= 1
            
        # Adjust for tense variety
        if indicators['tense_usage'] >= 3:
            base_score += 0.5
        elif indicators['tense_usage'] <= 1:
            base_score -= 0.5
            
        return min(9, max(1, int(base_score)))
    
    @classmethod
    def _calculate_overall_band(cls, fluency_ind, lexical_ind, grammar_ind):
        """Calculate overall band score"""
        fluency_score = cls._score_fluency(fluency_ind)
        lexical_score = cls._score_lexical(lexical_ind)
        grammar_score = cls._score_grammar(grammar_ind)
        pronunciation_score = 6  # Default
        
        overall = (fluency_score + lexical_score + grammar_score + pronunciation_score) / 4
        return round(overall * 2) / 2  # Round to nearest 0.5
    
    @classmethod
    def _generate_feedback(cls, fluency_ind, lexical_ind, grammar_ind):
        """Generate detailed feedback based on performance"""
        feedback = []
        
        # Fluency feedback
        if fluency_ind['hesitation_markers'] > 5:
            feedback.append("Try to reduce hesitation markers (um, uh) for better fluency")
        if fluency_ind['response_length'] < 30:
            feedback.append("Provide more detailed responses to fully address the question")
            
        # Lexical feedback
        if lexical_ind['vocabulary_range'] < 20:
            feedback.append("Use a wider range of vocabulary to express your ideas")
        if lexical_ind['academic_words'] == 0:
            feedback.append("Include more sophisticated vocabulary in your responses")
            
        # Grammar feedback
        if grammar_ind['sentence_complexity'] < 0.2:
            feedback.append("Use more complex sentence structures to demonstrate grammar range")
        if grammar_ind['tense_usage'] <= 1:
            feedback.append("Vary your tense usage to show grammatical flexibility")
            
        return feedback