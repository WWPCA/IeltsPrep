#!/usr/bin/env python3
"""
Seamless Content Moderation Service for IELTS Speaking Assessments
Provides real-time content moderation that maintains authentic conversation flow
"""

import re
import logging
from typing import Dict, Tuple, List, Optional
from enum import Enum

class ModerationSeverity(Enum):
    """Content moderation severity levels"""
    CLEAN = "clean"
    MILD = "mild"  # Minor issues, continue conversation
    MODERATE = "moderate"  # Gentle redirection needed
    SEVERE = "severe"  # Stop assessment immediately

class ContentModerationService:
    """
    Real-time content moderation service designed specifically for IELTS speaking assessments.
    Maintains conversation flow while ensuring appropriate content.
    """
    
    def __init__(self):
        self.profanity_patterns = self._load_profanity_patterns()
        self.inappropriate_patterns = self._load_inappropriate_patterns()
        self.redirection_responses = self._load_redirection_responses()
        
    def _load_profanity_patterns(self) -> List[str]:
        """Load comprehensive profanity detection patterns"""
        # Common profanity patterns (sanitized for educational assessment)
        return [
            r'\b(f\*{2,3}|f[\*@#]{1,3}k|sh\*t|d\*mn|h\*ll)\b',
            r'\b(stupid|idiot|moron|dumb\*ss)\b',
            r'\b(hate|kill|murder|die)\s+(you|them|everyone)\b',
            # Add more patterns as needed for comprehensive coverage
        ]
    
    def _load_inappropriate_patterns(self) -> List[str]:
        """Load patterns for inappropriate but not offensive content"""
        return [
            r'\b(drugs?|marijuana|cocaine|heroin|alcohol|drunk|wasted)\b',
            r'\b(sex|sexual|pornography|xxx|explicit)\b',
            r'\b(violence|fight|punch|kick|hurt)\s+(someone|people)\b',
            r'\b(cheating|cheat|copy|plagiarism)\b',
        ]
    
    def _load_redirection_responses(self) -> Dict[str, List[str]]:
        """Load IELTS-appropriate redirection responses for different topics"""
        return {
            'inappropriate_topic': [
                "That's an interesting point. Let's focus on a more suitable topic for our discussion. Can you tell me about your hobbies instead?",
                "I understand, but let's redirect our conversation to something more appropriate. What do you enjoy doing in your free time?",
                "Let's move to a different topic that might be more relevant for your assessment. Could you describe your hometown?",
            ],
            'mild_language': [
                "I see. Let's continue with our discussion. Can you elaborate on that using more formal language?",
                "That's understandable. How would you express that in a more academic way?",
                "Let's maintain a formal tone for this assessment. Can you rephrase that thought?",
            ],
            'off_topic': [
                "Thank you for sharing. Now, returning to our main topic, what are your thoughts on...",
                "That's interesting. Let's get back to discussing the question I asked earlier about...",
                "I appreciate your perspective. Let's refocus on the IELTS topic we were exploring...",
            ]
        }
    
    def moderate_content(self, text: str, context: str = "speaking") -> Tuple[ModerationSeverity, Optional[str], str]:
        """
        Moderate content while maintaining conversation flow
        
        Args:
            text: User's spoken content (transcribed)
            context: Assessment context ("speaking", "writing", etc.)
            
        Returns:
            Tuple of (severity, redirection_response, processed_text)
        """
        if not text or not text.strip():
            return ModerationSeverity.CLEAN, None, text
            
        # Normalize text for analysis
        normalized_text = text.lower().strip()
        
        # Check for severe violations (stop assessment)
        if self._has_severe_violations(normalized_text):
            return ModerationSeverity.SEVERE, self._get_termination_message(), text
            
        # Check for moderate violations (gentle redirection)
        if self._has_moderate_violations(normalized_text):
            redirection = self._select_redirection_response('inappropriate_topic')
            return ModerationSeverity.MODERATE, redirection, text
            
        # Check for mild violations (continue with guidance)
        if self._has_mild_violations(normalized_text):
            redirection = self._select_redirection_response('mild_language')
            return ModerationSeverity.MILD, redirection, text
            
        # Content is clean
        return ModerationSeverity.CLEAN, None, text
    
    def _has_severe_violations(self, text: str) -> bool:
        """Check for content that requires immediate assessment termination"""
        severe_patterns = [
            r'\b(threat|kill|murder|bomb|weapon|gun)\b',
            r'\b(extreme|graphic|violent)\s+(content|description)\b',
            r'\b(personal|private|confidential)\s+(information|data)\b',
            r'\b(racist|sexist|discriminatory)\b',
        ]
        
        for pattern in severe_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                logging.warning(f"Severe violation detected: {pattern}")
                return True
                
        # Check explicit profanity patterns
        for pattern in self.profanity_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                # Some profanity might be severe depending on context
                if len(re.findall(pattern, text, re.IGNORECASE)) > 2:  # Repeated use
                    logging.warning(f"Repeated profanity detected: {pattern}")
                    return True
                    
        return False
    
    def _has_moderate_violations(self, text: str) -> bool:
        """Check for inappropriate content that needs redirection"""
        for pattern in self.inappropriate_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                logging.info(f"Moderate violation detected: {pattern}")
                return True
        return False
    
    def _has_mild_violations(self, text: str) -> bool:
        """Check for mild language issues"""
        for pattern in self.profanity_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                logging.info(f"Mild language violation detected: {pattern}")
                return True
        return False
    
    def _select_redirection_response(self, category: str) -> str:
        """Select an appropriate redirection response"""
        import random
        responses = self.redirection_responses.get(category, [])
        return random.choice(responses) if responses else "Let's continue with our discussion."
    
    def _get_termination_message(self) -> str:
        """Get message for assessment termination"""
        return """I'm sorry, but I need to end this assessment due to inappropriate content. 
        For IELTS speaking assessments, we maintain professional standards. 
        You may restart the assessment when you're ready to proceed appropriately."""
    
    def generate_examiner_response(self, user_text: str, moderation_result: Tuple[ModerationSeverity, Optional[str], str]) -> str:
        """
        Generate Maya AI examiner response that incorporates content moderation seamlessly
        
        Args:
            user_text: Original user input
            moderation_result: Result from content moderation
            
        Returns:
            Appropriate examiner response that maintains conversation flow
        """
        severity, redirection, processed_text = moderation_result
        
        if severity == ModerationSeverity.SEVERE:
            return redirection or self._get_termination_message()
            
        elif severity == ModerationSeverity.MODERATE:
            # Gentle redirection while maintaining examiner role
            return redirection or "Thank you for sharing. Let's explore a different aspect of this topic. Can you tell me about your educational background?"
            
        elif severity == ModerationSeverity.MILD:
            # Subtle guidance toward more appropriate language
            return redirection or "I understand your point. Could you elaborate on that using more formal language suitable for an academic discussion?"
            
        else:
            # Clean content - proceed with normal IELTS speaking assessment flow
            return None  # Let normal conversation flow continue
    
    def log_moderation_event(self, user_id: str, content: str, severity: ModerationSeverity, action_taken: str):
        """Log moderation events for compliance and improvement"""
        logging.info(f"Content moderation event: user={user_id}, severity={severity.value}, action={action_taken}")
        
        # In production, this would log to CloudWatch/DynamoDB for compliance
        moderation_log = {
            'timestamp': self._get_timestamp(),
            'user_id': user_id,
            'content_hash': self._hash_content(content),  # Never log actual content
            'severity': severity.value,
            'action_taken': action_taken,
            'assessment_type': 'speaking'
        }
        
        # Store in secure logging system
        self._store_moderation_log(moderation_log)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for logging"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    def _hash_content(self, content: str) -> str:
        """Create hash of content for logging (privacy protection)"""
        import hashlib
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _store_moderation_log(self, log_entry: Dict):
        """Store moderation log securely"""
        # In production, this would use AWS CloudWatch or DynamoDB
        logging.info(f"Moderation log: {log_entry}")

# Global instance for use across the application
content_moderator = ContentModerationService()

def moderate_speaking_content(user_text: str, user_id: str = "anonymous") -> Tuple[bool, str, Optional[str]]:
    """
    Convenient function to moderate speaking assessment content
    
    Returns:
        Tuple of (continue_assessment, processed_text, examiner_response)
    """
    moderation_result = content_moderator.moderate_content(user_text, "speaking")
    severity, redirection, processed_text = moderation_result
    
    # Log the event
    content_moderator.log_moderation_event(
        user_id=user_id,
        content=user_text,
        severity=severity,
        action_taken=f"redirection_given" if redirection else "clean_content"
    )
    
    # Determine if assessment should continue
    continue_assessment = severity != ModerationSeverity.SEVERE
    
    # Generate examiner response
    examiner_response = content_moderator.generate_examiner_response(user_text, moderation_result)
    
    return continue_assessment, processed_text, examiner_response

if __name__ == "__main__":
    # Test the content moderation service
    test_cases = [
        "I really enjoy reading books and learning new languages.",
        "This f***ing test is so damn hard!",
        "I like to drink alcohol every weekend with friends.",
        "I want to kill this exam and get the best score possible.",
        "My hobby is collecting stamps from different countries.",
    ]
    
    for test_text in test_cases:
        continue_assessment, processed_text, examiner_response = moderate_speaking_content(test_text)
        print(f"\nInput: {test_text}")
        print(f"Continue: {continue_assessment}")
        print(f"Examiner Response: {examiner_response}")
        print("-" * 50)