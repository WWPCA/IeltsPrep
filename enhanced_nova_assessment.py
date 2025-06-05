"""
Enhanced Nova Assessment Module
Provides enhanced Nova AI assessment capabilities
"""

from comprehensive_nova_service import comprehensive_nova_service

def get_enhanced_assessment(assessment_type, content, prompt):
    """Get enhanced assessment using Nova services"""
    if 'writing' in assessment_type:
        return comprehensive_nova_service.assess_writing_with_nova(
            content, prompt, 'task1' if 'task1' in assessment_type else 'task2', assessment_type
        )
    elif 'speaking' in assessment_type:
        return comprehensive_nova_service.analyze_speaking_transcript(content, 1, assessment_type)
    
    return {'success': False, 'error': 'Unsupported assessment type'}