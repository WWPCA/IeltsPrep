"""
Update the writing assessment to use AWS Nova Micro instead of OpenAI.
This script creates a new writing assessment module that uses AWS Bedrock's Nova Micro model.
"""
import os

def create_nova_writing_assessment():
    """Create a new writing assessment module using AWS Nova Micro."""
    
    # Path to the new file
    new_file = 'nova_writing_assessment.py'
    
    # Create the new file content
    content = """\"\"\"
IELTS Writing Assessment using AWS Nova Micro model.
This module provides functions to evaluate IELTS writing responses with AWS Bedrock.
\"\"\"
import os
import json
import logging
from aws_bedrock_services import evaluate_writing_with_nova_micro

logger = logging.getLogger(__name__)

def assess_writing_response(essay_text, prompt_text, essay_type):
    \"\"\"
    Assess an IELTS writing response using AWS Nova Micro.
    
    Args:
        essay_text (str): The student's essay to evaluate
        prompt_text (str): The original writing prompt
        essay_type (str): "task1" or "task2" to indicate the essay type
        
    Returns:
        dict: Assessment results including scores and feedback
    \"\"\"
    try:
        # Call the Nova Micro assessment function
        assessment_result = evaluate_writing_with_nova_micro(essay_text, prompt_text, essay_type)
        return assessment_result
    except Exception as e:
        logger.error(f"Error assessing writing with Nova Micro: {str(e)}")
        logger.info("Falling back to OpenAI assessment...")
        
        # Fall back to OpenAI if Nova Micro fails
        try:
            from openai_writing_assessment import assess_writing_response as openai_assess
            return openai_assess(essay_text, prompt_text, essay_type)
        except Exception as fallback_error:
            logger.error(f"Fallback to OpenAI also failed: {str(fallback_error)}")
            # Return a basic error response
            return {
                "criteria_scores": {},
                "overall_score": 0,
                "detailed_feedback": {
                    "error": f"Assessment failed: {str(e)}"
                },
                "summary_feedback": "An error occurred during assessment."
            }
"""
    
    # Write the new file
    try:
        with open(new_file, 'w') as f:
            f.write(content)
        print(f"Successfully created {new_file}")
    except Exception as e:
        print(f"Error creating file: {str(e)}")
        return False
    
    # Now update the writing assessment routes to use the new module
    routes_file = 'writing_assessment_routes.py'
    
    try:
        with open(routes_file, 'r') as f:
            routes_content = f.read()
    except FileNotFoundError:
        print(f"Error: {routes_file} not found.")
        return False
    
    # Create a backup of the original routes file
    backup_file = f'{routes_file}.bak'
    try:
        with open(backup_file, 'w') as f:
            f.write(routes_content)
        print(f"Created backup at {backup_file}")
    except Exception as e:
        print(f"Error creating backup: {str(e)}")
        return False
    
    # Replace the import statement for assessment module
    original_import = "from openai_writing_assessment import assess_writing_response"
    new_import = "from nova_writing_assessment import assess_writing_response"
    
    # Only replace if the original import exists
    if original_import in routes_content:
        new_routes_content = routes_content.replace(original_import, new_import)
        
        # Write the updated content back to the file
        try:
            with open(routes_file, 'w') as f:
                f.write(new_routes_content)
            print(f"Successfully updated {routes_file} to use AWS Nova Micro for writing assessment.")
            return True
        except Exception as e:
            print(f"Error writing updated file: {str(e)}")
            return False
    else:
        print(f"Warning: Could not find '{original_import}' in {routes_file}.")
        print("Please manually update the import statement to use nova_writing_assessment.")
        return False

if __name__ == "__main__":
    create_nova_writing_assessment()