"""
IELTS Writing Assessment using AWS Nova Micro model.
This module provides functions to evaluate IELTS writing responses with AWS Bedrock Nova Micro.
"""
import os
import json
import logging
from aws_bedrock_services import evaluate_writing_with_nova_micro
from assessment_criteria.writing_criteria import calculate_writing_band_score

logger = logging.getLogger(__name__)

def assess_writing_task1(essay_text, task_prompt, ielts_test_type="academic"):
    """
    Assess an IELTS Writing Task 1 response using AWS Nova Micro.
    
    Args:
        essay_text (str): The candidate's essay
        task_prompt (str): The original task prompt
        ielts_test_type (str): "academic" or "general"
        
    Returns:
        dict: Assessment results including scores and feedback
    """
    try:
        # Call the Nova Micro assessment function
        assessment_result = evaluate_writing_with_nova_micro(essay_text, task_prompt, "task1")
        
        # Format the result to match the expected structure in routes
        formatted_result = {
            "scores": assessment_result.get("criteria_scores", {}),
            "criterion_feedback": assessment_result.get("detailed_feedback", {}),
            "overall_feedback": assessment_result.get("summary_feedback", ""),
            "word_count": len(essay_text.split()),
            "strengths": [],
            "areas_for_improvement": []
        }
        
        # Extract strengths and areas for improvement from the feedback if available
        if "summary_feedback" in assessment_result and assessment_result["summary_feedback"]:
            feedback = assessment_result["summary_feedback"]
            if "strengths" in feedback.lower():
                strengths_section = feedback.split("strengths:", 1)[1].split("areas", 1)[0].strip()
                formatted_result["strengths"] = [s.strip() for s in strengths_section.split(",") if s.strip()]
            
            if "improvement" in feedback.lower() or "improve" in feedback.lower():
                try:
                    areas_section = feedback.split("improvement:", 1)[1].strip()
                    formatted_result["areas_for_improvement"] = [a.strip() for a in areas_section.split(",") if a.strip()]
                except:
                    # If splitting fails, try to extract differently
                    formatted_result["areas_for_improvement"] = ["Review detailed feedback for areas to improve"]
        
        # Calculate overall band score for the task
        if "criteria_scores" in assessment_result:
            scores = assessment_result["criteria_scores"]
            formatted_result["overall_band_for_task"] = sum(scores.values()) / len(scores) if scores else 0
            
        return formatted_result
        
    except Exception as e:
        logger.error(f"Error assessing Task 1 with Nova Micro: {str(e)}")
        logger.info("Falling back to OpenAI assessment...")
        
        # Fall back to OpenAI if Nova Micro fails
        try:
            from openai_writing_assessment import assess_writing_task1 as openai_assess_task1
            return openai_assess_task1(essay_text, task_prompt, ielts_test_type)
        except Exception as fallback_error:
            logger.error(f"Fallback to OpenAI also failed: {str(fallback_error)}")
            # Return a basic error response
            return {
                "error": str(e),
                "scores": {
                    "Task Achievement": 0,
                    "Coherence and Cohesion": 0,
                    "Lexical Resource": 0,
                    "Grammatical Range and Accuracy": 0
                },
                "overall_band_for_task": 0,
                "overall_feedback": "An error occurred during the assessment."
            }

def assess_writing_task2(essay_text, task_prompt, ielts_test_type="academic"):
    """
    Assess an IELTS Writing Task 2 response using AWS Nova Micro.
    
    Args:
        essay_text (str): The candidate's essay
        task_prompt (str): The original task prompt
        ielts_test_type (str): "academic" or "general"
        
    Returns:
        dict: Assessment results including scores and feedback
    """
    try:
        # Call the Nova Micro assessment function
        assessment_result = evaluate_writing_with_nova_micro(essay_text, task_prompt, "task2")
        
        # Format the result to match the expected structure in routes
        formatted_result = {
            "scores": assessment_result.get("criteria_scores", {}),
            "criterion_feedback": assessment_result.get("detailed_feedback", {}),
            "overall_feedback": assessment_result.get("summary_feedback", ""),
            "word_count": len(essay_text.split()),
            "strengths": [],
            "areas_for_improvement": []
        }
        
        # Extract strengths and areas for improvement from the feedback if available
        if "summary_feedback" in assessment_result and assessment_result["summary_feedback"]:
            feedback = assessment_result["summary_feedback"]
            if "strengths" in feedback.lower():
                strengths_section = feedback.split("strengths:", 1)[1].split("areas", 1)[0].strip()
                formatted_result["strengths"] = [s.strip() for s in strengths_section.split(",") if s.strip()]
            
            if "improvement" in feedback.lower() or "improve" in feedback.lower():
                try:
                    areas_section = feedback.split("improvement:", 1)[1].strip()
                    formatted_result["areas_for_improvement"] = [a.strip() for a in areas_section.split(",") if a.strip()]
                except:
                    # If splitting fails, try to extract differently
                    formatted_result["areas_for_improvement"] = ["Review detailed feedback for areas to improve"]
        
        # Calculate overall band score for the task
        if "criteria_scores" in assessment_result:
            scores = assessment_result["criteria_scores"]
            formatted_result["overall_band_for_task"] = sum(scores.values()) / len(scores) if scores else 0
            
        return formatted_result
        
    except Exception as e:
        logger.error(f"Error assessing Task 2 with Nova Micro: {str(e)}")
        logger.info("Falling back to OpenAI assessment...")
        
        # Fall back to OpenAI if Nova Micro fails
        try:
            from openai_writing_assessment import assess_writing_task2 as openai_assess_task2
            return openai_assess_task2(essay_text, task_prompt, ielts_test_type)
        except Exception as fallback_error:
            logger.error(f"Fallback to OpenAI also failed: {str(fallback_error)}")
            # Return a basic error response
            return {
                "error": str(e),
                "scores": {
                    "Task Response": 0,
                    "Coherence and Cohesion": 0,
                    "Lexical Resource": 0,
                    "Grammatical Range and Accuracy": 0
                },
                "overall_band_for_task": 0,
                "overall_feedback": "An error occurred during the assessment."
            }

def assess_complete_writing_test(task1_essay, task1_prompt, task2_essay, task2_prompt, ielts_test_type="academic"):
    """
    Assess a complete IELTS Writing test (Task 1 and Task 2) and calculate the overall band score.
    
    Args:
        task1_essay (str): The candidate's Task 1 essay
        task1_prompt (str): The original Task 1 prompt
        task2_essay (str): The candidate's Task 2 essay
        task2_prompt (str): The original Task 2 prompt
        ielts_test_type (str): "academic" or "general"
        
    Returns:
        dict: Complete assessment results including individual task scores and overall band score
    """
    # Assess Task 1
    task1_assessment = assess_writing_task1(task1_essay, task1_prompt, ielts_test_type)
    
    # Assess Task 2
    task2_assessment = assess_writing_task2(task2_essay, task2_prompt, ielts_test_type)
    
    # Calculate overall band score
    overall_band = 0
    if "scores" in task1_assessment and "scores" in task2_assessment:
        try:
            overall_band = calculate_writing_band_score(task1_assessment["scores"], task2_assessment["scores"])
        except Exception as e:
            logger.error(f"Error calculating overall band score: {str(e)}")
            
    # Combine results
    combined_assessment = {
        "task1": task1_assessment,
        "task2": task2_assessment,
        "overall_band": overall_band,
        "ielts_test_type": ielts_test_type
    }
    
    return combined_assessment
