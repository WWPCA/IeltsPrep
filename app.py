#!/usr/bin/env python3
"""
Pure AWS Lambda Handler for IELTS GenAI Prep QR Authentication
Compatible with SAM CLI local testing
"""

import json
import os
import uuid
import time
import base64
from io import BytesIO
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Set environment for .replit testing
os.environ['REPLIT_ENVIRONMENT'] = 'true'

# Import AWS mock services
from aws_mock_config import aws_mock

def generate_qr_code(data: str) -> str:
    """Generate QR code image as base64 string"""
    try:
        import qrcode
        
        # Generate QR code using simple API
        qr_img = qrcode.make(data)
        
        # Convert to base64
        buffer = BytesIO()
        qr_img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode()
    except ImportError:
        print("[WARNING] QRCode library not available, using placeholder")
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

def lambda_handler(event, context):
    """Main AWS Lambda handler for QR authentication"""
    try:
        # Extract request information
        path = event.get('path', event.get('rawPath', ''))
        method = event.get('httpMethod', event.get('requestContext', {}).get('http', {}).get('method', 'GET'))
        body = event.get('body', '{}')
        headers = event.get('headers', {})
        
        # Parse request body
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            data = {}
        
        print(f"[CLOUDWATCH] Lambda processing {method} {path}")
        
        # Route requests
        if path == '/api/health':
            return handle_health_check()
        elif path == '/api/auth/generate-qr' and method == 'POST':
            return handle_generate_qr(data)
        elif path == '/api/auth/verify-qr' and method == 'POST':
            return handle_verify_qr(data)
        elif path == '/purchase/verify/apple' and method == 'POST':
            return handle_apple_purchase_verification(data)
        elif path == '/purchase/verify/google' and method == 'POST':
            return handle_google_purchase_verification(data)
        elif path.startswith('/assessment/') and method == 'GET':
            return handle_assessment_access(path, headers)
        elif path == '/api/website/request-qr' and method == 'POST':
            return handle_website_qr_request(data)
        elif path == '/api/website/check-auth' and method == 'POST':
            return handle_website_auth_check(data)
        elif path == '/api/mobile/scan-qr' and method == 'POST':
            return handle_mobile_qr_scan(data)
        elif path == '/api/register' and method == 'POST':
            return handle_user_registration(data)
        elif path == '/api/login' and method == 'POST':
            return handle_user_login(data)
        elif path == '/api/maya/introduction' and method == 'POST':
            return handle_maya_introduction(data)
        elif path == '/api/maya/conversation' and method == 'POST':
            return handle_maya_conversation(data)
        elif path == '/api/nova-micro/writing' and method == 'POST':
            return handle_nova_micro_writing(data)
        elif path == '/api/nova-micro/submit' and method == 'POST':
            return handle_nova_micro_submit(data)
        elif path == '/qr-auth' and method == 'GET':
            return handle_qr_auth_page()
        elif path == '/profile' and method == 'GET':
            return handle_profile_page(headers)
        elif path == '/test_mobile_home_screen.html' and method == 'GET':
            return handle_static_file('test_mobile_home_screen.html')
        elif path == '/nova-assessment.html' and method == 'GET':
            return handle_static_file('nova_assessment_demo.html')
        elif path == '/database-schema' and method == 'GET':
            return handle_database_schema_page()
        elif path == '/nova-assessment' and method == 'GET':
            return handle_nova_assessment_demo()
        elif path == '/' and method == 'GET':
            return handle_home_page()
        else:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Endpoint not found'})
            }
            
    except Exception as e:
        print(f"[CLOUDWATCH] Lambda handler error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }

def handle_static_file(filename: str) -> Dict[str, Any]:
    """Handle static file serving"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content_type = 'text/html' if filename.endswith('.html') else 'text/plain'
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': content_type,
                'Access-Control-Allow-Origin': '*'
            },
            'body': content
        }
    except FileNotFoundError:
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': f'File {filename} not found'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }

def handle_home_page() -> Dict[str, Any]:
    """Handle home page - serve mobile app home screen"""
    return handle_static_file('test_mobile_home_screen.html')

def handle_qr_auth_page() -> Dict[str, Any]:
    """Serve QR authentication page"""
    try:
        with open('templates/qr_auth_page.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
                'Cache-Control': 'no-cache'
            },
            'body': html_content
        }
    except FileNotFoundError:
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'text/html'},
            'body': '<h1>QR Authentication page not found</h1>'
        }

def handle_profile_page(headers: Dict[str, Any]) -> Dict[str, Any]:
    """Serve user profile page with session verification"""
    try:
        # Check for valid session cookie
        cookie_header = headers.get('cookie', '')
        session_id = None
        
        # Extract session ID from cookies
        if 'web_session_id=' in cookie_header:
            for cookie in cookie_header.split(';'):
                if 'web_session_id=' in cookie:
                    session_id = cookie.split('=')[1].strip()
                    break
        
        if not session_id:
            # No session found, redirect to QR auth
            return {
                'statusCode': 302,
                'headers': {
                    'Location': '/qr-auth',
                    'Content-Type': 'text/html'
                },
                'body': ''
            }
        
        # Verify session exists and is valid
        session_data = aws_mock.get_session(session_id)
        if not session_data:
            # Invalid session, redirect to QR auth
            return {
                'statusCode': 302,
                'headers': {
                    'Location': '/qr-auth',
                    'Content-Type': 'text/html'
                },
                'body': ''
            }
        
        # Check session expiry
        if session_data.get('expires_at', 0) < time.time():
            # Session expired
            return {
                'statusCode': 302,
                'headers': {
                    'Location': '/qr-auth',
                    'Content-Type': 'text/html'
                },
                'body': ''
            }
        
        # Load profile page template
        with open('templates/profile.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
                'Cache-Control': 'no-cache'
            },
            'body': html_content
        }
        
    except FileNotFoundError:
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'text/html'},
            'body': '<h1>Profile page not found</h1>'
        }
    except Exception as e:
        print(f"[CLOUDWATCH] Profile page error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': f'<h1>Error loading profile: {str(e)}</h1>'
        }

def handle_database_schema_page() -> Dict[str, Any]:
    """Serve database schema documentation page"""
    try:
        with open('database_schema_demo.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
                'Access-Control-Allow-Origin': '*'
            },
            'body': content
        }
        
    except FileNotFoundError:
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'text/plain'},
            'body': 'Database schema page not found'
        }
    except Exception as e:
        print(f"[CLOUDWATCH] Database schema page error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': f'<h1>Error loading database schema: {str(e)}</h1>'
        }

def handle_nova_assessment_demo() -> Dict[str, Any]:
    """Serve Nova AI assessment demonstration page"""
    try:
        with open('nova_assessment_demo.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
                'Access-Control-Allow-Origin': '*'
            },
            'body': content
        }
        
    except FileNotFoundError:
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'text/plain'},
            'body': 'Nova assessment demo not found'
        }
    except Exception as e:
        print(f"[CLOUDWATCH] Nova assessment demo error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': f'<h1>Error loading Nova demo: {str(e)}</h1>'
        }

def get_assessment_template(assessment_type: str, user_email: str, session_id: str) -> str:
    """Load appropriate assessment template with Maya auto-start functionality"""
    
    # Get Nova prompts from DynamoDB
    rubric = aws_mock.get_assessment_rubric(assessment_type)
    nova_prompts = rubric.get('nova_sonic_prompts', {}) if rubric else {}
    
    if 'speaking' in assessment_type:
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Maya - {assessment_type.replace('_', ' ').title()} Assessment</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
        .maya-intro {{ background: #e8f4fd; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .conversation-area {{ background: #f8f9fa; padding: 20px; border-radius: 8px; min-height: 300px; }}
        .maya-message {{ background: #d4edda; padding: 15px; border-radius: 8px; margin: 10px 0; }}
        .user-message {{ background: #fff3cd; padding: 15px; border-radius: 8px; margin: 10px 0; }}
        .controls {{ text-align: center; margin: 20px 0; }}
        .btn {{ padding: 12px 24px; margin: 5px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }}
        .btn-primary {{ background: #007bff; color: white; }}
        .btn-success {{ background: #28a745; color: white; }}
        .btn-danger {{ background: #dc3545; color: white; }}
        .status {{ text-align: center; margin: 15px 0; font-weight: bold; }}
        .auto-start-notice {{ background: #ffc107; color: #212529; padding: 10px; border-radius: 5px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Maya - Your IELTS Speaking Examiner</h1>
        
        <div class="maya-intro">
            <h3>Welcome to your {assessment_type.replace('_', ' ').title()} Assessment</h3>
            <p><strong>User:</strong> {user_email}</p>
            <p><strong>Session:</strong> {session_id}</p>
            <div class="auto-start-notice">
                📢 Maya will automatically introduce herself and start the assessment when this page loads.
            </div>
        </div>

        <div class="status" id="status">Initializing Maya...</div>
        
        <div class="conversation-area" id="conversation">
            <div class="maya-message" id="maya-intro">
                <strong>Maya:</strong> <span id="intro-text">Loading introduction...</span>
            </div>
        </div>

        <div class="controls">
            <button class="btn btn-success" id="speakBtn" disabled>🎤 Speak to Maya</button>
            <button class="btn btn-danger" id="stopBtn" disabled>⏹️ Stop</button>
        </div>

        <audio id="mayaAudio" style="display: none;"></audio>
    </div>

    <script>
        let isListening = false;
        let recognition = null;
        let conversationActive = false;
        
        // Initialize speech recognition
        function initializeSpeechRecognition() {{
            if ('webkitSpeechRecognition' in window) {{
                recognition = new webkitSpeechRecognition();
            }} else if ('SpeechRecognition' in window) {{
                recognition = new SpeechRecognition();
            }} else {{
                document.getElementById('status').innerHTML = '❌ Speech recognition not supported. Please use Chrome, Edge, or Safari.';
                return false;
            }}
            
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';
            
            recognition.onresult = function(event) {{
                const transcript = event.results[0][0].transcript;
                addMessage('You', transcript, 'user-message');
                sendToMaya(transcript);
            }};
            
            recognition.onerror = function(event) {{
                console.error('Speech recognition error:', event.error);
                document.getElementById('status').textContent = 'Speech recognition error. Please try again.';
                isListening = false;
                updateButtons();
            }};
            
            recognition.onend = function() {{
                isListening = false;
                updateButtons();
            }};
            
            return true;
        }}
        
        // Auto-start Maya introduction
        async function startMayaIntroduction() {{
            try {{
                document.getElementById('status').textContent = '🤖 Maya is introducing herself...';
                
                const response = await fetch('/api/maya/introduction', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        assessment_type: '{assessment_type}',
                        user_email: '{user_email}',
                        session_id: '{session_id}'
                    }})
                }});
                
                const result = await response.json();
                
                if (result.success) {{
                    document.getElementById('intro-text').textContent = result.introduction;
                    document.getElementById('status').textContent = '🔊 Maya is speaking...';
                    
                    // Auto-play Maya's introduction
                    if (result.audio_url) {{
                        const audio = document.getElementById('mayaAudio');
                        audio.src = result.audio_url;
                        
                        audio.onplay = () => {{
                            document.getElementById('status').textContent = '🔊 Maya is speaking - Listen carefully';
                        }};
                        
                        audio.onended = () => {{
                            document.getElementById('status').textContent = '✅ Maya has finished - Click "Speak to Maya" to respond';
                            conversationActive = true;
                            updateButtons();
                        }};
                        
                        audio.play();
                    }} else {{
                        document.getElementById('status').textContent = '✅ Maya is ready - Click "Speak to Maya" to start';
                        conversationActive = true;
                        updateButtons();
                    }}
                }} else {{
                    document.getElementById('status').textContent = '❌ Error starting assessment: ' + (result.error || 'Unknown error');
                }}
            }} catch (error) {{
                console.error('Error starting Maya:', error);
                document.getElementById('status').textContent = '❌ Connection error. Please refresh the page.';
            }}
        }}
        
        function addMessage(sender, message, className) {{
            const messageDiv = document.createElement('div');
            messageDiv.className = className;
            messageDiv.innerHTML = `<strong>${{sender}}:</strong> ${{message}}`;
            document.getElementById('conversation').appendChild(messageDiv);
        }}
        
        async function sendToMaya(userMessage) {{
            try {{
                document.getElementById('status').textContent = '🤖 Maya is thinking...';
                
                const response = await fetch('/api/maya/conversation', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        user_message: userMessage,
                        assessment_type: '{assessment_type}',
                        session_id: '{session_id}'
                    }})
                }});
                
                const result = await response.json();
                
                if (result.success) {{
                    addMessage('Maya', result.response, 'maya-message');
                    document.getElementById('status').textContent = '🔊 Maya is responding...';
                    
                    if (result.audio_url) {{
                        const audio = document.getElementById('mayaAudio');
                        audio.src = result.audio_url;
                        
                        audio.onended = () => {{
                            document.getElementById('status').textContent = '✅ Maya finished - Your turn to speak';
                            updateButtons();
                        }};
                        
                        audio.play();
                    }}
                }} else {{
                    document.getElementById('status').textContent = '❌ Maya error: ' + (result.error || 'Unknown error');
                }}
            }} catch (error) {{
                console.error('Error with Maya conversation:', error);
                document.getElementById('status').textContent = '❌ Connection error with Maya';
            }}
        }}
        
        function updateButtons() {{
            const speakBtn = document.getElementById('speakBtn');
            const stopBtn = document.getElementById('stopBtn');
            
            if (conversationActive && !isListening) {{
                speakBtn.disabled = false;
                speakBtn.textContent = '🎤 Speak to Maya';
                stopBtn.disabled = true;
            }} else if (isListening) {{
                speakBtn.disabled = true;
                stopBtn.disabled = false;
            }} else {{
                speakBtn.disabled = true;
                stopBtn.disabled = true;
            }}
        }}
        
        // Event listeners
        document.getElementById('speakBtn').addEventListener('click', function() {{
            if (recognition && !isListening) {{
                isListening = true;
                document.getElementById('status').textContent = '🎤 Listening... Speak now';
                updateButtons();
                recognition.start();
            }}
        }});
        
        document.getElementById('stopBtn').addEventListener('click', function() {{
            if (recognition && isListening) {{
                recognition.stop();
            }}
        }});
        
        // Initialize when page loads
        window.addEventListener('load', function() {{
            if (initializeSpeechRecognition()) {{
                // Auto-start Maya introduction after 2 seconds
                setTimeout(startMayaIntroduction, 2000);
            }}
        }});
    </script>
</body>
</html>
"""
    else:
        # Writing assessment template with Nova Micro integration
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nova Micro - {assessment_type.replace('_', ' ').title()} Assessment</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
        .task-prompt {{ background: #f0f8e8; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #28a745; }}
        .writing-area {{ width: 100%; min-height: 400px; padding: 15px; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; line-height: 1.5; }}
        .controls {{ display: flex; justify-content: space-between; align-items: center; margin: 20px 0; }}
        .word-count {{ font-weight: bold; color: #666; }}
        .btn {{ padding: 12px 24px; margin: 5px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }}
        .btn-primary {{ background: #007bff; color: white; }}
        .btn-success {{ background: #28a745; color: white; }}
        .btn-disabled {{ background: #6c757d; color: white; cursor: not-allowed; }}
        .status {{ text-align: center; margin: 15px 0; font-weight: bold; }}
        .assessment-result {{ background: #d4edda; padding: 20px; border-radius: 8px; margin: 20px 0; display: none; }}
        .band-scores {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 15px 0; }}
        .band-item {{ background: #f8f9fa; padding: 15px; border-radius: 5px; text-align: center; }}
        .overall-score {{ font-size: 24px; font-weight: bold; color: #28a745; }}
        .feedback-section {{ background: #fff3cd; padding: 15px; border-radius: 5px; margin: 10px 0; }}
        .timer {{ color: #dc3545; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Nova Micro Writing Assessment</h1>
        
        <div style="background: #e8f4fd; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3>{assessment_type.replace('_', ' ').title()} Assessment</h3>
            <p><strong>User:</strong> {user_email}</p>
            <p><strong>Session:</strong> {session_id}</p>
            <p>Nova Micro will evaluate your writing using official IELTS band descriptors from the database.</p>
        </div>

        <div class="task-prompt">
            <h3>Writing Task</h3>
            <p id="taskPrompt">You should spend about 40 minutes on this task. Some people believe that technology has made our lives more complicated, while others argue that it has made life easier. Discuss both views and give your own opinion. Give reasons for your answer and include any relevant examples from your own knowledge or experience. Write at least 250 words.</p>
        </div>

        <div class="controls">
            <div class="word-count">Words: <span id="wordCount">0</span> / <span id="minWords">250</span></div>
            <div class="timer">Time: <span id="timer">40:00</span></div>
        </div>

        <textarea 
            id="essayText" 
            class="writing-area" 
            placeholder="Start writing your essay here... Nova Micro will analyze your response against IELTS band criteria."
        ></textarea>

        <div class="controls">
            <button class="btn btn-primary" id="submitBtn" disabled>Submit for Nova Micro Assessment</button>
            <button class="btn btn-success" id="saveBtn">Save Draft</button>
        </div>

        <div class="status" id="status">Start writing to enable assessment...</div>

        <div class="assessment-result" id="assessmentResult">
            <h3>Nova Micro Assessment Results</h3>
            <div class="overall-score" id="overallScore">7.0</div>
            <p style="text-align: center; margin: 10px 0;">Overall Band Score</p>
            
            <div class="band-scores" id="bandScores">
                <div class="band-item">
                    <strong>Task Achievement</strong>
                    <div id="taskScore">7.0</div>
                </div>
                <div class="band-item">
                    <strong>Coherence & Cohesion</strong>
                    <div id="coherenceScore">6.5</div>
                </div>
                <div class="band-item">
                    <strong>Lexical Resource</strong>
                    <div id="lexicalScore">7.0</div>
                </div>
                <div class="band-item">
                    <strong>Grammar & Accuracy</strong>
                    <div id="grammarScore">6.5</div>
                </div>
            </div>

            <div class="feedback-section" id="feedbackSection">
                <h4>Nova Micro Feedback</h4>
                <p id="mainFeedback">Loading detailed feedback...</p>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 15px;">
                    <div>
                        <h5>Strengths</h5>
                        <ul id="strengthsList"></ul>
                    </div>
                    <div>
                        <h5>Areas for Improvement</h5>
                        <ul id="improvementsList"></ul>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let timeRemaining = 40 * 60; // 40 minutes in seconds
        let timerInterval = null;
        let assessmentSubmitted = false;
        
        const essayText = document.getElementById('essayText');
        const wordCount = document.getElementById('wordCount');
        const minWords = document.getElementById('minWords');
        const submitBtn = document.getElementById('submitBtn');
        const saveBtn = document.getElementById('saveBtn');
        const status = document.getElementById('status');
        const timer = document.getElementById('timer');
        const assessmentResult = document.getElementById('assessmentResult');
        
        // Start timer
        function startTimer() {{
            timerInterval = setInterval(() => {{
                timeRemaining--;
                const minutes = Math.floor(timeRemaining / 60);
                const seconds = timeRemaining % 60;
                timer.textContent = `${{minutes}}:${{seconds.toString().padStart(2, '0')}}`;
                
                if (timeRemaining <= 0) {{
                    clearInterval(timerInterval);
                    timer.textContent = "Time's up!";
                    if (!assessmentSubmitted) {{
                        submitEssay();
                    }}
                }}
            }}, 1000);
        }}
        
        // Update word count and enable/disable submit button
        essayText.addEventListener('input', function() {{
            const words = this.value.trim().split(/\\s+/).filter(word => word.length > 0);
            const currentWordCount = words.length;
            wordCount.textContent = currentWordCount;
            
            // Enable submit button if minimum word count is met
            if (currentWordCount >= parseInt(minWords.textContent)) {{
                submitBtn.disabled = false;
                submitBtn.className = 'btn btn-primary';
                status.textContent = 'Ready for Nova Micro assessment';
            }} else {{
                submitBtn.disabled = true;
                submitBtn.className = 'btn btn-disabled';
                status.textContent = `Write at least ${{minWords.textContent}} words to enable assessment`;
            }}
        }});
        
        // Submit essay for Nova Micro assessment
        async function submitEssay() {{
            if (assessmentSubmitted) return;
            
            assessmentSubmitted = true;
            submitBtn.disabled = true;
            submitBtn.textContent = 'Submitting to Nova Micro...';
            status.textContent = 'Nova Micro is analyzing your writing...';
            
            try {{
                const response = await fetch('/api/nova-micro/writing', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        essay_text: essayText.value,
                        prompt: document.getElementById('taskPrompt').textContent,
                        assessment_type: '{assessment_type}',
                        session_id: '{session_id}',
                        user_email: '{user_email}'
                    }})
                }});
                
                const result = await response.json();
                
                if (result.success) {{
                    displayAssessmentResults(result.assessment_result);
                    status.textContent = 'Nova Micro assessment completed successfully';
                }} else {{
                    status.textContent = 'Assessment error: ' + (result.error || 'Unknown error');
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Retry Assessment';
                    assessmentSubmitted = false;
                }}
            }} catch (error) {{
                console.error('Assessment error:', error);
                status.textContent = 'Connection error. Please try again.';
                submitBtn.disabled = false;
                submitBtn.textContent = 'Retry Assessment';
                assessmentSubmitted = false;
            }}
        }}
        
        // Display Nova Micro assessment results
        function displayAssessmentResults(result) {{
            document.getElementById('overallScore').textContent = result.overall_band_score;
            document.getElementById('taskScore').textContent = result.task_achievement;
            document.getElementById('coherenceScore').textContent = result.coherence_cohesion;
            document.getElementById('lexicalScore').textContent = result.lexical_resource;
            document.getElementById('grammarScore').textContent = result.grammatical_accuracy;
            document.getElementById('mainFeedback').textContent = result.feedback;
            
            // Display strengths and improvements
            const strengthsList = document.getElementById('strengthsList');
            const improvementsList = document.getElementById('improvementsList');
            
            strengthsList.innerHTML = '';
            improvementsList.innerHTML = '';
            
            if (result.detailed_feedback) {{
                result.detailed_feedback.strengths.forEach(strength => {{
                    const li = document.createElement('li');
                    li.textContent = strength;
                    strengthsList.appendChild(li);
                }});
                
                result.detailed_feedback.improvements.forEach(improvement => {{
                    const li = document.createElement('li');
                    li.textContent = improvement;
                    improvementsList.appendChild(li);
                }});
            }}
            
            assessmentResult.style.display = 'block';
            assessmentResult.scrollIntoView({{ behavior: 'smooth' }});
        }}
        
        // Save draft functionality
        saveBtn.addEventListener('click', function() {{
            localStorage.setItem('essay_draft_{session_id}', essayText.value);
            status.textContent = 'Draft saved locally';
            setTimeout(() => {{
                status.textContent = essayText.value.trim() ? 'Continue writing...' : 'Start writing to enable assessment...';
            }}, 2000);
        }});
        
        // Submit button click handler
        submitBtn.addEventListener('click', submitEssay);
        
        // Load saved draft if available
        window.addEventListener('load', function() {{
            const savedDraft = localStorage.getItem('essay_draft_{session_id}');
            if (savedDraft) {{
                essayText.value = savedDraft;
                essayText.dispatchEvent(new Event('input'));
            }}
            
            startTimer();
        }});
    </script>
</body>
</html>
"""

def handle_maya_introduction(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Maya's auto-start introduction for speaking assessments"""
    try:
        assessment_type = data.get('assessment_type')
        user_email = data.get('user_email')
        session_id = data.get('session_id')
        
        # Get assessment rubric and Nova Sonic prompts
        rubric = aws_mock.get_assessment_rubric(assessment_type)
        nova_prompts = rubric.get('nova_sonic_prompts', {}) if rubric else {}
        
        # Generate Maya's introduction based on assessment type
        if 'academic' in assessment_type:
            introduction = f"Hello, I'm Maya, your IELTS examiner. Today we'll be conducting the Academic Speaking test. This assessment has three parts: familiar topics, a long turn where you'll speak for 2 minutes, and an abstract discussion. Let's begin with Part 1. Can you tell me your name and where you're from?"
        else:
            introduction = f"Hello, I'm Maya, your IELTS examiner. Today we'll be conducting the General Training Speaking test. We'll cover everyday topics and practical situations. Let's start with some questions about yourself. What's your name and what do you do for work?"
        
        print(f"[CLOUDWATCH] Maya introduction started for {user_email} - {assessment_type}")
        
        # In production, this would call Nova Sonic to generate audio
        # For now, return text response with mock audio URL
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'introduction': introduction,
                'audio_url': '/api/maya/audio/introduction.mp3',  # Mock audio URL
                'assessment_part': 1,
                'nova_sonic_status': 'connected'
            })
        }
        
    except Exception as e:
        print(f"[CLOUDWATCH] Maya introduction error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }

def handle_maya_conversation(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Maya's conversation responses during speaking assessment"""
    try:
        user_message = data.get('user_message')
        assessment_type = data.get('assessment_type')
        session_id = data.get('session_id')
        
        # Get assessment rubric for context
        rubric = aws_mock.get_assessment_rubric(assessment_type)
        nova_prompts = rubric.get('nova_sonic_prompts', {}) if rubric else {}
        
        # Generate Maya's response based on user input
        # In production, this would use Nova Sonic bi-directional streaming
        if 'name' in user_message.lower() and 'from' in user_message.lower():
            response = "Thank you. Now, let's talk about your work. What do you do for a living, and how long have you been doing this job?"
        elif 'work' in user_message.lower() or 'job' in user_message.lower():
            response = "That's interesting. What do you enjoy most about your work? And what would you like to change about it if you could?"
        else:
            response = "I see. Let's move to another topic. Can you tell me about your hometown? What's it like there?"
        
        print(f"[CLOUDWATCH] Maya conversation - User: {user_message[:50]}...")
        
        # Store conversation in assessment results
        aws_mock.store_assessment_result({
            'result_id': f"{session_id}_{int(time.time())}",
            'user_email': data.get('user_email', 'unknown'),
            'assessment_type': assessment_type,
            'conversation_turn': {
                'user_message': user_message,
                'maya_response': response,
                'timestamp': datetime.utcnow().isoformat()
            }
        })
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'response': response,
                'audio_url': '/api/maya/audio/response.mp3',  # Mock audio URL
                'assessment_part': 1,
                'continue_conversation': True
            })
        }
        
    except Exception as e:
        print(f"[CLOUDWATCH] Maya conversation error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }

def handle_nova_micro_writing(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Nova Micro writing assessment requests"""
    try:
        essay_text = data.get('essay_text', '')
        prompt = data.get('prompt', '')
        assessment_type = data.get('assessment_type', 'academic_writing')
        session_id = data.get('session_id')
        
        if not essay_text or not prompt:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Essay text and prompt are required'
                })
            }
        
        # Get assessment rubric for Nova Micro prompts
        rubric = aws_mock.get_assessment_rubric(assessment_type)
        nova_prompts = rubric.get('nova_micro_prompts', {}) if rubric else {}
        
        # Analyze essay using Nova Micro criteria
        word_count = len(essay_text.split())
        min_words = 250 if 'task_2' in assessment_type else 150
        
        # Task Achievement/Response analysis
        task_score = 7.0 if word_count >= min_words else 6.0
        if 'argument' in essay_text.lower() and 'conclusion' in essay_text.lower():
            task_score += 0.5
        
        # Coherence and Cohesion analysis
        coherence_score = 6.5
        if 'however' in essay_text.lower() or 'furthermore' in essay_text.lower():
            coherence_score += 0.5
        
        # Lexical Resource analysis
        lexical_score = 7.0 if len(set(essay_text.lower().split())) > 100 else 6.0
        
        # Grammatical Range and Accuracy
        grammar_score = 6.5
        if '.' in essay_text and ',' in essay_text:
            grammar_score += 0.5
        
        overall_score = round((task_score + coherence_score + lexical_score + grammar_score) / 4, 1)
        
        assessment_result = {
            'task_achievement': task_score,
            'coherence_cohesion': coherence_score,
            'lexical_resource': lexical_score,
            'grammatical_accuracy': grammar_score,
            'overall_band_score': overall_score,
            'word_count': word_count,
            'feedback': f"Your essay demonstrates {overall_score} band level writing. Strong areas include task response and lexical variety. Consider improving coherence devices and grammatical complexity.",
            'detailed_feedback': {
                'strengths': ['Clear position', 'Appropriate length', 'Good vocabulary range'],
                'improvements': ['Use more linking words', 'Vary sentence structures', 'Check minor grammar errors']
            },
            'processed_by': 'Nova Micro',
            'assessment_type': assessment_type
        }
        
        # Store assessment result
        if session_id:
            aws_mock.store_assessment_result({
                'result_id': f"{session_id}_{int(time.time())}",
                'user_email': data.get('user_email', 'unknown'),
                'assessment_type': assessment_type,
                'essay_text': essay_text,
                'prompt': prompt,
                'assessment_result': assessment_result,
                'created_at': datetime.utcnow().isoformat()
            })
        
        print(f"[CLOUDWATCH] Nova Micro assessment completed - Overall band: {overall_score}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'assessment_result': assessment_result,
                'nova_micro_status': 'completed'
            })
        }
        
    except Exception as e:
        print(f"[CLOUDWATCH] Nova Micro writing error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }

def handle_nova_micro_submit(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle writing assessment submission"""
    try:
        return handle_nova_micro_writing(data)
    except Exception as e:
        print(f"[CLOUDWATCH] Nova Micro submit error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }

def handle_apple_purchase_verification(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Apple App Store in-app purchase verification"""
    try:
        receipt_data = data.get('receipt_data')
        product_id = data.get('product_id')
        
        if not receipt_data or not product_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Missing receipt_data or product_id'
                })
            }
        
        print(f"[CLOUDWATCH] Apple purchase verification: {product_id}")
        
        # In development environment, simulate successful verification
        # In production, this would verify with Apple's App Store servers
        verification_result = {
            'success': True,
            'product_id': product_id,
            'transaction_id': f"apple_txn_{int(time.time())}",
            'verified': True,
            'environment': 'development'
        }
        
        # Store purchase record in DynamoDB
        purchase_record = {
            'transaction_id': verification_result['transaction_id'],
            'product_id': product_id,
            'platform': 'apple',
            'verified_at': datetime.utcnow().isoformat(),
            'receipt_data': receipt_data[:50] + "..." if len(receipt_data) > 50 else receipt_data
        }
        
        # Store in mock DynamoDB purchase records table
        aws_mock.purchase_records_table.put_item(purchase_record)
        
        print(f"[CLOUDWATCH] Apple purchase verified: {verification_result['transaction_id']}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(verification_result)
        }
        
    except Exception as e:
        print(f"[CLOUDWATCH] Apple purchase verification error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'success': False, 'error': str(e)})
        }

def handle_google_purchase_verification(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Google Play Store in-app purchase verification"""
    try:
        purchase_token = data.get('purchase_token')
        product_id = data.get('product_id')
        
        if not purchase_token or not product_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Missing purchase_token or product_id'
                })
            }
        
        print(f"[CLOUDWATCH] Google purchase verification: {product_id}")
        
        # In development environment, simulate successful verification
        # In production, this would verify with Google Play Developer API
        verification_result = {
            'success': True,
            'product_id': product_id,
            'transaction_id': f"google_txn_{int(time.time())}",
            'verified': True,
            'environment': 'development'
        }
        
        # Store purchase record in DynamoDB
        purchase_record = {
            'transaction_id': verification_result['transaction_id'],
            'product_id': product_id,
            'platform': 'google',
            'verified_at': datetime.utcnow().isoformat(),
            'purchase_token': purchase_token[:50] + "..." if len(purchase_token) > 50 else purchase_token
        }
        
        # Store in mock DynamoDB purchase records table
        aws_mock.purchase_records_table.put_item(purchase_record)
        
        print(f"[CLOUDWATCH] Google purchase verified: {verification_result['transaction_id']}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(verification_result)
        }
        
    except Exception as e:
        print(f"[CLOUDWATCH] Google purchase verification error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'success': False, 'error': str(e)})
        }

def handle_website_qr_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle website QR authentication request - generates unique QR for website login"""
    try:
        # Generate unique website authentication token
        website_token_id = str(uuid.uuid4())
        
        # Create QR data with unique identifier and domain verification
        qr_data = {
            'type': 'website_auth',
            'token_id': website_token_id,
            'domain': 'ieltsaiprep.com',
            'timestamp': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(minutes=10)).isoformat()
        }
        
        # Store authentication token in DynamoDB with pending status
        auth_token = {
            'token_id': website_token_id,
            'type': 'website_auth',
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(minutes=10)).isoformat(),
            'authenticated_user': None,
            'user_products': None
        }
        
        aws_mock.store_qr_token(auth_token)
        
        # Generate QR code image
        qr_code_image = generate_qr_code(json.dumps(qr_data))
        
        print(f"[CLOUDWATCH] Website QR token generated: {website_token_id}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'token_id': website_token_id,
                'qr_code_image': qr_code_image,
                'expires_at': auth_token['expires_at'],
                'expires_in_minutes': 10
            })
        }
        
    except Exception as e:
        print(f"[CLOUDWATCH] Website QR request error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'success': False, 'error': str(e)})
        }

def handle_website_auth_check(data: Dict[str, Any]) -> Dict[str, Any]:
    """Check if website QR token has been authenticated by mobile app"""
    try:
        token_id = data.get('token_id')
        
        if not token_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'authenticated': False, 'error': 'Missing token_id'})
            }
        
        # Get token from DynamoDB
        token_data = aws_mock.get_qr_token(token_id)
        
        if not token_data:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'authenticated': False, 'expired': True})
            }
        
        # Check if token has expired
        expires_at = datetime.fromisoformat(token_data['expires_at'])
        if datetime.utcnow() > expires_at:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'authenticated': False, 'expired': True})
            }
        
        # Check authentication status
        if token_data.get('status') == 'authenticated':
            # Create website session for authenticated user
            session_id = f"web_session_{int(time.time())}_{token_id[:8]}"
            session_data = {
                'session_id': session_id,
                'user_email': token_data['authenticated_user'],
                'products': token_data['user_products'],
                'created_at': datetime.utcnow().isoformat(),
                'expires_at': time.time() + 3600,  # 1 hour
                'auth_method': 'mobile_qr'
            }
            
            aws_mock.create_session(session_data)
            
            print(f"[CLOUDWATCH] Website session created: {session_id} for {token_data['authenticated_user']}")
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Set-Cookie': f'web_session_id={session_id}; Max-Age=3600; Path=/'
                },
                'body': json.dumps({
                    'authenticated': True,
                    'user_email': token_data['authenticated_user'],
                    'products': token_data['user_products'],
                    'session_id': session_id
                })
            }
        else:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'authenticated': False, 'waiting': True})
            }
            
    except Exception as e:
        print(f"[CLOUDWATCH] Website auth check error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'authenticated': False, 'error': str(e)})
        }

def handle_mobile_qr_scan(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle mobile app scanning website QR code - authenticates specific user"""
    try:
        qr_data = data.get('qr_data')
        user_email = data.get('user_email')
        user_products = data.get('user_products', [])
        
        if not qr_data or not user_email:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Missing qr_data or user_email'
                })
            }
        
        # Parse QR data
        try:
            qr_info = json.loads(qr_data)
        except json.JSONDecodeError:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Invalid QR code format'
                })
            }
        
        # Validate QR code structure
        if (qr_info.get('type') != 'website_auth' or 
            qr_info.get('domain') != 'ieltsaiprep.com' or 
            not qr_info.get('token_id')):
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Invalid QR code - not an IELTS GenAI Prep authentication code'
                })
            }
        
        token_id = qr_info['token_id']
        
        # Get and validate token
        token_data = aws_mock.get_qr_token(token_id)
        
        if not token_data:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'success': False,
                    'error': 'QR code expired or invalid'
                })
            }
        
        # Check if already used
        if token_data.get('status') == 'authenticated':
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'success': False,
                    'error': 'QR code already used'
                })
            }
        
        # Update token with user authentication
        token_data['status'] = 'authenticated'
        token_data['authenticated_user'] = user_email
        token_data['user_products'] = user_products
        token_data['authenticated_at'] = datetime.utcnow().isoformat()
        
        aws_mock.store_qr_token(token_data)
        
        print(f"[CLOUDWATCH] Mobile QR scan successful: {user_email} authenticated token {token_id}")
        print(f"[CLOUDWATCH] User products: {user_products}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'message': 'Authentication successful',
                'user_email': user_email,
                'products': user_products
            })
        }
        
    except Exception as e:
        print(f"[CLOUDWATCH] Mobile QR scan error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'success': False, 'error': str(e)})
        }

def handle_generate_qr(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle QR token generation after purchase verification"""
    try:
        user_email = data.get('user_email')
        product_id = data.get('product_id')
        purchase_verified = data.get('purchase_verified', False)
        
        if not all([user_email, product_id, purchase_verified]):
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Missing required fields: user_email, product_id, purchase_verified'
                })
            }
        
        # Generate unique token
        token_id = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        
        # Store in AuthTokens table (DynamoDB simulation)
        token_data = {
            'token_id': token_id,
            'user_email': user_email,
            'product_id': product_id,
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': int(expires_at.timestamp()),
            'ttl': int(expires_at.timestamp()),
            'used': False,
            'purchase_verified': purchase_verified
        }
        
        # Store token using AWS mock service
        aws_mock.store_qr_token(token_data)
        
        # Generate QR code image
        qr_code_image = generate_qr_code(token_id)
        
        print(f"[CLOUDWATCH] QR Token Generated: {token_id} for {user_email} - Product: {product_id}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'token_id': token_id,
                'user_email': user_email,
                'product_id': product_id,
                'expires_at': expires_at.isoformat(),
                'expires_in_minutes': 10,
                'qr_code_image': f'data:image/png;base64,{qr_code_image}'
            })
        }
        
    except Exception as e:
        print(f"[CLOUDWATCH] QR Generation error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'success': False, 'error': str(e)})
        }

def handle_verify_qr(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle QR token verification and session creation"""
    try:
        token_id = data.get('token')
        
        if not token_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'success': False, 'error': 'Token required'})
            }
        
        print(f"[CLOUDWATCH] QR Verification attempt: {token_id}")
        
        # Retrieve token from AuthTokens table
        token_data = aws_mock.get_qr_token(token_id)
        
        if not token_data:
            print(f"[CLOUDWATCH] QR Verification failed: Invalid token {token_id}")
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'success': False, 'error': 'Invalid token'})
            }
        
        current_time = int(time.time())
        expires_at = token_data.get('expires_at', 0)
        
        # Check token expiry
        if current_time > expires_at:
            print(f"[CLOUDWATCH] QR Verification failed: Expired token {token_id}")
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'success': False,
                    'error': 'QR code expired. Please generate a new one from your mobile app.'
                })
            }
        
        # Check if token already used
        if token_data.get('used'):
            print(f"[CLOUDWATCH] QR Verification failed: Token already used {token_id}")
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'success': False,
                    'error': 'QR code already used. Please generate a new one.'
                })
            }
        
        # Mark token as used
        token_data['used'] = True
        token_data['used_at'] = datetime.utcnow().isoformat()
        
        # Create ElastiCache session (1-hour expiry)
        session_id = f"session_{int(time.time())}_{token_id[:8]}"
        session_data = {
            'session_id': session_id,
            'user_email': token_data['user_email'],
            'product_id': token_data.get('product_id'),
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': time.time() + 3600,
            'authenticated_via': 'qr_token',
            'purchased_products': [token_data.get('product_id')]
        }
        
        # Store session using AWS mock service
        aws_mock.create_session(session_data)
        
        print(f"[CLOUDWATCH] QR Verification successful: {token_id} -> Session: {session_id}")
        print(f"[CLOUDWATCH] User {token_data['user_email']} authenticated with products: {session_data['purchased_products']}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Set-Cookie': f'qr_session_id={session_id}; Max-Age=3600; Path=/'
            },
            'body': json.dumps({
                'success': True,
                'message': 'Authentication successful',
                'session_id': session_id,
                'user_email': token_data['user_email'],
                'redirect_url': '/profile'
            })
        }
        
    except Exception as e:
        print(f"[CLOUDWATCH] QR Verification error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'success': False, 'error': str(e)})
        }

def handle_assessment_access(path: str, headers: Dict[str, Any]) -> Dict[str, Any]:
    """Handle assessment access with session verification"""
    try:
        # Extract assessment type from path
        assessment_type = path.split('/')[-1]
        
        # Get session from cookie header
        cookie_header = headers.get('Cookie', headers.get('cookie', ''))
        session_id = None
        
        for cookie in cookie_header.split(';'):
            if 'qr_session_id=' in cookie:
                session_id = cookie.split('qr_session_id=')[1].strip()
                break
        
        if not session_id:
            print(f"[CLOUDWATCH] Assessment access denied: No session for {assessment_type}")
            return {
                'statusCode': 302,
                'headers': {'Location': '/'},
                'body': ''
            }
        
        # Verify session in ElastiCache
        session_data = aws_mock.get_session(session_id)
        
        if not session_data:
            print(f"[CLOUDWATCH] Assessment access denied: Invalid session for {assessment_type}")
            return {
                'statusCode': 302,
                'headers': {'Location': '/'},
                'body': ''
            }
        
        user_email = session_data['user_email']
        purchased_products = session_data.get('purchased_products', [])
        
        # Check if user has purchased this assessment type
        if assessment_type not in purchased_products:
            print(f"[CLOUDWATCH] Assessment access denied: {user_email} has not purchased {assessment_type}")
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/html'},
                'body': f"""
                <!DOCTYPE html>
                <html>
                <head><title>Access Restricted</title></head>
                <body style="font-family: Arial; padding: 40px; background: #f5f5f5;">
                    <div style="background: white; padding: 30px; border-radius: 10px; max-width: 500px; margin: 0 auto;">
                        <h2>🔒 Assessment Access Restricted</h2>
                        <p>You need to purchase the <strong>{assessment_type.replace('_', ' ').title()}</strong> assessment to access this content.</p>
                        <div style="margin-top: 20px;">
                            <a href="/test-mobile" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Purchase on Mobile App</a>
                        </div>
                    </div>
                </body>
                </html>
                """
            }
        
        print(f"[CLOUDWATCH] Assessment access granted: {user_email} accessing {assessment_type}")
        
        # Load appropriate assessment template based on type
        template_content = get_assessment_template(assessment_type, user_email, session_id)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': template_content
        }
        
    except Exception as e:
        print(f"[CLOUDWATCH] Assessment access error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'success': False, 'error': str(e)})
        }

def handle_health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    try:
        health_data = aws_mock.get_health_status()
        health_data['lambda'] = {
            'status': 'healthy',
            'memory_usage': '128MB',
            'cold_starts': 0,
            'architecture': 'serverless'
        }
        
        print(f"[CLOUDWATCH] Health check: healthy")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(health_data)
        }
        
    except Exception as e:
        print(f"[CLOUDWATCH] Health check failed: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'status': 'unhealthy', 'error': str(e)})
        }

def handle_user_registration(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle user registration with DynamoDB storage"""
    try:
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Validate input
        if not name or not email or not password:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'success': False, 'message': 'All fields are required'})
            }
        
        if len(password) < 6:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'success': False, 'message': 'Password must be at least 6 characters'})
            }
        
        # Check if user already exists
        existing_user = aws_mock.users_table.get_item(email)
        if existing_user:
            return {
                'statusCode': 409,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'success': False, 'message': 'User already exists with this email'})
            }
        
        # Hash password
        import hashlib
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Create user record
        user_data = {
            'user_id': email,
            'email': email,
            'name': name,
            'password_hash': password_hash,
            'created_at': datetime.utcnow().isoformat(),
            'products': [],
            'last_login': None
        }
        
        # Store in DynamoDB
        success = aws_mock.users_table.put_item(user_data)
        
        if success:
            aws_mock.log_event('UserAuth', f'User registered: {email}')
            return {
                'statusCode': 201,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'success': True, 
                    'user': {
                        'name': name,
                        'email': email,
                        'products': []
                    }
                })
            }
        else:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'success': False, 'message': 'Failed to create user account'})
            }
            
    except Exception as e:
        print(f"[CLOUDWATCH] User registration error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'success': False, 'message': 'Registration failed'})
        }

def handle_user_login(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle user login with DynamoDB authentication"""
    try:
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Validate input
        if not email or not password:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'success': False, 'message': 'Email and password are required'})
            }
        
        # Get user from DynamoDB
        user_data = aws_mock.users_table.get_item(email)
        if not user_data:
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'success': False, 'message': 'Invalid email or password'})
            }
        
        # Verify password
        import hashlib
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if user_data['password_hash'] != password_hash:
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'success': False, 'message': 'Invalid email or password'})
            }
        
        # Update last login
        aws_mock.users_table.update_item(email, {
            'last_login': datetime.utcnow().isoformat()
        })
        
        # Create session
        session_id = f"mobile_session_{int(time.time())}_{email.replace('@', '_').replace('.', '_')}"
        session_data = {
            'user_email': email,
            'created_at': time.time(),
            'type': 'mobile_app'
        }
        aws_mock.create_session(session_data)
        
        aws_mock.log_event('UserAuth', f'User logged in: {email}')
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'success': True,
                'user': {
                    'name': user_data['name'],
                    'email': user_data['email'],
                    'products': user_data.get('products', [])
                },
                'session_id': session_id
            })
        }
        
    except Exception as e:
        print(f"[CLOUDWATCH] User login error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'success': False, 'message': 'Login failed'})
        }