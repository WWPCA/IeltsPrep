#!/usr/bin/env python3
"""
Add All Assessment Types - Extend Working Template
Adds General Writing, Academic Speaking, and General Speaking to the working template
"""

import boto3
import json
import zipfile

def create_complete_assessment_system():
    """Create complete assessment system with all 4 types and task navigation"""
    
    lambda_code = '''
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

# Complete assessment questions for all 4 types
MOCK_QUESTIONS = {
    "academic_writing": {
        "question_id": "aw_001",
        "question_text": "The chart below shows the percentage of households in owned and rented accommodation in England and Wales between 1918 and 2011.",
        "chart_svg": "<svg width=\\"400\\" height=\\"300\\" xmlns=\\"http://www.w3.org/2000/svg\\"><rect width=\\"400\\" height=\\"300\\" fill=\\"#f9f9f9\\" stroke=\\"#ddd\\"/><text x=\\"200\\" y=\\"30\\" text-anchor=\\"middle\\" font-family=\\"Arial\\" font-size=\\"16\\" font-weight=\\"bold\\">Household Accommodation 1918-2011</text><line x1=\\"50\\" y1=\\"250\\" x2=\\"350\\" y2=\\"250\\" stroke=\\"#333\\" stroke-width=\\"2\\"/><line x1=\\"50\\" y1=\\"250\\" x2=\\"50\\" y2=\\"100\\" stroke=\\"#333\\" stroke-width=\\"2\\"/><rect x=\\"80\\" y=\\"150\\" width=\\"30\\" height=\\"100\\" fill=\\"#e31e24\\"/><rect x=\\"120\\" y=\\"180\\" width=\\"30\\" height=\\"70\\" fill=\\"#0066cc\\"/><rect x=\\"200\\" y=\\"120\\" width=\\"30\\" height=\\"130\\" fill=\\"#e31e24\\"/><rect x=\\"240\\" y=\\"200\\" width=\\"30\\" height=\\"50\\" fill=\\"#0066cc\\"/><text x=\\"200\\" y=\\"290\\" text-anchor=\\"middle\\" font-family=\\"Arial\\" font-size=\\"10\\">Red: Owned, Blue: Rented</text></svg>",
        "tasks": [
            {"task_number": 1, "time_minutes": 20, "instructions": "Summarize the information by selecting and reporting the main features, and make comparisons where relevant.", "word_count": 150},
            {"task_number": 2, "time_minutes": 40, "instructions": "Some people think that all university students should study whatever they like. Others believe that they should only be allowed to study subjects that will be useful in the future, such as those related to science and technology. Discuss both these views and give your own opinion.", "word_count": 250}
        ]
    },
    "general_writing": {
        "question_id": "gw_001",
        "question_text": "You recently bought a piece of equipment for your kitchen but it did not work. You phoned the shop but no action was taken.",
        "tasks": [
            {"task_number": 1, "time_minutes": 20, "instructions": "Write a letter to the shop manager. In your letter: describe the problem with the equipment, explain what happened when you phoned the shop, say what you would like the manager to do.", "word_count": 150},
            {"task_number": 2, "time_minutes": 40, "instructions": "Some people say that the main environmental problem of our time is the loss of particular species of plants and animals. Others say that there are more important environmental problems. Discuss both these views and give your own opinion.", "word_count": 250}
        ]
    },
    "academic_speaking": {
        "question_id": "as_001",
        "question_text": "Academic Speaking Assessment with Maya AI Examiner",
        "tasks": [
            {"task_number": 1, "time_minutes": 5, "instructions": "Introduction and Interview - Answer questions about yourself, your home, work or studies, and other familiar topics.", "word_count": 0},
            {"task_number": 2, "time_minutes": 4, "instructions": "Long Turn - You will be given a topic card. You have 1 minute to prepare and should speak for 1-2 minutes. Topic: Describe a memorable journey you have taken.", "word_count": 0},
            {"task_number": 3, "time_minutes": 5, "instructions": "Discussion - Answer questions related to the topic in Part 2, discussing abstract ideas and issues.", "word_count": 0}
        ]
    },
    "general_speaking": {
        "question_id": "gs_001",
        "question_text": "General Speaking Assessment with Maya AI Examiner",
        "tasks": [
            {"task_number": 1, "time_minutes": 5, "instructions": "Introduction and Interview - Answer questions about yourself, your home, work or studies, and other familiar topics.", "word_count": 0},
            {"task_number": 2, "time_minutes": 4, "instructions": "Long Turn - You will be given a topic card. You have 1 minute to prepare and should speak for 1-2 minutes. Topic: Describe a place you like to visit in your free time.", "word_count": 0},
            {"task_number": 3, "time_minutes": 5, "instructions": "Discussion - Answer questions related to the topic in Part 2, discussing abstract ideas and issues.", "word_count": 0}
        ]
    }
}

def lambda_handler(event, context):
    """Main AWS Lambda handler with all assessment types"""
    try:
        path = event.get("path", "/")
        method = event.get("httpMethod", "GET")
        query_params = event.get("queryStringParameters") or {}
        
        if path == "/":
            return handle_home_page()
        elif path.startswith("/assessment/"):
            assessment_type = path.split("/")[-1]
            current_task = int(query_params.get("task", 1))
            return handle_assessment_page(assessment_type, current_task)
        elif path == "/api/health":
            return handle_health_check()
        else:
            return {"statusCode": 404, "headers": {"Content-Type": "text/html"}, "body": "<h1>404 Not Found</h1>"}
    except Exception as e:
        return {"statusCode": 500, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"error": str(e)})}

def handle_home_page():
    """Enhanced home page with all 4 assessment types"""
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/html"},
        "body": get_home_page_html()
    }

def get_home_page_html():
    """Generate home page HTML"""
    return """<!DOCTYPE html>
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
                   <strong>Task 2:</strong> Essay writing (40 min, 250 words)<br>
                   <strong>Technology:</strong> TrueScore® Nova Micro</p>
                <a href="/assessment/academic-writing" class="btn">Start Assessment</a>
            </div>
            
            <div class="assessment-card">
                <h3>General Writing<span class="writing-badge">Writing</span><span class="general-badge">General</span></h3>
                <p><strong>Task 1:</strong> Letter writing (20 min, 150 words)<br>
                   <strong>Task 2:</strong> Essay writing (40 min, 250 words)<br>
                   <strong>Technology:</strong> TrueScore® Nova Micro</p>
                <a href="/assessment/general-writing" class="btn">Start Assessment</a>
            </div>
            
            <div class="assessment-card">
                <h3>Academic Speaking<span class="speaking-badge">Speaking</span><span class="academic-badge">Academic</span></h3>
                <p><strong>Part 1:</strong> Interview (5 min)<br>
                   <strong>Part 2:</strong> Long turn (4 min)<br>
                   <strong>Part 3:</strong> Discussion (5 min)<br>
                   <strong>Technology:</strong> ClearScore® Maya AI</p>
                <a href="/assessment/academic-speaking" class="btn">Start Assessment</a>
            </div>
            
            <div class="assessment-card">
                <h3>General Speaking<span class="speaking-badge">Speaking</span><span class="general-badge">General</span></h3>
                <p><strong>Part 1:</strong> Interview (5 min)<br>
                   <strong>Part 2:</strong> Long turn (4 min)<br>
                   <strong>Part 3:</strong> Discussion (5 min)<br>
                   <strong>Technology:</strong> ClearScore® Maya AI</p>
                <a href="/assessment/general-speaking" class="btn">Start Assessment</a>
            </div>
        </div>
        
        <div style="margin-top: 40px; padding: 20px; background: #e8f4fd; border: 1px solid #0066cc; border-radius: 4px;">
            <strong>Assessment Features:</strong><br>
            • Single task display with authentic IELTS layout<br>
            • Multi-task progression flow (Task 1 → Submit → Continue to Task 2)<br>
            • Real-time word counting and timer functionality<br>
            • Professional chart display for writing assessments<br>
            • Maya AI examiner for speaking assessments<br>
            • Complete Google Play compliance integration
        </div>
    </div>
</body>
</html>"""

def handle_assessment_page(assessment_type, current_task):
    """Handle assessment page with multi-task progression and official IELTS layout"""
    question_data = MOCK_QUESTIONS.get(assessment_type, {})
    if not question_data:
        return {"statusCode": 404, "headers": {"Content-Type": "text/html"}, "body": "Assessment type not found"}
    
    tasks = question_data.get("tasks", [])
    if current_task > len(tasks):
        current_task = len(tasks)
    
    current_task_data = tasks[current_task - 1] if tasks else {}
    
    assessment_title = assessment_type.replace("_", " ").title()
    is_speaking = "speaking" in assessment_type
    is_academic = "academic" in assessment_type
    
    total_tasks = len(tasks)
    
    # Task navigation indicators
    task_indicators = ""
    for i in range(1, total_tasks + 1):
        css_class = "active" if i == current_task else ("completed" if i < current_task else "inactive")
        task_indicators += '<span class="task-indicator ' + css_class + '">Part ' + str(i) + '</span>'
    
    # Task content
    if current_task == 1:
        task_content = question_data.get("question_text", "")
    else:
        task_content = current_task_data.get("instructions", "")
    
    # Chart display for writing tasks only on Task 1
    chart_display = ""
    if not is_speaking and current_task == 1 and "chart_svg" in question_data:
        chart_display = '''
        <div class="chart-container">
            <div class="chart-title">Household Accommodation 1918-2011</div>
            ''' + question_data["chart_svg"] + '''
        </div>
        '''
    
    # Input area based on assessment type
    if is_speaking:
        input_area = get_speaking_input_area(current_task)
    else:
        input_area = get_writing_input_area()
    
    # Navigation buttons
    if current_task < total_tasks:
        nav_buttons = '<button class="btn btn-next" id="nextBtn" onclick="nextTask()">Continue to Part ' + str(current_task + 1) + '</button>'
    else:
        nav_buttons = '<button class="btn btn-submit" id="submitBtn">Submit Assessment</button>'
    
    # Generate complete HTML
    html_content = get_assessment_html_template(
        assessment_title, current_task, current_task_data, 
        task_content, chart_display, input_area, 
        task_indicators, nav_buttons, total_tasks,
        question_data.get("question_id", ""), is_speaking, is_academic
    )
    
    return {"statusCode": 200, "headers": {"Content-Type": "text/html"}, "body": html_content}

def get_speaking_input_area(current_task):
    """Generate speaking input area with Maya AI chat"""
    return '''
        <div class="speaking-area">
            <div class="recording-controls">
                <button class="btn btn-record" id="recordBtn">🎤 Start Recording</button>
                <button class="btn btn-stop" id="stopBtn" disabled>⏹️ Stop Recording</button>
                <button class="btn btn-play" id="playBtn" disabled>▶️ Play Recording</button>
            </div>
            <div class="recording-status" id="recordingStatus">Click "Start Recording" to begin speaking with Maya</div>
            <div class="maya-chat">
                <div class="maya-messages" id="mayaMessages">
                    <div class="maya-message">
                        <strong>Maya (AI Examiner):</strong> Hello! I'm Maya, your AI examiner. Let's begin Part ''' + str(current_task) + ''' of your IELTS Speaking assessment. Are you ready to start?
                    </div>
                </div>
            </div>
        </div>
        '''

def get_writing_input_area():
    """Generate writing input area with word count"""
    return '''
        <textarea id="essayText" class="answer-textarea" placeholder="Type your answer here..."></textarea>
        <div class="word-count">Words: <span id="wordCount">0</span></div>
        '''

def get_assessment_html_template(assessment_title, current_task, current_task_data, task_content, chart_display, input_area, task_indicators, nav_buttons, total_tasks, question_id, is_speaking, is_academic):
    """Generate complete assessment HTML template"""
    
    time_minutes = current_task_data.get("time_minutes", 60)
    word_count = current_task_data.get("word_count", 150)
    
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>''' + assessment_title + ''' Assessment</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background-color: #f5f5f5; }
        .header { background-color: #fff; padding: 15px 20px; border-bottom: 1px solid #ddd; display: flex; justify-content: space-between; align-items: center; }
        .logo { background-color: #e31e24; color: white; padding: 8px 12px; font-weight: bold; font-size: 18px; }
        .timer { background-color: #333; color: white; padding: 8px 15px; border-radius: 4px; font-weight: bold; }
        .main-content { display: flex; height: calc(100vh - 120px); background-color: #fff; }
        .question-panel { width: 50%; padding: 20px; border-right: 1px solid #ddd; overflow-y: auto; }
        .answer-panel { width: 50%; padding: 20px; display: flex; flex-direction: column; }
        .part-header { background-color: #f8f8f8; padding: 10px 15px; margin-bottom: 20px; border-left: 4px solid #e31e24; }
        .chart-container { margin: 20px 0; padding: 20px; background-color: #f9f9f9; border: 1px solid #ddd; text-align: center; }
        .chart-title { font-size: 14px; font-weight: bold; margin-bottom: 15px; }
        .answer-textarea { flex: 1; width: 100%; padding: 15px; border: 1px solid #ddd; font-family: Arial, sans-serif; font-size: 14px; resize: none; }
        .word-count { text-align: right; padding: 10px; font-size: 12px; color: #666; border: 1px solid #ddd; border-top: none; background-color: #f9f9f9; }
        .speaking-area { flex: 1; display: flex; flex-direction: column; }
        .recording-controls { display: flex; gap: 10px; margin-bottom: 15px; flex-wrap: wrap; }
        .recording-status { padding: 10px; background-color: #f8f9fa; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 15px; }
        .maya-chat { flex: 1; border: 1px solid #ddd; border-radius: 4px; padding: 15px; background-color: #f9f9f9; }
        .maya-messages { height: 100%; overflow-y: auto; }
        .maya-message { padding: 10px; margin-bottom: 10px; background-color: white; border-radius: 4px; }
        .footer { display: flex; justify-content: space-between; align-items: center; padding: 15px 20px; background-color: #f8f8f8; border-top: 1px solid #ddd; }
        .btn { padding: 10px 20px; border: none; border-radius: 4px; font-size: 14px; font-weight: bold; cursor: pointer; }
        .btn-submit { background-color: #28a745; color: white; }
        .btn-next { background-color: #007bff; color: white; }
        .btn-record { background-color: #dc3545; color: white; }
        .btn-stop { background-color: #6c757d; color: white; }
        .btn-play { background-color: #17a2b8; color: white; }
        .btn:disabled { background-color: #e9ecef; color: #6c757d; cursor: not-allowed; }
        .task-indicator { padding: 5px 10px; border-radius: 3px; font-size: 12px; font-weight: bold; margin-right: 5px; }
        .task-indicator.active { background-color: #e31e24; color: white; }
        .task-indicator.completed { background-color: #28a745; color: white; }
        .task-indicator.inactive { background-color: #e9ecef; color: #6c757d; }
        .progress-info { font-size: 12px; color: #666; margin-left: 10px; }
        @media (max-width: 768px) {
            .main-content { flex-direction: column; height: auto; }
            .question-panel, .answer-panel { width: 100%; }
            .question-panel { border-right: none; border-bottom: 1px solid #ddd; }
        }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <div class="logo">IELTS GenAI</div>
            <div style="font-size: 14px; color: #666;">Test taker: test@example.com</div>
        </div>
        <div class="timer" id="timer">''' + str(time_minutes) + ''':00</div>
    </div>
    
    <div class="main-content">
        <div class="question-panel">
            <div class="part-header">
                <div style="font-size: 16px; font-weight: bold;">Part ''' + str(current_task) + '''</div>
                <div style="font-size: 14px; color: #666;">
                    ''' + current_task_data.get("instructions", "") + '''
                </div>
            </div>
            
            <div style="line-height: 1.6; margin-bottom: 20px;">
                ''' + task_content + '''
            </div>
            
            ''' + chart_display + '''
            
            <div style="margin-top: 20px; padding: 15px; background: #e8f4fd; border: 1px solid #0066cc; border-radius: 4px;">
                <strong>Assessment Information:</strong><br>
                • Question ID: ''' + question_id + '''<br>
                • Technology: ''' + ("ClearScore® Maya AI" if is_speaking else "TrueScore® Nova Micro") + '''<br>
                • Format: ''' + ("Official IELTS Speaking" if is_speaking else "Official IELTS Writing") + '''<br>
                • Type: ''' + ("Academic" if is_academic else "General Training") + '''
            </div>
        </div>
        
        <div class="answer-panel">
            ''' + input_area + '''
        </div>
    </div>
    
    <div class="footer">
        <div>
            ''' + task_indicators + '''
            <span class="progress-info">Part ''' + str(current_task) + ''' of ''' + str(total_tasks) + '''</span>
        </div>
        <div>''' + nav_buttons + '''</div>
    </div>
    
    <script>
        let timeRemaining = ''' + str(time_minutes) + ''' * 60;
        const timer = document.getElementById('timer');
        const isWriting = ''' + ("false" if is_speaking else "true") + ''';
        
        function updateTimer() {
            const minutes = Math.floor(timeRemaining / 60);
            const seconds = timeRemaining % 60;
            timer.textContent = minutes.toString().padStart(2, '0') + ':' + seconds.toString().padStart(2, '0');
            
            if (timeRemaining <= 0) {
                alert('Time is up for this part!');
                return;
            }
            
            timeRemaining--;
        }
        
        function nextTask() {
            const currentUrl = new URL(window.location);
            const nextTaskNum = ''' + str(current_task + 1) + ''';
            currentUrl.searchParams.set('task', nextTaskNum);
            window.location.href = currentUrl.toString();
        }
        
        setInterval(updateTimer, 1000);
        updateTimer();
        
        if (isWriting) {
            const essayText = document.getElementById('essayText');
            const wordCount = document.getElementById('wordCount');
            const submitBtn = document.getElementById('submitBtn');
            
            function updateWordCount() {
                const text = essayText.value.trim();
                const words = text ? text.split(/\\s+/).length : 0;
                wordCount.textContent = words;
                
                const minWords = ''' + str(word_count) + ''';
                if (words >= minWords && submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.style.backgroundColor = '#28a745';
                } else if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.style.backgroundColor = '#e9ecef';
                }
            }
            
            essayText.addEventListener('input', updateWordCount);
            updateWordCount();
            
            // Auto-save functionality
            setInterval(function() {
                if (essayText.value.trim()) {
                    localStorage.setItem('ielts_essay_draft_''' + assessment_type + '''_''' + str(current_task) + '''', essayText.value);
                }
            }, 30000);
            
            // Load saved draft
            const savedDraft = localStorage.getItem('ielts_essay_draft_''' + assessment_type + '''_''' + str(current_task) + '''');
            if (savedDraft) {
                essayText.value = savedDraft;
                updateWordCount();
            }
        }
        
        if (!isWriting) {
            // Speaking assessment functionality
            const recordBtn = document.getElementById('recordBtn');
            const stopBtn = document.getElementById('stopBtn');
            const playBtn = document.getElementById('playBtn');
            const recordingStatus = document.getElementById('recordingStatus');
            
            let mediaRecorder;
            let audioChunks = [];
            
            recordBtn.addEventListener('click', async function() {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream);
                    audioChunks = [];
                    
                    mediaRecorder.ondataavailable = function(event) {
                        audioChunks.push(event.data);
                    };
                    
                    mediaRecorder.start();
                    recordBtn.disabled = true;
                    stopBtn.disabled = false;
                    recordingStatus.textContent = 'Recording in progress... Speak clearly for Maya AI analysis';
                    recordingStatus.style.backgroundColor = '#fff3cd';
                } catch (error) {
                    recordingStatus.textContent = 'Error: Could not access microphone. Please allow microphone access.';
                    recordingStatus.style.backgroundColor = '#f8d7da';
                }
            });
            
            stopBtn.addEventListener('click', function() {
                mediaRecorder.stop();
                recordBtn.disabled = false;
                stopBtn.disabled = true;
                playBtn.disabled = false;
                recordingStatus.textContent = 'Recording completed. You can play it back or continue to the next part.';
                recordingStatus.style.backgroundColor = '#d1ecf1';
            });
            
            playBtn.addEventListener('click', function() {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                const audioUrl = URL.createObjectURL(audioBlob);
                const audio = new Audio(audioUrl);
                audio.play();
            });
        }
    </script>
</body>
</html>'''

def handle_health_check():
    """Handle health check"""
    return {"statusCode": 200, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"status": "healthy", "timestamp": datetime.now().isoformat()})}
'''
    
    return lambda_code

def deploy_complete_system():
    """Deploy complete assessment system with all 4 types"""
    
    print("🚀 Deploying Complete Assessment System")
    print("=" * 45)
    
    # Create lambda code
    lambda_code = create_complete_assessment_system()
    
    # Write to file
    with open('lambda_function.py', 'w') as f:
        f.write(lambda_code)
    
    # Create deployment package
    with zipfile.ZipFile('complete_assessment_system.zip', 'w') as zipf:
        zipf.write('lambda_function.py')
    
    # Deploy to AWS
    try:
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        with open('complete_assessment_system.zip', 'rb') as f:
            lambda_client.update_function_code(
                FunctionName='ielts-genai-prep-api',
                ZipFile=f.read()
            )
        
        print("✅ Complete assessment system deployed successfully!")
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
        
        # Test task navigation
        try:
            response = urllib.request.urlopen('https://www.ieltsaiprep.com/assessment/academic-writing?task=2')
            if response.getcode() == 200:
                print("✅ Multi-task navigation working!")
            else:
                print(f"⚠️ Task navigation returned status {response.getcode()}")
        except Exception as e:
            print(f"⚠️ Task navigation test failed: {str(e)}")
        
    except Exception as e:
        print(f"❌ Deployment failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    deploy_complete_system()