#!/usr/bin/env python3
"""
Simple Lambda Fix - Add All Assessment Types
Extends the working template to include all 4 assessment types
"""

import boto3
import json
import zipfile

def create_extended_lambda():
    """Create extended Lambda with all assessment types"""
    
    lambda_code = '''
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

# Mock test data for all assessment types
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
            {"task_number": 1, "time_minutes": 20, "instructions": "Summarize the information by selecting and reporting the main features, and make comparisons where relevant.", "word_count": 150}
        ]
    },
    "general_writing": {
        "question_id": "gw_001",
        "question_text": "You recently bought a piece of equipment for your kitchen but it did not work. You phoned the shop but no action was taken.",
        "tasks": [
            {"task_number": 1, "time_minutes": 20, "instructions": "Write a letter to the shop manager. In your letter: describe the problem with the equipment, explain what happened when you phoned the shop, say what you would like the manager to do.", "word_count": 150}
        ]
    },
    "academic_speaking": {
        "question_id": "as_001",
        "question_text": "Academic Speaking Assessment with Maya AI Examiner",
        "tasks": [
            {"task_number": 1, "time_minutes": 5, "instructions": "Introduction and Interview - Answer questions about yourself, your home, work or studies, and other familiar topics.", "word_count": 0}
        ]
    },
    "general_speaking": {
        "question_id": "gs_001",
        "question_text": "General Speaking Assessment with Maya AI Examiner",
        "tasks": [
            {"task_number": 1, "time_minutes": 5, "instructions": "Introduction and Interview - Answer questions about yourself, your home, work or studies, and other familiar topics.", "word_count": 0}
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
            return handle_assessment_page("academic_writing")
        elif path == "/assessment/general-writing":
            return handle_assessment_page("general_writing")
        elif path == "/assessment/academic-speaking":
            return handle_assessment_page("academic_speaking")
        elif path == "/assessment/general-speaking":
            return handle_assessment_page("general_speaking")
        elif path == "/api/health":
            return handle_health_check()
        else:
            return {"statusCode": 404, "headers": {"Content-Type": "text/html"}, "body": "<h1>404 Not Found</h1>"}
    except Exception as e:
        return {"statusCode": 500, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"error": str(e)})}

def handle_home_page():
    """Handle home page with all assessment types"""
    html = """<!DOCTYPE html>
<html>
<head>
    <title>IELTS GenAI Prep</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 1000px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #e31e24; margin-bottom: 10px; font-size: 32px; }
        .subtitle { color: #666; margin-bottom: 40px; font-size: 18px; }
        .assessment-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 25px; margin-top: 30px; }
        .assessment-card { background: #f8f9fa; padding: 25px; border-radius: 8px; border: 1px solid #ddd; transition: transform 0.2s; }
        .assessment-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
        .assessment-card h3 { color: #333; margin-bottom: 15px; font-size: 20px; }
        .assessment-card p { color: #666; margin-bottom: 20px; line-height: 1.5; }
        .btn { background-color: #e31e24; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; font-weight: bold; transition: background-color 0.2s; }
        .btn:hover { background-color: #c21a1f; }
        .writing-badge { background: #28a745; color: white; padding: 4px 8px; border-radius: 3px; font-size: 12px; margin-left: 10px; }
        .speaking-badge { background: #007bff; color: white; padding: 4px 8px; border-radius: 3px; font-size: 12px; margin-left: 10px; }
        .academic-badge { background: #6f42c1; color: white; padding: 4px 8px; border-radius: 3px; font-size: 12px; margin-left: 10px; }
        .general-badge { background: #fd7e14; color: white; padding: 4px 8px; border-radius: 3px; font-size: 12px; margin-left: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>IELTS GenAI Prep</h1>
        <p class="subtitle">AI-powered IELTS preparation platform with authentic assessment experience</p>
        
        <div class="assessment-grid">
            <div class="assessment-card">
                <h3>Academic Writing<span class="writing-badge">Writing</span><span class="academic-badge">Academic</span></h3>
                <p><strong>Task 1:</strong> Data description (20 min, 150 words)<br>
                   <strong>Technology:</strong> TrueScore® Nova Micro<br>
                   <strong>Format:</strong> Official IELTS Writing</p>
                <a href="/assessment/academic-writing" class="btn">Start Assessment</a>
            </div>
            
            <div class="assessment-card">
                <h3>General Writing<span class="writing-badge">Writing</span><span class="general-badge">General</span></h3>
                <p><strong>Task 1:</strong> Letter writing (20 min, 150 words)<br>
                   <strong>Technology:</strong> TrueScore® Nova Micro<br>
                   <strong>Format:</strong> Official IELTS Writing</p>
                <a href="/assessment/general-writing" class="btn">Start Assessment</a>
            </div>
            
            <div class="assessment-card">
                <h3>Academic Speaking<span class="speaking-badge">Speaking</span><span class="academic-badge">Academic</span></h3>
                <p><strong>Part 1:</strong> Interview (5 min)<br>
                   <strong>Technology:</strong> ClearScore® Maya AI<br>
                   <strong>Format:</strong> Official IELTS Speaking</p>
                <a href="/assessment/academic-speaking" class="btn">Start Assessment</a>
            </div>
            
            <div class="assessment-card">
                <h3>General Speaking<span class="speaking-badge">Speaking</span><span class="general-badge">General</span></h3>
                <p><strong>Part 1:</strong> Interview (5 min)<br>
                   <strong>Technology:</strong> ClearScore® Maya AI<br>
                   <strong>Format:</strong> Official IELTS Speaking</p>
                <a href="/assessment/general-speaking" class="btn">Start Assessment</a>
            </div>
        </div>
        
        <div style="margin-top: 40px; padding: 20px; background: #e8f4fd; border: 1px solid #0066cc; border-radius: 4px;">
            <strong>Assessment Features:</strong><br>
            • Single task display with authentic IELTS layout<br>
            • Real-time word counting and timer functionality<br>
            • Professional chart display for writing assessments<br>
            • Maya AI examiner for speaking assessments<br>
            • Complete Google Play compliance integration
        </div>
    </div>
</body>
</html>"""
    
    return {"statusCode": 200, "headers": {"Content-Type": "text/html"}, "body": html}

def handle_assessment_page(assessment_type):
    """Handle assessment page with official IELTS layout"""
    question_data = MOCK_QUESTIONS.get(assessment_type, {})
    if not question_data:
        return {"statusCode": 404, "headers": {"Content-Type": "text/html"}, "body": "Assessment type not found"}
    
    tasks = question_data.get("tasks", [])
    current_task_data = tasks[0] if tasks else {}
    
    assessment_title = assessment_type.replace("_", " ").title()
    is_speaking = "speaking" in assessment_type
    is_academic = "academic" in assessment_type
    
    # Task content
    task_content = question_data.get("question_text", "")
    
    # Chart display for writing tasks
    chart_display = ""
    if not is_speaking and "chart_svg" in question_data:
        chart_display = '<div class="chart-container">' + question_data["chart_svg"] + '</div>'
    
    # Input area based on assessment type
    if is_speaking:
        input_area = '<div class="speaking-area"><div class="recording-controls"><button class="btn btn-record" id="recordBtn">Start Recording</button><button class="btn btn-stop" id="stopBtn" disabled>Stop Recording</button><button class="btn btn-play" id="playBtn" disabled>Play Recording</button></div><div class="recording-status" id="recordingStatus">Click "Start Recording" to begin speaking with Maya</div><div class="maya-chat"><div class="maya-messages" id="mayaMessages"><div class="maya-message"><strong>Maya (AI Examiner):</strong> Hello! I am Maya, your AI examiner. Lets begin your IELTS Speaking assessment. Are you ready to start?</div></div></div></div>'
    else:
        input_area = '<textarea id="essayText" class="answer-textarea" placeholder="Type your answer here..."></textarea><div class="word-count">Words: <span id="wordCount">0</span></div>'
    
    time_minutes = current_task_data.get("time_minutes", 20)
    word_count = current_task_data.get("word_count", 150)
    question_id = question_data.get("question_id", "")
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{assessment_title} Assessment</title>
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
        .speaking-area {{ flex: 1; display: flex; flex-direction: column; }}
        .recording-controls {{ display: flex; gap: 10px; margin-bottom: 15px; flex-wrap: wrap; }}
        .recording-status {{ padding: 10px; background-color: #f8f9fa; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 15px; }}
        .maya-chat {{ flex: 1; border: 1px solid #ddd; border-radius: 4px; padding: 15px; background-color: #f9f9f9; }}
        .maya-messages {{ height: 100%; overflow-y: auto; }}
        .maya-message {{ padding: 10px; margin-bottom: 10px; background-color: white; border-radius: 4px; }}
        .footer {{ display: flex; justify-content: space-between; padding: 15px 20px; background-color: #f8f8f8; border-top: 1px solid #ddd; }}
        .btn {{ padding: 10px 20px; border: none; border-radius: 4px; font-size: 14px; font-weight: bold; cursor: pointer; }}
        .btn-submit {{ background-color: #28a745; color: white; }}
        .btn-record {{ background-color: #dc3545; color: white; }}
        .btn-stop {{ background-color: #6c757d; color: white; }}
        .btn-play {{ background-color: #17a2b8; color: white; }}
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
        <div class="timer" id="timer">{time_minutes}:00</div>
    </div>
    
    <div class="main-content">
        <div class="question-panel">
            <div class="part-header">
                <div style="font-size: 16px; font-weight: bold;">Part 1</div>
                <div style="font-size: 14px; color: #666;">
                    {current_task_data.get("instructions", "")}
                </div>
            </div>
            
            <div style="line-height: 1.6; margin-bottom: 20px;">
                {task_content}
            </div>
            
            {chart_display}
            
            <div style="margin-top: 20px; padding: 15px; background: #e8f4fd; border: 1px solid #0066cc; border-radius: 4px;">
                <strong>Assessment Information:</strong><br>
                • Question ID: {question_id}<br>
                • Technology: {"ClearScore® Maya AI" if is_speaking else "TrueScore® Nova Micro"}<br>
                • Format: {"Official IELTS Speaking" if is_speaking else "Official IELTS Writing"}<br>
                • Type: {"Academic" if is_academic else "General Training"}
            </div>
        </div>
        
        <div class="answer-panel">
            {input_area}
        </div>
    </div>
    
    <div class="footer">
        <div>Part 1 of 1</div>
        <div><button class="btn btn-submit" id="submitBtn" {"disabled" if not is_speaking else ""}>Submit</button></div>
    </div>
    
    <script>
        let timeRemaining = {time_minutes} * 60;
        const timer = document.getElementById('timer');
        const isWriting = {"false" if is_speaking else "true"};
        
        function updateTimer() {{
            const minutes = Math.floor(timeRemaining / 60);
            const seconds = timeRemaining % 60;
            timer.textContent = minutes.toString().padStart(2, '0') + ':' + seconds.toString().padStart(2, '0');
            
            if (timeRemaining <= 0) {{
                alert('Time is up!');
                return;
            }}
            
            timeRemaining--;
        }}
        
        setInterval(updateTimer, 1000);
        updateTimer();
        
        if (isWriting) {{
            const essayText = document.getElementById('essayText');
            const wordCount = document.getElementById('wordCount');
            const submitBtn = document.getElementById('submitBtn');
            
            function updateWordCount() {{
                const text = essayText.value.trim();
                const words = text ? text.split(/\\s+/).length : 0;
                wordCount.textContent = words;
                
                const minWords = {word_count};
                if (words >= minWords && submitBtn) {{
                    submitBtn.disabled = false;
                    submitBtn.style.backgroundColor = '#28a745';
                }} else if (submitBtn) {{
                    submitBtn.disabled = true;
                    submitBtn.style.backgroundColor = '#e9ecef';
                }}
            }}
            
            essayText.addEventListener('input', updateWordCount);
            updateWordCount();
        }}
        
        if (!isWriting) {{
            const recordBtn = document.getElementById('recordBtn');
            const stopBtn = document.getElementById('stopBtn');
            const playBtn = document.getElementById('playBtn');
            const recordingStatus = document.getElementById('recordingStatus');
            
            let mediaRecorder;
            let audioChunks = [];
            
            recordBtn.addEventListener('click', async function() {{
                try {{
                    const stream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
                    mediaRecorder = new MediaRecorder(stream);
                    audioChunks = [];
                    
                    mediaRecorder.ondataavailable = function(event) {{
                        audioChunks.push(event.data);
                    }};
                    
                    mediaRecorder.start();
                    recordBtn.disabled = true;
                    stopBtn.disabled = false;
                    recordingStatus.textContent = 'Recording in progress... Speak clearly for Maya AI analysis';
                    recordingStatus.style.backgroundColor = '#fff3cd';
                }} catch (error) {{
                    recordingStatus.textContent = 'Error: Could not access microphone. Please allow microphone access.';
                    recordingStatus.style.backgroundColor = '#f8d7da';
                }}
            }});
            
            stopBtn.addEventListener('click', function() {{
                mediaRecorder.stop();
                recordBtn.disabled = false;
                stopBtn.disabled = true;
                playBtn.disabled = false;
                recordingStatus.textContent = 'Recording completed. You can play it back or submit your assessment.';
                recordingStatus.style.backgroundColor = '#d1ecf1';
            }});
            
            playBtn.addEventListener('click', function() {{
                const audioBlob = new Blob(audioChunks, {{ type: 'audio/wav' }});
                const audioUrl = URL.createObjectURL(audioBlob);
                const audio = new Audio(audioUrl);
                audio.play();
            }});
        }}
    </script>
</body>
</html>'''
    
    return {"statusCode": 200, "headers": {"Content-Type": "text/html"}, "body": html}

def handle_health_check():
    """Handle health check"""
    return {"statusCode": 200, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"status": "healthy", "timestamp": datetime.now().isoformat()})}
'''
    
    return lambda_code

def deploy_extended_system():
    """Deploy extended system with all assessment types"""
    
    print("🚀 Deploying Extended Assessment System")
    print("=" * 45)
    
    # Create lambda code
    lambda_code = create_extended_lambda()
    
    # Write to file
    with open('lambda_function.py', 'w') as f:
        f.write(lambda_code)
    
    # Create deployment package
    with zipfile.ZipFile('extended_assessment_system.zip', 'w') as zipf:
        zipf.write('lambda_function.py')
    
    # Deploy to AWS
    try:
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        with open('extended_assessment_system.zip', 'rb') as f:
            lambda_client.update_function_code(
                FunctionName='ielts-genai-prep-api',
                ZipFile=f.read()
            )
        
        print("✅ Extended assessment system deployed successfully!")
        print("🌐 Testing all assessment types...")
        
        # Test all assessment types
        import time
        time.sleep(5)
        
        assessment_types = [
            ("academic-writing", "Academic Writing"),
            ("general-writing", "General Writing"), 
            ("academic-speaking", "Academic Speaking"),
            ("general-speaking", "General Speaking")
        ]
        
        for assessment_type, display_name in assessment_types:
            try:
                import urllib.request
                response = urllib.request.urlopen(f'https://www.ieltsaiprep.com/assessment/{assessment_type}')
                if response.getcode() == 200:
                    print(f"✅ {display_name} assessment working!")
                else:
                    print(f"⚠️ {assessment_type} returned status {response.getcode()}")
            except Exception as e:
                print(f"⚠️ {assessment_type} test failed: {str(e)}")
        
        # Test home page
        try:
            response = urllib.request.urlopen('https://www.ieltsaiprep.com/')
            if response.getcode() == 200:
                print("✅ Enhanced home page working!")
            else:
                print(f"⚠️ Home page returned status {response.getcode()}")
        except Exception as e:
            print(f"⚠️ Home page test failed: {str(e)}")
        
    except Exception as e:
        print(f"❌ Deployment failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    deploy_extended_system()