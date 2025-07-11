"""
Fix Assessment Questions - Add Proper Chart Data and Images
"""

import boto3
import json
from datetime import datetime

def create_proper_academic_writing_questions():
    """Create proper academic writing questions with embedded chart data"""
    
    questions = [
        {
            "question_id": "academic-writing_q1",
            "assessment_type": "academic_writing",
            "question_text": "The chart below shows the percentage of households in different income brackets in City X from 2010 to 2020.",
            "chart_type": "bar_chart",
            "chart_data": {
                "title": "Household Income Distribution in City X (2010-2020)",
                "data": [
                    {"year": "2010", "low_income": 35, "middle_income": 45, "high_income": 20},
                    {"year": "2015", "low_income": 30, "middle_income": 50, "high_income": 20},
                    {"year": "2020", "low_income": 25, "middle_income": 55, "high_income": 20}
                ],
                "x_axis": "Year",
                "y_axis": "Percentage of Households"
            },
            "chart_svg": '''<svg width="600" height="400" viewBox="0 0 600 400" xmlns="http://www.w3.org/2000/svg">
                <rect width="600" height="400" fill="#f9f9f9" stroke="#ddd"/>
                <text x="300" y="25" text-anchor="middle" font-size="16" font-weight="bold">Household Income Distribution in City X (2010-2020)</text>
                
                <!-- 2010 Data -->
                <rect x="80" y="320" width="40" height="70" fill="#e74c3c" opacity="0.8"/>
                <rect x="80" y="250" width="40" height="90" fill="#3498db" opacity="0.8"/>
                <rect x="80" y="210" width="40" height="40" fill="#2ecc71" opacity="0.8"/>
                
                <!-- 2015 Data -->
                <rect x="200" y="330" width="40" height="60" fill="#e74c3c" opacity="0.8"/>
                <rect x="200" y="230" width="40" height="100" fill="#3498db" opacity="0.8"/>
                <rect x="200" y="190" width="40" height="40" fill="#2ecc71" opacity="0.8"/>
                
                <!-- 2020 Data -->
                <rect x="320" y="340" width="40" height="50" fill="#e74c3c" opacity="0.8"/>
                <rect x="320" y="230" width="40" height="110" fill="#3498db" opacity="0.8"/>
                <rect x="320" y="190" width="40" height="40" fill="#2ecc71" opacity="0.8"/>
                
                <!-- Labels -->
                <text x="100" y="375" text-anchor="middle" font-size="12">2010</text>
                <text x="220" y="375" text-anchor="middle" font-size="12">2015</text>
                <text x="340" y="375" text-anchor="middle" font-size="12">2020</text>
                
                <!-- Legend -->
                <rect x="450" y="200" width="15" height="15" fill="#e74c3c"/>
                <text x="475" y="212" font-size="12">Low Income (Below $40k)</text>
                <rect x="450" y="220" width="15" height="15" fill="#3498db"/>
                <text x="475" y="232" font-size="12">Middle Income ($40k-$80k)</text>
                <rect x="450" y="240" width="15" height="15" fill="#2ecc71"/>
                <text x="475" y="252" font-size="12">High Income (Above $80k)</text>
                
                <!-- Y-axis labels -->
                <text x="70" y="200" text-anchor="end" font-size="10">60%</text>
                <text x="70" y="240" text-anchor="end" font-size="10">40%</text>
                <text x="70" y="280" text-anchor="end" font-size="10">20%</text>
                <text x="70" y="320" text-anchor="end" font-size="10">0%</text>
            </svg>''',
            "tasks": [
                {
                    "task_number": 1,
                    "time_minutes": 20,
                    "instructions": "Summarize the information by selecting and reporting the main features, and make comparisons where relevant.",
                    "word_count": 150,
                    "type": "data_description"
                },
                {
                    "task_number": 2,
                    "time_minutes": 40,
                    "instructions": "Some people believe that technology has made our lives more complex, while others argue that it has simplified daily tasks. Discuss both views and give your own opinion.",
                    "word_count": 250,
                    "type": "opinion_essay"
                }
            ],
            "created_at": datetime.now().isoformat()
        },
        {
            "question_id": "academic-writing_q2",
            "assessment_type": "academic_writing",
            "question_text": "The line graph below shows the consumption of three types of energy sources in a country from 1980 to 2020.",
            "chart_type": "line_graph",
            "chart_data": {
                "title": "Energy Consumption by Source (1980-2020)",
                "data": [
                    {"year": 1980, "coal": 60, "oil": 30, "renewable": 10},
                    {"year": 1990, "coal": 55, "oil": 35, "renewable": 10},
                    {"year": 2000, "coal": 45, "oil": 40, "renewable": 15},
                    {"year": 2010, "coal": 35, "oil": 40, "renewable": 25},
                    {"year": 2020, "coal": 25, "oil": 35, "renewable": 40}
                ]
            },
            "chart_svg": '''<svg width="600" height="400" viewBox="0 0 600 400" xmlns="http://www.w3.org/2000/svg">
                <rect width="600" height="400" fill="#f9f9f9" stroke="#ddd"/>
                <text x="300" y="25" text-anchor="middle" font-size="16" font-weight="bold">Energy Consumption by Source (1980-2020)</text>
                
                <!-- Grid lines -->
                <line x1="80" y1="60" x2="80" y2="320" stroke="#ccc" stroke-width="1"/>
                <line x1="80" y1="320" x2="520" y2="320" stroke="#ccc" stroke-width="1"/>
                
                <!-- Coal line (red) -->
                <polyline points="80,140 170,150 260,170 350,210 440,250" fill="none" stroke="#e74c3c" stroke-width="3"/>
                
                <!-- Oil line (blue) -->
                <polyline points="80,200 170,180 260,160 350,160 440,180" fill="none" stroke="#3498db" stroke-width="3"/>
                
                <!-- Renewable line (green) -->
                <polyline points="80,290 170,290 260,270 350,220 440,120" fill="none" stroke="#2ecc71" stroke-width="3"/>
                
                <!-- Data points -->
                <circle cx="80" cy="140" r="4" fill="#e74c3c"/>
                <circle cx="170" cy="150" r="4" fill="#e74c3c"/>
                <circle cx="260" cy="170" r="4" fill="#e74c3c"/>
                <circle cx="350" cy="210" r="4" fill="#e74c3c"/>
                <circle cx="440" cy="250" r="4" fill="#e74c3c"/>
                
                <!-- X-axis labels -->
                <text x="80" y="340" text-anchor="middle" font-size="12">1980</text>
                <text x="170" y="340" text-anchor="middle" font-size="12">1990</text>
                <text x="260" y="340" text-anchor="middle" font-size="12">2000</text>
                <text x="350" y="340" text-anchor="middle" font-size="12">2010</text>
                <text x="440" y="340" text-anchor="middle" font-size="12">2020</text>
                
                <!-- Y-axis labels -->
                <text x="70" y="120" text-anchor="end" font-size="10">60%</text>
                <text x="70" y="160" text-anchor="end" font-size="10">40%</text>
                <text x="70" y="200" text-anchor="end" font-size="10">30%</text>
                <text x="70" y="240" text-anchor="end" font-size="10">20%</text>
                <text x="70" y="280" text-anchor="end" font-size="10">10%</text>
                <text x="70" y="320" text-anchor="end" font-size="10">0%</text>
                
                <!-- Legend -->
                <line x1="450" y1="80" x2="470" y2="80" stroke="#e74c3c" stroke-width="3"/>
                <text x="480" y="85" font-size="12">Coal</text>
                <line x1="450" y1="100" x2="470" y2="100" stroke="#3498db" stroke-width="3"/>
                <text x="480" y="105" font-size="12">Oil</text>
                <line x1="450" y1="120" x2="470" y2="120" stroke="#2ecc71" stroke-width="3"/>
                <text x="480" y="125" font-size="12">Renewable</text>
            </svg>''',
            "tasks": [
                {
                    "task_number": 1,
                    "time_minutes": 20,
                    "instructions": "Summarize the information by selecting and reporting the main features, and make comparisons where relevant.",
                    "word_count": 150,
                    "type": "data_description"
                },
                {
                    "task_number": 2,
                    "time_minutes": 40,
                    "instructions": "Environmental protection is the responsibility of politicians, not individuals, as individuals can do too little. To what extent do you agree or disagree with this statement?",
                    "word_count": 250,
                    "type": "opinion_essay"
                }
            ],
            "created_at": datetime.now().isoformat()
        }
    ]
    
    return questions

def update_dynamodb_questions():
    """Update DynamoDB with questions that include chart data"""
    
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('ielts-assessment-questions')
    
    questions = create_proper_academic_writing_questions()
    
    for question in questions:
        try:
            table.put_item(Item=question)
            print(f"✅ Updated question: {question['question_id']}")
        except Exception as e:
            print(f"❌ Error updating {question['question_id']}: {e}")
    
    print(f"\n🎯 Updated {len(questions)} academic writing questions with proper chart data")

def main():
    """Main function"""
    
    print("📊 Fixing Assessment Questions - Adding Chart Data")
    print("=" * 50)
    
    update_dynamodb_questions()
    
    print("\n✅ Assessment questions updated!")
    print("Charts should now display properly in the assessment pages")
    print("\nTest the updated questions at:")
    print("https://www.ieltsaiprep.com/assessment/academic-writing")

if __name__ == "__main__":
    main()