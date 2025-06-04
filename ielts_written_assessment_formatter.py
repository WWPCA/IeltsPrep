"""
Professional IELTS Written Assessment Formatter
Creates comprehensive, professionally formatted assessment reports for users.
"""

from datetime import datetime
import json

class IELTSWrittenAssessmentFormatter:
    """
    Professional formatter for IELTS speaking and writing assessments
    Following official IELTS assessment report standards
    """
    
    ASSESSMENT_HEADER = """
    ═══════════════════════════════════════════════════════════════════════════════
                                IELTS ASSESSMENT REPORT
                           International English Language Testing System
    ═══════════════════════════════════════════════════════════════════════════════
    """
    
    BAND_SCORE_DESCRIPTIONS = {
        9: "Expert User - Has fully operational command of the language",
        8: "Very Good User - Has fully operational command with only occasional unsystematic inaccuracies",
        7: "Good User - Has operational command of the language, though with occasional inaccuracies",
        6: "Competent User - Has generally effective command despite some inaccuracies",
        5: "Modest User - Has partial command; copes with overall meaning in most situations",
        4: "Limited User - Basic competence limited to familiar situations",
        3: "Extremely Limited User - Conveys and understands only general meaning",
        2: "Intermittent User - No real communication possible except for basic information",
        1: "Non User - Essentially has no ability to use the language"
    }
    
    @classmethod
    def format_speaking_assessment(cls, assessment_data):
        """
        Format comprehensive speaking assessment report
        
        Args:
            assessment_data (dict): Complete assessment results from Nova Sonic
            
        Returns:
            str: Professional formatted assessment report
        """
        
        current_date = datetime.now().strftime("%B %d, %Y")
        report_id = assessment_data.get('conversation_id', 'IELTS_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
        
        # Extract key data
        overall_band = assessment_data.get('overall_band_score', 0)
        individual_scores = assessment_data.get('individual_scores', {})
        performance_summary = assessment_data.get('performance_summary', {})
        band_descriptors = assessment_data.get('band_descriptors', {})
        recommendations = assessment_data.get('improvement_recommendations', [])
        
        # Build professional report
        report = cls.ASSESSMENT_HEADER
        
        # Assessment Details Section
        report += f"""
    ASSESSMENT DETAILS
    ───────────────────────────────────────────────────────────────────────────────
    Report ID:           {report_id}
    Assessment Date:     {current_date}
    Test Type:           {performance_summary.get('assessment_type', 'Academic Speaking').replace('_', ' ').title()}
    Duration:            {performance_summary.get('assessment_duration_minutes', 0)} minutes
    Parts Completed:     Part {performance_summary.get('part_completed', 1)}
    Total Questions:     {performance_summary.get('total_questions', 0)}
    
    """
        
        # Overall Band Score Section
        overall_desc = cls.BAND_SCORE_DESCRIPTIONS.get(int(overall_band), "Assessment in progress")
        report += f"""
    OVERALL BAND SCORE
    ───────────────────────────────────────────────────────────────────────────────
    
                              BAND SCORE: {overall_band}
                         {overall_desc}
    
    """
        
        # Individual Component Scores
        report += """
    COMPONENT SCORES
    ───────────────────────────────────────────────────────────────────────────────
    
    """
        
        components = {
            'fluency_coherence': 'Fluency and Coherence',
            'lexical_resource': 'Lexical Resource', 
            'grammar_accuracy': 'Grammatical Range and Accuracy',
            'pronunciation': 'Pronunciation'
        }
        
        for key, title in components.items():
            score = individual_scores.get(key, 0)
            descriptor_data = band_descriptors.get(key, {})
            descriptor = descriptor_data.get('descriptor', 'Assessment in progress')
            
            report += f"""
    {title:.<50} Band {score}
    
    Assessment: {descriptor}
    
    """
        
        # Performance Analysis Section
        report += """
    PERFORMANCE ANALYSIS
    ───────────────────────────────────────────────────────────────────────────────
    
    """
        
        # Add detailed performance feedback
        if individual_scores.get('fluency_coherence', 0) >= 7:
            report += "✓ STRENGTHS: Demonstrates good fluency with natural speech patterns\n"
        elif individual_scores.get('fluency_coherence', 0) >= 5:
            report += "• DEVELOPING: Shows adequate fluency with some hesitation\n"
        else:
            report += "⚠ FOCUS AREA: Fluency needs significant improvement\n"
            
        if individual_scores.get('lexical_resource', 0) >= 7:
            report += "✓ STRENGTHS: Uses varied and appropriate vocabulary effectively\n"
        elif individual_scores.get('lexical_resource', 0) >= 5:
            report += "• DEVELOPING: Demonstrates reasonable vocabulary range\n"
        else:
            report += "⚠ FOCUS AREA: Vocabulary range requires expansion\n"
            
        if individual_scores.get('grammar_accuracy', 0) >= 7:
            report += "✓ STRENGTHS: Shows good grammatical control and variety\n"
        elif individual_scores.get('grammar_accuracy', 0) >= 5:
            report += "• DEVELOPING: Uses basic grammar with some complex structures\n"
        else:
            report += "⚠ FOCUS AREA: Grammar accuracy needs attention\n"
            
        report += "\n"
        
        # Improvement Recommendations
        if recommendations:
            report += """
    IMPROVEMENT RECOMMENDATIONS
    ───────────────────────────────────────────────────────────────────────────────
    
    """
            for i, recommendation in enumerate(recommendations[:5], 1):
                report += f"    {i}. {recommendation}\n"
            
        # Study Guidance Section
        report += f"""
    
    STUDY GUIDANCE
    ───────────────────────────────────────────────────────────────────────────────
    
    Based on your current band score of {overall_band}, we recommend:
    
    """
        
        if overall_band >= 7:
            report += """
    • Focus on achieving consistency across all four criteria
    • Practice with complex academic topics and abstract concepts
    • Work on subtle language features and natural expression
    • Aim for precision in vocabulary and grammatical structures
    """
        elif overall_band >= 6:
            report += """
    • Expand vocabulary range with topic-specific terminology
    • Practice complex grammatical structures regularly
    • Work on reducing hesitation and improving flow
    • Focus on clear pronunciation and word stress
    """
        elif overall_band >= 5:
            report += """
    • Build confidence with extended speaking practice
    • Learn common IELTS topic vocabulary systematically
    • Practice basic to intermediate grammar structures
    • Work on clear pronunciation of individual sounds
    """
        else:
            report += """
    • Focus on building fundamental speaking confidence
    • Learn essential vocabulary for common topics
    • Practice basic sentence structures daily
    • Work with pronunciation fundamentals
    """
        
        # Assessment Methodology
        report += """
    
    ASSESSMENT METHODOLOGY
    ───────────────────────────────────────────────────────────────────────────────
    
    This assessment was conducted using:
    • Official IELTS Speaking test format and timing
    • Authentic IELTS question database
    • Real-time evaluation against official band descriptors
    • Professional AI examiner (Maya) with British accent
    • Comprehensive performance tracking and analysis
    
    """
        
        # Footer
        report += f"""
    ═══════════════════════════════════════════════════════════════════════════════
                        Assessment completed on {current_date}
                          IELTS GenAI Prep - Professional Assessment
    ═══════════════════════════════════════════════════════════════════════════════
    """
        
        return report
    
    @classmethod
    def format_writing_assessment(cls, writing_data):
        """
        Format comprehensive writing assessment report
        
        Args:
            writing_data (dict): Writing assessment results
            
        Returns:
            str: Professional formatted writing assessment
        """
        
        current_date = datetime.now().strftime("%B %d, %Y")
        
        report = cls.ASSESSMENT_HEADER
        
        # Writing-specific assessment details
        task_type = writing_data.get('task_type', 'Academic Writing')
        word_count = writing_data.get('word_count', 0)
        time_taken = writing_data.get('time_taken_minutes', 0)
        
        report += f"""
    WRITING ASSESSMENT DETAILS
    ───────────────────────────────────────────────────────────────────────────────
    Assessment Date:     {current_date}
    Task Type:          {task_type}
    Word Count:         {word_count} words
    Time Taken:         {time_taken} minutes
    
    """
        
        # Writing band scores
        overall_score = writing_data.get('overall_band_score', 0)
        components = writing_data.get('component_scores', {})
        
        report += f"""
    OVERALL WRITING BAND SCORE: {overall_score}
    ───────────────────────────────────────────────────────────────────────────────
    
    Task Achievement/Response:     Band {components.get('task_achievement', 0)}
    Coherence and Cohesion:       Band {components.get('coherence_cohesion', 0)}
    Lexical Resource:             Band {components.get('lexical_resource', 0)}
    Grammatical Range/Accuracy:   Band {components.get('grammar_accuracy', 0)}
    
    """
        
        # Writing-specific feedback
        feedback = writing_data.get('detailed_feedback', [])
        if feedback:
            report += """
    DETAILED FEEDBACK
    ───────────────────────────────────────────────────────────────────────────────
    
    """
            for item in feedback:
                report += f"    • {item}\n"
        
        report += f"""
    
    ═══════════════════════════════════════════════════════════════════════════════
                        Writing Assessment completed on {current_date}
                          IELTS GenAI Prep - Professional Assessment
    ═══════════════════════════════════════════════════════════════════════════════
    """
        
        return report
    
    @classmethod
    def generate_progress_report(cls, user_assessments):
        """
        Generate comprehensive progress tracking report
        
        Args:
            user_assessments (list): List of user's assessment history
            
        Returns:
            str: Professional progress report
        """
        
        current_date = datetime.now().strftime("%B %d, %Y")
        
        report = cls.ASSESSMENT_HEADER.replace("ASSESSMENT REPORT", "PROGRESS REPORT")
        
        report += f"""
    PROGRESS TRACKING SUMMARY
    ───────────────────────────────────────────────────────────────────────────────
    Report Date:         {current_date}
    Total Assessments:   {len(user_assessments)}
    Period Covered:      Last 30 days
    
    """
        
        if user_assessments:
            # Calculate progress metrics
            scores = [a.get('overall_band_score', 0) for a in user_assessments]
            latest_score = scores[-1] if scores else 0
            initial_score = scores[0] if scores else 0
            improvement = latest_score - initial_score
            
            report += f"""
    SCORE PROGRESSION
    ───────────────────────────────────────────────────────────────────────────────
    
    Initial Score:       Band {initial_score}
    Latest Score:        Band {latest_score}
    Total Improvement:   {'+' if improvement >= 0 else ''}{improvement} band points
    
    """
            
            # Assessment history
            report += """
    ASSESSMENT HISTORY
    ───────────────────────────────────────────────────────────────────────────────
    
    """
            
            for i, assessment in enumerate(user_assessments[-5:], 1):  # Last 5 assessments
                date = assessment.get('date', 'Recent')
                score = assessment.get('overall_band_score', 0)
                test_type = assessment.get('type', 'Speaking')
                report += f"    {i}. {date} - {test_type} - Band {score}\n"
        
        report += f"""
    
    ═══════════════════════════════════════════════════════════════════════════════
                        Progress Report generated on {current_date}
                          IELTS GenAI Prep - Professional Assessment
    ═══════════════════════════════════════════════════════════════════════════════
    """
        
        return report