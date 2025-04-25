"""
OpenAI GPT-4o Integration for IELTS Writing Assessment
This module provides functions to assess IELTS writing tasks using OpenAI's GPT-4o.
"""

import os
import json
import requests
from openai import OpenAI
from assessment_criteria.writing_criteria import (
    WRITING_TASK1_BAND_DESCRIPTORS, 
    WRITING_TASK2_BAND_DESCRIPTORS,
    WRITING_ASSESSMENT_CRITERIA,
    calculate_writing_band_score
)

# Initialize OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def assess_writing_task1(essay_text, task_prompt, ielts_test_type="academic"):
    """
    Assess an IELTS Writing Task 1 response using GPT-4o.
    
    Args:
        essay_text (str): The candidate's essay
        task_prompt (str): The original task prompt
        ielts_test_type (str): "academic" or "general"
        
    Returns:
        dict: Assessment results including scores and feedback
    """
    # Create system prompt with IELTS criteria
    criteria_descriptions = ""
    for criterion, description in WRITING_ASSESSMENT_CRITERIA.items():
        if criterion != "Task Response":  # Task Response is for Task 2
            criteria_descriptions += f"- {criterion}: {description}\n"
    
    # Format band descriptors for easier reference by the model
    band_descriptors_text = ""
    for band in range(9, 3, -1):  # Include bands 9 down to 4
        band_descriptors_text += f"\nBand {band}:\n"
        for criterion, descriptor in WRITING_TASK1_BAND_DESCRIPTORS[band].items():
            if criterion != "Task Response":  # Task Response is for Task 2
                band_descriptors_text += f"- {criterion}: {descriptor}\n"
    
    # Customize instructions based on test type
    test_type_instructions = ""
    if ielts_test_type == "academic":
        test_type_instructions = """
        This is an Academic IELTS Writing Task 1 which typically involves describing visual information 
        (graph/table/chart/diagram) or a process. The candidate should identify key features, describe trends, 
        make comparisons, and organize information logically.
        """
    elif ielts_test_type == "general":
        test_type_instructions = """
        This is a General Training IELTS Writing Task 1 which involves writing a letter.
        The candidate should address the prompt's requirements, use an appropriate tone and format for the specified 
        context (formal, semi-formal, or informal), and develop ideas with proper organization.
        """
    
    system_prompt = f"""
    You are an expert IELTS Writing examiner tasked with assessing a candidate's response to a Writing Task 1 prompt.
    
    Assessment Criteria:
    {criteria_descriptions}
    
    IELTS Band Descriptors (Selected bands):
    {band_descriptors_text}
    
    {test_type_instructions}
    
    Provide a fair, detailed assessment for each criterion. Score each criterion from 0 to 9.
    
    Return your assessment in the following JSON format:
    {{
        "scores": {{
            "Task Achievement": number,
            "Coherence and Cohesion": number,
            "Lexical Resource": number,
            "Grammatical Range and Accuracy": number
        }},
        "criterion_feedback": {{
            "Task Achievement": "detailed feedback",
            "Coherence and Cohesion": "detailed feedback",
            "Lexical Resource": "detailed feedback",
            "Grammatical Range and Accuracy": "detailed feedback"
        }},
        "word_count": number,
        "strengths": ["strength1", "strength2", "strength3"],
        "areas_for_improvement": ["area1", "area2", "area3"],
        "overall_feedback": "summary feedback paragraph"
    }}
    """
    
    # Format user message with the candidate's essay
    user_message = f"""
    Writing Task 1 Prompt: {task_prompt}
    
    Candidate's Essay:
    {essay_text}
    
    Please provide a detailed IELTS assessment of this Writing Task 1 response.
    """
    
    # Call OpenAI API
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse the assessment result
        assessment = json.loads(response.choices[0].message.content)
        
        # Calculate band score
        if "scores" in assessment:
            assessment["overall_band_for_task"] = sum(assessment["scores"].values()) / 4
        
        return assessment
        
    except Exception as e:
        print(f"Error during GPT-4o Task 1 assessment: {str(e)}")
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
    Assess an IELTS Writing Task 2 response using GPT-4o.
    
    Args:
        essay_text (str): The candidate's essay
        task_prompt (str): The original task prompt
        ielts_test_type (str): "academic" or "general"
        
    Returns:
        dict: Assessment results including scores and feedback
    """
    # Create system prompt with IELTS criteria
    criteria_descriptions = ""
    for criterion, description in WRITING_ASSESSMENT_CRITERIA.items():
        if criterion != "Task Achievement":  # Task Achievement is for Task 1
            criteria_descriptions += f"- {criterion}: {description}\n"
    
    # Format band descriptors for easier reference by the model
    band_descriptors_text = ""
    for band in range(9, 3, -1):  # Include bands 9 down to 4
        band_descriptors_text += f"\nBand {band}:\n"
        for criterion, descriptor in WRITING_TASK2_BAND_DESCRIPTORS[band].items():
            if criterion != "Task Achievement":  # Task Achievement is for Task 1
                band_descriptors_text += f"- {criterion}: {descriptor}\n"
    
    # Customize instructions based on test type
    test_type_instructions = ""
    if ielts_test_type == "academic":
        test_type_instructions = """
        This is an Academic IELTS Writing Task 2 which involves writing an essay in response to a point of view, 
        argument, or problem. The candidate should present a clear position, develop ideas with relevant examples, 
        and organize their essay coherently.
        """
    elif ielts_test_type == "general":
        test_type_instructions = """
        This is a General Training IELTS Writing Task 2 which involves writing an essay in response to a point of view, 
        argument, or problem. Topics are often more related to everyday concerns. The candidate should present a clear 
        position, develop ideas with relevant examples, and organize their essay coherently.
        """
    
    system_prompt = f"""
    You are an expert IELTS Writing examiner tasked with assessing a candidate's response to a Writing Task 2 prompt.
    
    Assessment Criteria:
    {criteria_descriptions}
    
    IELTS Band Descriptors (Selected bands):
    {band_descriptors_text}
    
    {test_type_instructions}
    
    Provide a fair, detailed assessment for each criterion. Score each criterion from 0 to 9.
    
    Return your assessment in the following JSON format:
    {{
        "scores": {{
            "Task Response": number,
            "Coherence and Cohesion": number,
            "Lexical Resource": number,
            "Grammatical Range and Accuracy": number
        }},
        "criterion_feedback": {{
            "Task Response": "detailed feedback",
            "Coherence and Cohesion": "detailed feedback",
            "Lexical Resource": "detailed feedback",
            "Grammatical Range and Accuracy": "detailed feedback"
        }},
        "word_count": number,
        "strengths": ["strength1", "strength2", "strength3"],
        "areas_for_improvement": ["area1", "area2", "area3"],
        "overall_feedback": "summary feedback paragraph"
    }}
    """
    
    # Format user message with the candidate's essay
    user_message = f"""
    Writing Task 2 Prompt: {task_prompt}
    
    Candidate's Essay:
    {essay_text}
    
    Please provide a detailed IELTS assessment of this Writing Task 2 response.
    """
    
    # Call OpenAI API
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse the assessment result
        assessment = json.loads(response.choices[0].message.content)
        
        # Calculate band score
        if "scores" in assessment:
            assessment["overall_band_for_task"] = sum(assessment["scores"].values()) / 4
        
        return assessment
        
    except Exception as e:
        print(f"Error during GPT-4o Task 2 assessment: {str(e)}")
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
            print(f"Error calculating overall band score: {str(e)}")
            
    # Combine results
    combined_assessment = {
        "task1": task1_assessment,
        "task2": task2_assessment,
        "overall_band": overall_band,
        "ielts_test_type": ielts_test_type
    }
    
    return combined_assessment