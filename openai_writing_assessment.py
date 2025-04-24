"""
IELTS Writing Assessment Implementation using OpenAI GPT-4o
This module implements the OpenAI API integration for IELTS writing assessment.
"""

import json
import os
import time
from typing import Dict, Any, List, Optional, Tuple

# Import the prompt construction module
from openai_assessment_prompts import construct_assessment_prompt

# Initialize OpenAI client lazily when API key is provided
client = None

def initialize_openai():
    """Initialize OpenAI client when API key is available"""
    from openai import OpenAI
    global client
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        client = OpenAI(api_key=api_key)
        return True
    return False

# Import tenacity for retry logic
try:
    from tenacity import retry, stop_after_attempt, wait_exponential
    has_tenacity = True
except ImportError:
    has_tenacity = False
    # Define a simple decorator if tenacity is not available
    def retry(stop=None, wait=None):
        def decorator(func):
            return func
        return decorator

def get_openai_response(messages: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Send a request to the OpenAI API with retry logic for robustness.
    
    Args:
        messages: List of message dictionaries for the chat completion
        
    Returns:
        The API response content
    """
    # Check if we have initialized OpenAI client
    if not initialize_openai():
        # Return mock response if API key is not available
        return {
            "error": True,
            "message": "OpenAI API key not available. Please set the OPENAI_API_KEY environment variable."
        }
    
    try:
        # Define retry decorator if tenacity is available
        retry_decorator = retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10)) if has_tenacity else lambda f: f
        
        # Define the actual API call function
        @retry_decorator
        def call_openai_api():
            response = client.chat.completions.create(
                model="gpt-4o",  # Using the latest model for best results
                messages=messages,
                temperature=0.2,  # Lower temperature for more consistent results
                response_format={"type": "json_object"},  # Ensure JSON response
                max_tokens=1500  # Ensure enough tokens for detailed feedback
            )
            return json.loads(response.choices[0].message.content)
        
        # Call the API
        return call_openai_api()
    except Exception as e:
        print(f"Error calling OpenAI API: {str(e)}")
        return {
            "error": True,
            "message": f"Error calling OpenAI API: {str(e)}"
        }

def count_words(text: str) -> int:
    """
    Count the number of words in a text.
    
    Args:
        text: The text to count words in
        
    Returns:
        Word count as an integer
    """
    return len(text.split())

def assess_writing(essay_text: str, task_prompt: str, task_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Main function to assess an IELTS writing submission.
    
    Args:
        essay_text: The student's essay text
        task_prompt: The original task instruction
        task_type: Optional hint about task type (Academic Task 1, General Task 1, Task 2)
        
    Returns:
        Assessment results including scores and feedback
    """
    # Pre-processing
    word_count = count_words(essay_text)
    
    # Log basic information
    print(f"Processing essay with {word_count} words")
    
    # Construct the assessment prompt
    messages = construct_assessment_prompt(essay_text, task_prompt)
    
    # Add task type hint if provided
    if task_type:
        messages[1]["content"] += f"\n\nTask Type Hint: {task_type}"
    
    try:
        # Get assessment from OpenAI
        assessment_result = get_openai_response(messages)
        
        # Post-processing
        # Check if the response matches expected format
        if not all(key in assessment_result for key in ["task_type", "scores", "feedback"]):
            raise ValueError("Incomplete assessment response from OpenAI")
        
        # Add timestamp and metadata
        assessment_result["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
        assessment_result["word_count"] = word_count
        
        return assessment_result
    
    except Exception as e:
        # Error handling
        print(f"Assessment failed: {str(e)}")
        return {
            "error": True,
            "message": f"Assessment failed: {str(e)}",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

def format_assessment_for_display(assessment_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format the assessment results for user-friendly display.
    
    Args:
        assessment_result: The raw assessment result from OpenAI
        
    Returns:
        Formatted assessment for display to the user
    """
    if "error" in assessment_result:
        return {
            "display_title": "Assessment Error",
            "display_content": f"Sorry, we couldn't assess your writing: {assessment_result.get('message', 'Unknown error')}",
            "task_type": "Unknown",
            "overall_score": "N/A",
            "score_description": "Assessment not available",
            "criteria_scores": {
                "Task Achievement/Response": "N/A",
                "Coherence & Cohesion": "N/A",
                "Lexical Resource": "N/A",
                "Grammatical Range & Accuracy": "N/A"
            },
            "word_count": assessment_result.get("word_count", 0),
            "meets_requirement": False,
            "strengths": [],
            "improvements": [],
            "summary": "The assessment couldn't be completed. Please check your OpenAI API key configuration or try again later."
        }
    
    # Format overall score with appropriate band description
    overall_score = assessment_result["scores"]["overall"]
    score_description = get_band_description(overall_score)
    
    # Format the individual criteria scores
    criteria_scores = {
        "Task Achievement/Response": assessment_result["scores"].get("task_achievement", "N/A"),
        "Coherence & Cohesion": assessment_result["scores"].get("coherence_cohesion", "N/A"),
        "Lexical Resource": assessment_result["scores"].get("lexical_resource", "N/A"),
        "Grammatical Range & Accuracy": assessment_result["scores"].get("grammatical_range", "N/A")
    }
    
    # Format strengths and improvements
    strengths = assessment_result["feedback"]["strengths"]
    improvements = assessment_result["feedback"]["areas_for_improvement"]
    
    # Create the formatted output
    formatted_result = {
        "display_title": f"IELTS Writing Assessment - Band {overall_score}",
        "task_type": assessment_result["task_type"],
        "overall_score": overall_score,
        "score_description": score_description,
        "criteria_scores": criteria_scores,
        "word_count": assessment_result["word_count"],
        "meets_requirement": assessment_result.get("meets_word_count_requirement", False),
        "strengths": strengths,
        "improvements": improvements,
        "summary": assessment_result["feedback"]["summary"]
    }
    
    return formatted_result

def get_band_description(band_score: float) -> str:
    """
    Get a descriptive text for a given band score.
    
    Args:
        band_score: IELTS band score (1-9)
        
    Returns:
        Description of what the band score means
    """
    descriptions = {
        9: "Expert User: Complete mastery of English, appropriate, accurate, and fluent with full understanding.",
        8.5: "Very Good User: Fully operational command with only occasional unsystematic inaccuracies and misunderstandings.",
        8: "Very Good User: Fully operational command with only occasional unsystematic inaccuracies and misunderstandings.",
        7.5: "Good User: Operational command with occasional inaccuracies and misunderstandings in unfamiliar situations.",
        7: "Good User: Operational command with occasional inaccuracies and misunderstandings in unfamiliar situations.",
        6.5: "Competent User: Generally effective command with some inaccuracies and misunderstandings.",
        6: "Competent User: Generally effective command with some inaccuracies and misunderstandings.",
        5.5: "Modest User: Partial command with frequent problems in understanding and expression.",
        5: "Modest User: Partial command with frequent problems in understanding and expression.",
        4.5: "Limited User: Basic competence is limited to familiar situations with frequent problems.",
        4: "Limited User: Basic competence is limited to familiar situations with frequent problems.",
        3.5: "Extremely Limited User: Conveys and understands only general meaning in very familiar situations.",
        3: "Extremely Limited User: Conveys and understands only general meaning in very familiar situations.",
        2.5: "Intermittent User: Great difficulty understanding and communicating.",
        2: "Intermittent User: Great difficulty understanding and communicating.",
        1.5: "Non User: Essentially no ability to use the language beyond isolated words.",
        1: "Non User: Essentially no ability to use the language beyond isolated words.",
        0: "Did not attempt the test or impossible to assess."
    }
    
    return descriptions.get(band_score, "No description available for this band score.")

# Functions needed by routes.py 
def assess_writing_response(essay_text: str, task_prompt: str, task_type: str = None) -> Dict[str, Any]:
    """
    Alias for assess_writing to maintain compatibility with routes.py.
    """
    return assess_writing(essay_text, task_prompt, task_type)

def generate_writing_feedback(essay_text: str, task_prompt: str) -> Dict[str, Any]:
    """
    Generate detailed feedback for a writing submission without scoring.
    
    Args:
        essay_text: The student's essay text
        task_prompt: The original task instruction
        
    Returns:
        Detailed feedback dictionary
    """
    assessment = assess_writing(essay_text, task_prompt)
    # Return only the feedback portion
    if "error" in assessment:
        return assessment
    return {
        "feedback": assessment["feedback"],
        "timestamp": assessment.get("timestamp", time.strftime("%Y-%m-%d %H:%M:%S")),
        "word_count": assessment.get("word_count", count_words(essay_text))
    }

def generate_personalized_study_plan(assessment_result: Dict[str, Any], user_goals: str = None) -> Dict[str, Any]:
    """
    Generate a personalized study plan based on writing assessment results.
    
    Args:
        assessment_result: The assessment result from assess_writing
        user_goals: Optional string describing user's learning goals
        
    Returns:
        Study plan dictionary with recommendations
    """
    if "error" in assessment_result:
        return {
            "error": True,
            "message": "Cannot generate study plan from failed assessment",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    # Construct prompt for study plan generation
    messages = [
        {"role": "system", "content": "You are an expert IELTS writing tutor. Generate a personalized study plan based on the student's assessment results."},
        {"role": "user", "content": f"Create a personalized IELTS writing study plan based on these assessment results:\n\n{json.dumps(assessment_result, indent=2)}"}
    ]
    
    # Add user goals if provided
    if user_goals:
        messages[1]["content"] += f"\n\nStudent's goals: {user_goals}"
    
    try:
        # Get study plan from OpenAI
        study_plan_result = get_openai_response(messages)
        
        # Add timestamp
        study_plan_result["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        return study_plan_result
    
    except Exception as e:
        # Error handling
        print(f"Study plan generation failed: {str(e)}")
        return {
            "error": True,
            "message": f"Study plan generation failed: {str(e)}",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

def get_openai_models_list() -> List[str]:
    """
    Get the list of available OpenAI models.
    
    Returns:
        List of model names
    """
    # Check if we have initialized OpenAI client
    if not initialize_openai():
        # Return mock response if API key is not available
        return ["API key not available"]
    
    try:
        # Get available models
        models = client.models.list()
        return [model.id for model in models.data]
    except Exception as e:
        print(f"Error getting OpenAI models: {str(e)}")
        return ["Error getting models"]