"""
Format Nova Sonic Assessment into Written IELTS Rubric
This module takes Nova Sonic's real-time assessment and creates formatted written documentation.
"""

import json
from datetime import datetime

def format_sonic_assessment_to_rubric(sonic_assessment_data):
    """
    Format Nova Sonic's real-time assessment into written IELTS rubric format.
    
    Args:
        sonic_assessment_data (dict): Assessment data from Nova Sonic's real-time evaluation
        
    Returns:
        dict: Formatted written assessment following official IELTS rubric structure
    """
    
    # Extract Nova Sonic's assessment results
    overall_score = sonic_assessment_data.get('overall_band_score', 7.0)
    fluency_score = sonic_assessment_data.get('fluency_coherence_score', 7.0)
    lexical_score = sonic_assessment_data.get('lexical_resource_score', 7.0)
    grammar_score = sonic_assessment_data.get('grammatical_range_score', 7.0)
    pronunciation_score = sonic_assessment_data.get('pronunciation_score', 7.0)
    
    # Format into official IELTS rubric structure
    formatted_assessment = {
        "assessment_date": datetime.utcnow().isoformat(),
        "overall_band_score": overall_score,
        "assessment_type": "Speaking Assessment - Real-time Conversational",
        
        "fluency_and_coherence": {
            "band_score": fluency_score,
            "criteria": "Speech flow, logical progression, discourse markers, self-correction",
            "performance_notes": sonic_assessment_data.get('fluency_feedback', ''),
            "strengths": sonic_assessment_data.get('fluency_strengths', []),
            "areas_for_improvement": sonic_assessment_data.get('fluency_improvements', [])
        },
        
        "lexical_resource": {
            "band_score": lexical_score,
            "criteria": "Vocabulary range, word choice, idiomatic expressions, paraphrasing",
            "performance_notes": sonic_assessment_data.get('lexical_feedback', ''),
            "strengths": sonic_assessment_data.get('lexical_strengths', []),
            "areas_for_improvement": sonic_assessment_data.get('lexical_improvements', [])
        },
        
        "grammatical_range_and_accuracy": {
            "band_score": grammar_score,
            "criteria": "Sentence variety, grammar accuracy, complex structures, error patterns",
            "performance_notes": sonic_assessment_data.get('grammar_feedback', ''),
            "strengths": sonic_assessment_data.get('grammar_strengths', []),
            "areas_for_improvement": sonic_assessment_data.get('grammar_improvements', [])
        },
        
        "pronunciation": {
            "band_score": pronunciation_score,
            "criteria": "Sound clarity, stress patterns, rhythm, intonation, intelligibility",
            "performance_notes": sonic_assessment_data.get('pronunciation_feedback', ''),
            "strengths": sonic_assessment_data.get('pronunciation_strengths', []),
            "areas_for_improvement": sonic_assessment_data.get('pronunciation_improvements', [])
        },
        
        "overall_feedback": {
            "summary": sonic_assessment_data.get('overall_feedback', ''),
            "key_recommendations": sonic_assessment_data.get('key_recommendations', []),
            "next_steps": sonic_assessment_data.get('next_steps', [])
        },
        
        "conversation_details": {
            "total_speaking_time": sonic_assessment_data.get('speaking_duration', ''),
            "interaction_quality": sonic_assessment_data.get('interaction_quality', ''),
            "response_appropriateness": sonic_assessment_data.get('response_appropriateness', '')
        }
    }
    
    return formatted_assessment

def create_written_assessment_report(formatted_assessment):
    """
    Create a comprehensive written assessment report from formatted data.
    
    Args:
        formatted_assessment (dict): Formatted assessment data
        
    Returns:
        str: Written assessment report in professional format
    """
    
    report = f"""
IELTS SPEAKING ASSESSMENT REPORT
Generated: {formatted_assessment['assessment_date']}
Assessment Type: {formatted_assessment['assessment_type']}

OVERALL BAND SCORE: {formatted_assessment['overall_band_score']}/9.0

═══════════════════════════════════════════════════════════════

DETAILED ASSESSMENT BY CRITERIA:

1. FLUENCY AND COHERENCE - Band Score: {formatted_assessment['fluency_and_coherence']['band_score']}/9.0
   
   Assessment Criteria: {formatted_assessment['fluency_and_coherence']['criteria']}
   
   Performance Notes:
   {formatted_assessment['fluency_and_coherence']['performance_notes']}
   
   Strengths:
   {chr(10).join(f"   • {strength}" for strength in formatted_assessment['fluency_and_coherence']['strengths'])}
   
   Areas for Improvement:
   {chr(10).join(f"   • {improvement}" for improvement in formatted_assessment['fluency_and_coherence']['areas_for_improvement'])}

───────────────────────────────────────────────────────────────

2. LEXICAL RESOURCE - Band Score: {formatted_assessment['lexical_resource']['band_score']}/9.0
   
   Assessment Criteria: {formatted_assessment['lexical_resource']['criteria']}
   
   Performance Notes:
   {formatted_assessment['lexical_resource']['performance_notes']}
   
   Strengths:
   {chr(10).join(f"   • {strength}" for strength in formatted_assessment['lexical_resource']['strengths'])}
   
   Areas for Improvement:
   {chr(10).join(f"   • {improvement}" for improvement in formatted_assessment['lexical_resource']['areas_for_improvement'])}

───────────────────────────────────────────────────────────────

3. GRAMMATICAL RANGE AND ACCURACY - Band Score: {formatted_assessment['grammatical_range_and_accuracy']['band_score']}/9.0
   
   Assessment Criteria: {formatted_assessment['grammatical_range_and_accuracy']['criteria']}
   
   Performance Notes:
   {formatted_assessment['grammatical_range_and_accuracy']['performance_notes']}
   
   Strengths:
   {chr(10).join(f"   • {strength}" for strength in formatted_assessment['grammatical_range_and_accuracy']['strengths'])}
   
   Areas for Improvement:
   {chr(10).join(f"   • {improvement}" for improvement in formatted_assessment['grammatical_range_and_accuracy']['areas_for_improvement'])}

───────────────────────────────────────────────────────────────

4. PRONUNCIATION - Band Score: {formatted_assessment['pronunciation']['band_score']}/9.0
   
   Assessment Criteria: {formatted_assessment['pronunciation']['criteria']}
   
   Performance Notes:
   {formatted_assessment['pronunciation']['performance_notes']}
   
   Strengths:
   {chr(10).join(f"   • {strength}" for strength in formatted_assessment['pronunciation']['strengths'])}
   
   Areas for Improvement:
   {chr(10).join(f"   • {improvement}" for improvement in formatted_assessment['pronunciation']['areas_for_improvement'])}

═══════════════════════════════════════════════════════════════

OVERALL PERFORMANCE SUMMARY:

{formatted_assessment['overall_feedback']['summary']}

KEY RECOMMENDATIONS:
{chr(10).join(f"• {rec}" for rec in formatted_assessment['overall_feedback']['key_recommendations'])}

SUGGESTED NEXT STEPS:
{chr(10).join(f"• {step}" for step in formatted_assessment['overall_feedback']['next_steps'])}

───────────────────────────────────────────────────────────────

CONVERSATION ANALYSIS:
• Speaking Duration: {formatted_assessment['conversation_details']['total_speaking_time']}
• Interaction Quality: {formatted_assessment['conversation_details']['interaction_quality']}
• Response Appropriateness: {formatted_assessment['conversation_details']['response_appropriateness']}

═══════════════════════════════════════════════════════════════
End of Assessment Report
"""
    
    return report

def save_assessment_to_database(user_id, assessment_data, written_report):
    """
    Save the formatted assessment to database for user records.
    
    Args:
        user_id (int): User ID
        assessment_data (dict): Formatted assessment data
        written_report (str): Written assessment report
    """
    from models import db, UserTestAttempt
    
    try:
        # Create assessment record
        test_attempt = UserTestAttempt(
            user_id=user_id,
            test_type='speaking_conversational',
            overall_score=assessment_data['overall_band_score'],
            fluency_coherence_score=assessment_data['fluency_and_coherence']['band_score'],
            lexical_resource_score=assessment_data['lexical_resource']['band_score'],
            grammatical_range_score=assessment_data['grammatical_range_and_accuracy']['band_score'],
            pronunciation_score=assessment_data['pronunciation']['band_score'],
            detailed_feedback=written_report,
            assessment_data=json.dumps(assessment_data)
        )
        
        db.session.add(test_attempt)
        db.session.commit()
        
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"Error saving assessment: {e}")
        return False