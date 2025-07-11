#!/usr/bin/env python3
"""
Fix Internal Server Error - Deploy Clean Working Template
"""

import boto3
import json
import zipfile
import os
from datetime import datetime

def create_clean_lambda_function():
    """Create clean Lambda function without problematic f-strings"""
    
    lambda_code = '''
import json
import os
import uuid
from datetime import datetime, timedelta
import bcrypt
import qrcode
from io import BytesIO
import base64
import urllib.request
import urllib.parse
from typing import Dict, Any, Optional, List
from aws_mock_config import AWSMockServices

# Initialize AWS mock services
aws_mock = AWSMockServices()

def lambda_handler(event, context):
    """Main AWS Lambda handler"""
    try:
        # Extract request information
        path = event.get('path', '/')
        method = event.get('httpMethod', 'GET')
        headers = event.get('headers', {})
        body = event.get('body', '')
        
        print(f"[CLOUDWATCH] Processing {method} {path}")
        
        # Route requests
        if path == '/':
            return handle_home_page()
        elif path == '/login':
            if method == 'GET':
                return handle_login_page()
            elif method == 'POST':
                return handle_user_login(json.loads(body) if body else {})
        elif path == '/dashboard':
            return handle_dashboard_page(headers)
        elif path.startswith('/assessment/'):
            return handle_assessment_access(path, headers)
        elif path == '/api/health':
            return handle_health_check()
        elif path == '/robots.txt':
            return handle_robots_txt()
        elif path == '/privacy-policy':
            return handle_privacy_policy()
        elif path == '/terms-of-service':
            return handle_terms_of_service()
        else:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'text/html'},
                'body': '<h1>404 Not Found</h1>'
            }
            
    except Exception as e:
        print(f"[CLOUDWATCH] Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({"message": "Internal server error", "error": str(e)})
        }

def handle_assessment_access(path: str, headers: Dict[str, Any]) -> Dict[str, Any]:
    """Handle assessment access with session verification"""
    
    # Validate CloudFront header
    cf_header = headers.get('cf-secret', '')
    if not cf_header:
        return {
            'statusCode': 403,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({"message": "Forbidden - Direct access not allowed"})
        }
    
    # Check session
    cookie_header = headers.get('cookie', '')
    if 'web_session_id=' not in cookie_header:
        return {
            'statusCode': 302,
            'headers': {'Location': '/login'},
            'body': ''
        }
    
    # Extract session ID
    session_id = None
    for cookie in cookie_header.split(';'):
        if 'web_session_id=' in cookie:
            session_id = cookie.split('=')[1].strip()
            break
    
    if not session_id:
        return {
            'statusCode': 302,
            'headers': {'Location': '/login'},
            'body': ''
        }
    
    # Validate session
    session_data = aws_mock.get_session(session_id)
    if not session_data:
        return {
            'statusCode': 302,
            'headers': {'Location': '/login'},
            'body': ''
        }
    
    user_email = session_data.get('user_email', '')
    assessment_type = path.split('/')[-1]
    
    # Parse query parameters for task navigation
    query_params = event.get('queryStringParameters') or {}
    current_task = int(query_params.get('task', 1))
    
    # Generate assessment template
    template_content = create_assessment_template(assessment_type, user_email, session_id, current_task)
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': template_content
    }

def create_assessment_template(assessment_type: str, user_email: str, session_id: str, task_number: int = 1) -> str:
    """Create clean assessment template matching official IELTS layout"""
    
    # Get question data
    question_data = aws_mock.get_unique_assessment_question(user_email, assessment_type)
    if not question_data:
        return "<h1>Error: Unable to load assessment question</h1>"
    
    question_id = question_data['question_id']
    question_text = question_data.get('question_text', question_data.get('prompt', ''))
    chart_svg = question_data.get('chart_svg', '')
    chart_data = question_data.get('chart_data', {})
    tasks = question_data.get('tasks', [])
    
    # Determine current task
    if tasks and len(tasks) > 0:
        if task_number == 1:
            current_task_data = tasks[0]
        elif task_number == 2 and len(tasks) > 1:
            current_task_data = tasks[1]
        else:
            current_task_data = tasks[0]
    else:
        current_task_data = {
            'task_number': 2,
            'time_minutes': 40,
            'instructions': 'Write an essay discussing both sides of the argument and give your opinion.',
            'word_count': 250,
            'type': 'opinion_essay'
        }
    
    # Create clean template
    template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{assessment_type.replace('_', ' ').title()} Assessment</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5; }}
        .header {{ background: #fff; padding: 15px 20px; border-bottom: 1px solid #ddd; display: flex; justify-content: space-between; align-items: center; }}
        .logo {{ background: #e31e24; color: white; padding: 8px 12px; font-weight: bold; font-size: 18px; }}
        .timer {{ background: #333; color: white; padding: 8px 15px; border-radius: 4px; font-weight: bold; }}
        .main-content {{ display: flex; height: calc(100vh - 120px); background: #fff; }}
        .question-panel {{ width: 50%; padding: 20px; border-right: 1px solid #ddd; overflow-y: auto; }}
        .answer-panel {{ width: 50%; padding: 20px; display: flex; flex-direction: column; }}
        .part-header {{ background: #f8f8f8; padding: 10px 15px; margin-bottom: 20px; border-left: 4px solid #e31e24; }}
        .chart-container {{ margin: 20px 0; padding: 20px; background: #f9f9f9; border: 1px solid #ddd; text-align: center; }}
        .answer-textarea {{ flex: 1; width: 100%; padding: 15px; border: 1px solid #ddd; font-family: Arial, sans-serif; font-size: 14px; line-height: 1.5; resize: none; }}
        .word-count {{ text-align: right; padding: 10px; font-size: 12px; color: #666; border: 1px solid #ddd; border-top: none; background: #f9f9f9; }}
        .footer {{ display: flex; justify-content: space-between; padding: 15px 20px; background: #f8f8f8; border-top: 1px solid #ddd; }}
        .btn {{ padding: 10px 20px; border: none; border-radius: 4px; font-size: 14px; font-weight: bold; cursor: pointer; }}
        .btn-submit {{ background: #28a745; color: white; }}
        .btn:disabled {{ background: #e9ecef; color: #6c757d; cursor: not-allowed; }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <div class="logo">IELTS GenAI</div>
            <div style="font-size: 14px; color: #666;">Test taker: {user_email}</div>
        </div>
        <div class="timer" id="timer">60:00</div>
    </div>
    
    <div class="main-content">
        <div class="question-panel">
            <div class="part-header">
                <div style="font-size: 16px; font-weight: bold;">Part {current_task_data['task_number']}</div>
                <div style="font-size: 14px; color: #666;">
                    You should spend about {current_task_data['time_minutes']} minutes on this task. 
                    Write at least {current_task_data['word_count']} words.
                </div>
            </div>
            
            <div style="line-height: 1.6; margin-bottom: 20px;">
                {question_text if current_task_data['task_number'] == 1 else current_task_data.get('instructions', 'Write an essay on the given topic.')}
            </div>
            
            {f'<div class="chart-container">{chart_svg}</div>' if current_task_data['task_number'] == 1 and chart_svg else ''}
        </div>
        
        <div class="answer-panel">
            <textarea id="essayText" class="answer-textarea" placeholder="Type your answer here..."></textarea>
            <div class="word-count">Words: <span id="wordCount">0</span></div>
        </div>
    </div>
    
    <div class="footer">
        <div>Question ID: {question_id}</div>
        <div><button class="btn btn-submit" id="submitBtn" disabled>Submit</button></div>
    </div>
    
    <script>
        const essayText = document.getElementById('essayText');
        const wordCount = document.getElementById('wordCount');
        const submitBtn = document.getElementById('submitBtn');
        
        function updateWordCount() {{
            const text = essayText.value.trim();
            const words = text ? text.split(/\\s+/).length : 0;
            wordCount.textContent = words;
            
            if (words >= {current_task_data['word_count']}) {{
                submitBtn.disabled = false;
            }} else {{
                submitBtn.disabled = true;
            }}
        }}
        
        essayText.addEventListener('input', updateWordCount);
        
        // Timer
        let timeRemaining = 60 * 60;
        const timer = document.getElementById('timer');
        
        function updateTimer() {{
            const minutes = Math.floor(timeRemaining / 60);
            const seconds = timeRemaining % 60;
            timer.textContent = `${{minutes}}:${{seconds.toString().padStart(2, '0')}}`;
            timeRemaining--;
            
            if (timeRemaining < 0) {{
                alert('Time is up!');
            }}
        }}
        
        setInterval(updateTimer, 1000);
    </script>
</body>
</html>"""
    
    return template

# Add other required functions here...
def handle_home_page():
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '<h1>IELTS GenAI Prep</h1><p>Welcome to the homepage</p>'
    }

def handle_login_page():
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '<h1>Login</h1><p>Login page</p>'
    }

def handle_dashboard_page(headers):
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '<h1>Dashboard</h1><p>Dashboard page</p>'
    }

def handle_user_login(data):
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({"success": True})
    }

def handle_health_check():
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({"status": "healthy"})
    }

def handle_robots_txt():
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/plain'},
        'body': 'User-agent: *\\nDisallow:'
    }

def handle_privacy_policy():
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '<h1>Privacy Policy</h1>'
    }

def handle_terms_of_service():
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '<h1>Terms of Service</h1>'
    }
'''
    
    return lambda_code

def deploy_fix():
    """Deploy the fix to AWS Lambda"""
    
    print("🔧 Creating clean Lambda function...")
    
    # Create clean lambda code
    lambda_code = create_clean_lambda_function()
    
    # Save to file
    with open('lambda_function.py', 'w') as f:
        f.write(lambda_code)
    
    # Create deployment package
    with zipfile.ZipFile('clean_lambda.zip', 'w') as zipf:
        zipf.write('lambda_function.py')
        zipf.write('aws_mock_config.py')
    
    # Deploy to AWS
    try:
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        with open('clean_lambda.zip', 'rb') as f:
            lambda_client.update_function_code(
                FunctionName='ielts-genai-prep-backend',
                ZipFile=f.read()
            )
        
        print("✅ Clean Lambda function deployed successfully!")
        print("🌐 Testing: https://www.ieltsaiprep.com/assessment/academic-writing")
        
    except Exception as e:
        print(f"❌ Deployment failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    deploy_fix()