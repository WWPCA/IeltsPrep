#!/usr/bin/env python3
"""
Minimal Working Template - Fix Internal Server Error
Creates a clean assessment template matching official IELTS layout
"""

import boto3
import json
import zipfile

def create_minimal_assessment_template():
    """Create minimal working assessment template"""
    
    lambda_code = '''
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

# Mock test data
MOCK_QUESTIONS = {
    "academic_writing": {
        "question_id": "aw_001",
        "question_text": "The chart below shows the percentage of households in owned and rented accommodation in England and Wales between 1918 and 2011.",
        "chart_svg": """<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
            <rect width="400" height="300" fill="#f9f9f9" stroke="#ddd"/>
            <text x="200" y="30" text-anchor="middle" font-family="Arial" font-size="16" font-weight="bold">Household Accommodation 1918-2011</text>
            <text x="200" y="60" text-anchor="middle" font-family="Arial" font-size="12">Percentage of households</text>
            <line x1="50" y1="250" x2="350" y2="250" stroke="#333" stroke-width="2"/>
            <line x1="50" y1="250" x2="50" y2="100" stroke="#333" stroke-width="2"/>
            <rect x="80" y="150" width="30" height="100" fill="#e31e24"/>
            <rect x="120" y="180" width="30" height="70" fill="#0066cc"/>
            <rect x="200" y="120" width="30" height="130" fill="#e31e24"/>
            <rect x="240" y="200" width="30" height="50" fill="#0066cc"/>
            <text x="200" y="280" text-anchor="middle" font-family="Arial" font-size="10">Sample Chart Data</text>
        </svg>""",
        "tasks": [
            {
                "task_number": 1,
                "time_minutes": 20,
                "instructions": "Summarize the information by selecting and reporting the main features, and make comparisons where relevant.",
                "word_count": 150
            }
        ]
    }
}

def lambda_handler(event, context):
    """Main AWS Lambda handler"""
    try:
        path = event.get("path", "/")
        method = event.get("httpMethod", "GET")
        
        if path == "/":
            return handle_home_page()
        elif path == "/assessment/academic-writing":
            return handle_assessment_page()
        elif path == "/api/health":
            return handle_health_check()
        else:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "text/html"},
                "body": "<h1>404 Not Found</h1>"
            }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }

def handle_home_page():
    """Handle home page"""
    html = """<!DOCTYPE html>
<html>
<head><title>IELTS GenAI Prep</title></head>
<body>
    <h1>IELTS GenAI Prep</h1>
    <p>AI-powered IELTS preparation platform</p>
    <a href="/assessment/academic-writing">Academic Writing Assessment</a>
</body>
</html>"""
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/html"},
        "body": html
    }

def handle_assessment_page():
    """Handle assessment page with official IELTS layout"""
    question_data = MOCK_QUESTIONS["academic_writing"]
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Academic Writing Assessment</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: Arial, sans-serif; background-color: #f5f5f5; }}
        .header {{ background-color: #fff; padding: 15px 20px; border-bottom: 1px solid #ddd; display: flex; justify-content: space-between; align-items: center; }}
        .logo {{ background-color: #e31e24; color: white; padding: 8px 12px; font-weight: bold; font-size: 18px; }}
        .timer {{ background-color: #333; color: white; padding: 8px 15px; border-radius: 4px; font-weight: bold; }}
        .main-content {{ display: flex; height: calc(100vh - 120px); background-color: #fff; }}
        .question-panel {{ width: 50%; padding: 20px; border-right: 1px solid #ddd; overflow-y: auto; }}
        .answer-panel {{ width: 50%; padding: 20px; display: flex; flex-direction: column; }}
        .part-header {{ background-color: #f8f8f8; padding: 10px 15px; margin-bottom: 20px; border-left: 4px solid #e31e24; }}
        .chart-container {{ margin: 20px 0; padding: 20px; background-color: #f9f9f9; border: 1px solid #ddd; text-align: center; }}
        .answer-textarea {{ flex: 1; width: 100%; padding: 15px; border: 1px solid #ddd; font-family: Arial, sans-serif; font-size: 14px; resize: none; }}
        .word-count {{ text-align: right; padding: 10px; font-size: 12px; color: #666; border: 1px solid #ddd; border-top: none; background-color: #f9f9f9; }}
        .footer {{ display: flex; justify-content: space-between; padding: 15px 20px; background-color: #f8f8f8; border-top: 1px solid #ddd; }}
        .btn {{ padding: 10px 20px; border: none; border-radius: 4px; font-size: 14px; font-weight: bold; cursor: pointer; }}
        .btn-submit {{ background-color: #28a745; color: white; }}
        .btn:disabled {{ background-color: #e9ecef; color: #6c757d; cursor: not-allowed; }}
        @media (max-width: 768px) {{
            .main-content {{ flex-direction: column; height: auto; }}
            .question-panel, .answer-panel {{ width: 100%; }}
            .question-panel {{ border-right: none; border-bottom: 1px solid #ddd; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <div class="logo">IELTS GenAI</div>
            <div style="font-size: 14px; color: #666;">Test taker: test@example.com</div>
        </div>
        <div class="timer" id="timer">20:00</div>
    </div>
    
    <div class="main-content">
        <div class="question-panel">
            <div class="part-header">
                <div style="font-size: 16px; font-weight: bold;">Part 1</div>
                <div style="font-size: 14px; color: #666;">
                    You should spend about 20 minutes on this task. 
                    Write at least 150 words.
                </div>
            </div>
            
            <div style="line-height: 1.6; margin-bottom: 20px;">
                {question_data["question_text"]}
            </div>
            
            <div class="chart-container">
                <div style="font-size: 14px; font-weight: bold; margin-bottom: 15px;">Household Accommodation 1918-2011</div>
                {question_data["chart_svg"]}
            </div>
        </div>
        
        <div class="answer-panel">
            <textarea id="essayText" class="answer-textarea" placeholder="Type your answer here..."></textarea>
            <div class="word-count">Words: <span id="wordCount">0</span></div>
        </div>
    </div>
    
    <div class="footer">
        <div>Question ID: {question_data["question_id"]}</div>
        <div><button class="btn btn-submit" id="submitBtn" disabled>Submit</button></div>
    </div>
    
    <script>
        const essayText = document.getElementById('essayText');
        const wordCount = document.getElementById('wordCount');
        const submitBtn = document.getElementById('submitBtn');
        const timer = document.getElementById('timer');
        
        let timeRemaining = 20 * 60;
        
        function updateWordCount() {{
            const text = essayText.value.trim();
            const words = text ? text.split(/\\s+/).length : 0;
            wordCount.textContent = words;
            
            if (words >= 150) {{
                submitBtn.disabled = false;
            }} else {{
                submitBtn.disabled = true;
            }}
        }}
        
        function updateTimer() {{
            const minutes = Math.floor(timeRemaining / 60);
            const seconds = timeRemaining % 60;
            timer.textContent = minutes + ':' + (seconds < 10 ? '0' : '') + seconds;
            
            if (timeRemaining <= 0) {{
                alert('Time is up!');
                return;
            }}
            
            timeRemaining--;
        }}
        
        essayText.addEventListener('input', updateWordCount);
        
        submitBtn.addEventListener('click', function() {{
            if (essayText.value.trim()) {{
                alert('Assessment submitted successfully!');
            }}
        }});
        
        setInterval(updateTimer, 1000);
        updateTimer();
    </script>
</body>
</html>"""
    
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/html"},
        "body": html
    }

def handle_health_check():
    """Handle health check"""
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"status": "healthy"})
    }
'''
    
    return lambda_code

def deploy_minimal_template():
    """Deploy the minimal template fix"""
    
    print("🚀 Deploying Minimal Template Fix")
    print("=" * 40)
    
    # Create lambda code
    lambda_code = create_minimal_assessment_template()
    
    # Write to file
    with open('lambda_function.py', 'w') as f:
        f.write(lambda_code)
    
    # Create deployment package
    with zipfile.ZipFile('minimal_lambda.zip', 'w') as zipf:
        zipf.write('lambda_function.py')
    
    # Deploy to AWS
    try:
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        with open('minimal_lambda.zip', 'rb') as f:
            lambda_client.update_function_code(
                FunctionName='ielts-genai-prep-api',
                ZipFile=f.read()
            )
        
        print("✅ Minimal template deployed successfully!")
        print("🌐 Testing website...")
        
        # Test the deployment
        import time
        time.sleep(3)
        
        try:
            import urllib.request
            response = urllib.request.urlopen('https://www.ieltsaiprep.com/assessment/academic-writing')
            status = response.getcode()
            content = response.read().decode('utf-8')
            
            if status == 200:
                print("✅ Website is working!")
                if 'Academic Writing Assessment' in content:
                    print("✅ Assessment page loads correctly!")
                    print("✅ Internal server error FIXED!")
                else:
                    print("⚠️ Page content needs verification")
            else:
                print(f"⚠️ Website returned status {status}")
                
        except Exception as e:
            print(f"⚠️ Test failed: {str(e)}")
        
    except Exception as e:
        print(f"❌ Deployment failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    deploy_minimal_template()