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
    
    # Academic Task 1 example
    academic_task1_prompt = "The chart below shows the percentage of people living in urban areas in different parts of the world. Summarize the information by selecting and reporting the main features, and make comparisons where relevant."
    academic_task1_response = """
    The bar graph illustrates the percentage of urban population across various regions globally. Overall, North America has the highest urbanization rate, while Africa has the lowest.
    
    According to the graph, North America leads with approximately 82% of its population residing in urban areas. Europe follows closely with around 75% urbanization. In contrast, Africa has the lowest urban population percentage at just about 40%.
    
    Asia and South America show moderate levels of urbanization, with roughly 48% and 65% of their populations living in urban settings respectively. Oceania falls between these regions at approximately 70%.
    
    The disparity between North America and Africa is particularly striking, with a difference of about 42 percentage points separating their urbanization rates. This likely reflects significant differences in economic development, infrastructure, and historical settlement patterns between the two continents.
    
    These figures highlight the varying degrees of urbanization across global regions, with more economically developed parts generally showing higher percentages of urban dwellers.
    """
    
    # General Task 1 example
    general_task1_prompt = "You have a problem with a piece of equipment you bought recently. Write a letter to the shop manager. In your letter explain what equipment you bought, describe the problem, say what action you would like the manager to take."
    general_task1_response = """
    Dear Sir/Madam,
    
    I am writing to express my dissatisfaction with a laptop I purchased from your store, TechWorld, located at 123 Main Street, on 15 April 2025.
    
    The laptop in question is a GalaxyBook Pro, which cost $1,200. According to your advertisement, this model was supposed to have 16GB of RAM and 512GB of storage. However, after using it for a few days, I noticed that the system was running unusually slow. Upon checking the specifications through the system information, I discovered that the laptop only has 8GB of RAM and 256GB of storage.
    
    Additionally, the battery life is far below what was advertised. The specification claimed 12 hours of battery life, but in reality, it barely lasts 4 hours even with minimal usage. This is particularly problematic as I purchased this laptop specifically for work purposes when I'm away from power sources.
    
    Given these significant discrepancies between the advertised specifications and the actual product, I would like a full replacement with a laptop that meets the specifications I paid for. Alternatively, I would accept a full refund so that I can purchase the correct model elsewhere.
    
    I have attached the receipt and warranty information with this letter. I expect to hear from you within the next seven days regarding this matter.
    
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