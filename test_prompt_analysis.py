"""
Test the updated Nova writing assessment with prompt analysis.
"""
import json
import os
import sys

from nova_writing_assessment import analyze_writing_response

def test_prompt_analysis():
    """Test the enhanced writing assessment with prompt analysis."""
    print("Testing the writing assessment with enhanced prompt analysis...")
    
    # Academic Task 1 example - short version for quick testing
    academic_task1_prompt = "The chart below shows the percentage of people living in urban areas in different parts of the world. Summarize the information by selecting and reporting the main features, and make comparisons where relevant."
    academic_task1_response = """
    The bar graph shows urban population percentages across global regions. North America has the highest at 82%, followed by Europe at 75%. Africa has the lowest at 40%. 
    
    Asia and South America have moderate levels at 48% and 65% respectively. Oceania is at 70%. The significant 42% gap between North America and Africa reflects differences in economic development.
    """
    
    # General Task 1 example - shorter version for testing
    general_task1_prompt = "You have a problem with a piece of equipment you bought recently. Write a letter to the shop manager. In your letter explain what equipment you bought, describe the problem, say what action you would like the manager to take."
    general_task1_response = """
    Dear Sir/Madam,
    
    I am writing about a laptop I purchased from your store on April 15, 2025.
    
    The GalaxyBook Pro cost $1,200 but has only 8GB RAM and 256GB storage instead of the advertised 16GB and 512GB. The battery lasts only 4 hours, not 12 as claimed.
    
    I request a full replacement with the correct specifications or a complete refund.
    
    Yours faithfully,
    John Smith
    """
    
    # Test Academic Task 1 assessment
    academic_result = analyze_writing_response(
        academic_task1_response,
        academic_task1_prompt,
        task_type="task1",
        test_type="academic"
    )
    
    print("\nAcademic Task 1 Assessment Result:")
    print(f"Overall Score: {academic_result.get('overall_score')}")
    
    if 'prompt_analysis' in academic_result:
        print("\nPrompt Analysis:")
        print(f"Score: {academic_result['prompt_analysis'].get('score')}/10")
        print(f"Explanation: {academic_result['prompt_analysis'].get('explanation')[:200]}...")
    else:
        print("\nNo prompt analysis returned for Academic Task 1")
    
    # Test General Task 1 assessment
    general_result = analyze_writing_response(
        general_task1_response,
        general_task1_prompt,
        task_type="task1",
        test_type="general"
    )
    
    print("\nGeneral Task 1 Assessment Result:")
    print(f"Overall Score: {general_result.get('overall_score')}")
    
    if 'prompt_analysis' in general_result:
        print("\nPrompt Analysis:")
        print(f"Score: {general_result['prompt_analysis'].get('score')}/10")
        print(f"Explanation: {general_result['prompt_analysis'].get('explanation')[:200]}...")
    else:
        print("\nNo prompt analysis returned for General Task 1")

if __name__ == "__main__":
    test_prompt_analysis()