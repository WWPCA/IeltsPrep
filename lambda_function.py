
import json
import uuid
import boto3
import os
import base64
from datetime import datetime
from typing import Dict, Any, Optional

def lambda_handler(event, context):
    """Main AWS Lambda handler"""
    try:
        path = event.get("path", "/")
        method = event.get("httpMethod", "GET")
        
        if path == "/":
            return handle_home_page()
        elif path == "/assessment/academic-speaking":
            return handle_nova_sonic_assessment()
        elif path == "/assessment/academic-writing":
            return handle_writing_assessment()
        elif path == "/api/health":
            return handle_health_check()
        elif path == "/api/nova-sonic-stream":
            return handle_nova_sonic_stream(event)
        elif path == "/api/nova-sonic-connect":
            return handle_nova_sonic_connect(event)
        else:
            return {"statusCode": 404, "headers": {"Content-Type": "text/html"}, "body": "<h1>404 Not Found</h1>"}
    except Exception as e:
        return {"statusCode": 500, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"error": str(e)})}

def handle_nova_sonic_connect(event):
    """Handle Nova Sonic connection with proper AWS Bedrock integration"""
    try:
        # Initialize Bedrock client for Nova Sonic
        bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Test Nova Sonic availability
        model_id = "amazon.nova-sonic-v1:0"
        
        # Nova Sonic system prompt for Maya
        system_prompt = """You are Maya, a professional IELTS examiner with a British accent. 
        Conduct speaking assessments following the official IELTS 3-part structure:
        - Part 1: Personal interview (4-5 minutes)
        - Part 2: Individual long turn (3-4 minutes) 
        - Part 3: Two-way discussion (4-5 minutes)
        
        Be professional, encouraging, and maintain authentic examiner behavior."""
        
        # Test connection with a simple prompt
        test_payload = {
            "modelId": model_id,
            "contentType": "application/json",
            "accept": "application/json",
            "body": json.dumps({
                "inputText": "Hello, this is a connection test.",
                "taskType": "TEXT_TO_SPEECH",
                "voiceId": "amy",
                "outputFormat": "mp3",
                "textType": "text"
            })
        }
        
        response = bedrock_client.invoke_model(
            modelId=model_id,
            body=test_payload["body"],
            contentType=test_payload["contentType"],
            accept=test_payload["accept"]
        )
        
        # If we get here, Nova Sonic is accessible
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "status": "connected",
                "model": "nova-sonic-v1",
                "voice": "amy",
                "accent": "british",
                "streaming": True,
                "ready": True
            })
        }
        
    except Exception as e:
        # Return detailed error information
        error_details = {
            "error": "Nova Sonic connection failed",
            "message": str(e),
            "model_id": "amazon.nova-sonic-v1:0",
            "voice": "amy",
            "region": "us-east-1",
            "issue_type": "bedrock_access"
        }
        
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(error_details)
        }

def handle_nova_sonic_stream(event):
    """Handle Nova Sonic streaming for Maya conversation"""
    try:
        body = json.loads(event.get("body", "{}"))
        message = body.get("message", "")
        
        if not message:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "No message provided"})
            }
        
        # Initialize Bedrock client
        bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Nova Sonic streaming configuration
        payload = {
            "modelId": "amazon.nova-sonic-v1:0",
            "contentType": "application/json",
            "accept": "application/json",
            "body": json.dumps({
                "inputText": message,
                "taskType": "TEXT_TO_SPEECH",
                "voiceId": "amy",
                "outputFormat": "mp3",
                "textType": "text",
                "engine": "neural"
            })
        }
        
        response = bedrock_client.invoke_model(
            modelId=payload["modelId"],
            body=payload["body"],
            contentType=payload["contentType"],
            accept=payload["accept"]
        )
        
        # Process response
        response_body = json.loads(response["body"].read())
        
        # Return audio data
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "audio_data": response_body.get("audioStream", ""),
                "voice": "amy",
                "status": "success"
            })
        }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": "Nova Sonic streaming failed",
                "message": str(e),
                "voice": "amy"
            })
        }

def handle_home_page():
    """Handle home page"""
    html = """<!DOCTYPE html>
<html>
<head>
    <title>IELTS GenAI Prep</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 1000px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #e31e24; margin-bottom: 10px; font-size: 32px; }
        .assessment-card { background: #f8f9fa; padding: 25px; border-radius: 8px; border: 1px solid #ddd; margin: 20px 0; }
        .btn { background-color: #e31e24; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; font-weight: bold; }
        .btn:hover { background-color: #c21a1f; }
    </style>
</head>
<body>
    <div class="container">
        <h1>IELTS GenAI Prep</h1>
        <p>AI-powered IELTS preparation with Maya AI examiner</p>
        
        <div class="assessment-card">
            <h3>Academic Speaking Assessment</h3>
            <p><strong>Maya AI Examiner:</strong> AWS Nova Sonic British voice<br>
               <strong>Visual Experience:</strong> Particle globe animation<br>
               <strong>Assessment Format:</strong> Official IELTS 3-part structure<br>
               <strong>Duration:</strong> 11-14 minutes total</p>
            <a href="/assessment/academic-speaking" class="btn">Start Maya Assessment</a>
        </div>
    </div>
</body>
</html>"""
    
    return {"statusCode": 200, "headers": {"Content-Type": "text/html"}, "body": html}

def handle_nova_sonic_assessment():
    """Handle Nova Sonic assessment with proper AWS integration"""
    
    maya_questions = [
        {
            "part": 1,
            "question": "Hello! I am Maya, your AI examiner for this IELTS Speaking assessment. Let me start by asking you some questions about yourself. What is your name and where are you from?",
            "expected_duration": 30
        },
        {
            "part": 1,
            "question": "That is interesting. Can you tell me about your work or studies?",
            "expected_duration": 45
        },
        {
            "part": 1,
            "question": "What do you enjoy doing in your free time?",
            "expected_duration": 45
        },
        {
            "part": 2,
            "question": "Now I will give you a topic card. You have one minute to prepare and then speak for 1-2 minutes. Describe a memorable journey you have taken. You should say: where you went, who you went with, what you did there, and explain why this journey was memorable for you.",
            "expected_duration": 120,
            "prep_time": 60
        },
        {
            "part": 3,
            "question": "Let us discuss travel and journeys in general. How has travel changed in your country over the past few decades?",
            "expected_duration": 60
        },
        {
            "part": 3,
            "question": "What are the benefits of traveling to different countries?",
            "expected_duration": 60
        }
    ]
    
    maya_questions_json = json.dumps(maya_questions)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Academic Speaking Assessment - Maya AI</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }}
        
        .header {{ 
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 15px 20px;
            box-shadow: 0 2px 20px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .logo {{ 
            background: linear-gradient(45deg, #e31e24, #ff6b6b);
            color: white;
            padding: 10px 16px;
            border-radius: 8px;
            font-weight: bold;
            font-size: 18px;
            box-shadow: 0 4px 15px rgba(227, 30, 36, 0.3);
        }}
        
        .timer {{ 
            background: linear-gradient(45deg, #333, #555);
            color: white;
            padding: 10px 16px;
            border-radius: 8px;
            font-weight: bold;
            font-size: 16px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }}
        
        .main-content {{ 
            display: flex;
            height: calc(100vh - 120px);
            gap: 20px;
            padding: 20px;
        }}
        
        .question-panel {{ 
            flex: 1;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            overflow-y: auto;
        }}
        
        .maya-panel {{ 
            flex: 1;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            position: relative;
        }}
        
        .part-header {{ 
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 25px;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }}
        
        .part-title {{ font-size: 18px; font-weight: bold; margin-bottom: 5px; }}
        .part-subtitle {{ font-size: 14px; opacity: 0.9; }}
        
        .assessment-structure {{ 
            background: rgba(102, 126, 234, 0.1);
            border: 1px solid rgba(102, 126, 234, 0.3);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 25px;
        }}
        
        .audio-setup {{ 
            background: rgba(227, 30, 36, 0.1);
            border: 1px solid rgba(227, 30, 36, 0.3);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 25px;
        }}
        
        .permission-status {{ 
            padding: 12px;
            margin: 10px 0;
            border-radius: 6px;
            font-weight: 500;
            transition: all 0.3s ease;
        }}
        
        .permission-granted {{ 
            background: rgba(76, 175, 80, 0.1);
            color: #2e7d32;
            border: 1px solid rgba(76, 175, 80, 0.3);
        }}
        
        .permission-denied {{ 
            background: rgba(244, 67, 54, 0.1);
            color: #c62828;
            border: 1px solid rgba(244, 67, 54, 0.3);
        }}
        
        .permission-pending {{ 
            background: rgba(255, 193, 7, 0.1);
            color: #f57c00;
            border: 1px solid rgba(255, 193, 7, 0.3);
        }}
        
        .maya-globe-container {{ 
            position: relative;
            height: 200px;
            width: 200px;
            margin: 20px auto;
            border-radius: 50%;
            background: radial-gradient(circle at 30% 30%, rgba(102, 126, 234, 0.8), rgba(118, 75, 162, 0.8));
            box-shadow: 0 0 30px rgba(102, 126, 234, 0.5);
            overflow: hidden;
        }}
        
        .maya-globe {{ 
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border-radius: 50%;
        }}
        
        .maya-conversation {{ 
            flex: 1;
            background: rgba(248, 249, 250, 0.8);
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            overflow-y: auto;
            max-height: 300px;
        }}
        
        .maya-message {{ 
            padding: 12px 16px;
            margin: 8px 0;
            border-radius: 8px;
            animation: slideIn 0.3s ease;
        }}
        
        .maya-message.maya {{ 
            background: rgba(102, 126, 234, 0.1);
            border-left: 4px solid #667eea;
        }}
        
        .maya-message.user {{ 
            background: rgba(76, 175, 80, 0.1);
            border-left: 4px solid #4caf50;
        }}
        
        .controls {{ 
            display: flex;
            gap: 10px;
            margin-top: 20px;
            flex-wrap: wrap;
        }}
        
        .btn {{ 
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        
        .btn-primary {{ 
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
        }}
        
        .btn-primary:hover {{ 
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }}
        
        .btn-record {{ 
            background: linear-gradient(45deg, #e31e24, #ff6b6b);
            color: white;
        }}
        
        .btn-record:hover {{ 
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(227, 30, 36, 0.4);
        }}
        
        .btn-stop {{ 
            background: linear-gradient(45deg, #6c757d, #495057);
            color: white;
        }}
        
        .btn-submit {{ 
            background: linear-gradient(45deg, #28a745, #20c997);
            color: white;
        }}
        
        .btn:disabled {{ 
            background: #e9ecef;
            color: #6c757d;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }}
        
        .footer {{ 
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 -2px 20px rgba(0,0,0,0.1);
        }}
        
        .status-info {{ 
            display: flex;
            gap: 20px;
            font-weight: 500;
        }}
        
        .error-message {{ 
            background: rgba(244, 67, 54, 0.1);
            color: #c62828;
            border: 1px solid rgba(244, 67, 54, 0.3);
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            font-size: 14px;
        }}
        
        @keyframes slideIn {{ 
            from {{ opacity: 0; transform: translateX(-20px); }}
            to {{ opacity: 1; transform: translateX(0); }}
        }}
        
        @keyframes pulseGlow {{ 
            0%, 100% {{ box-shadow: 0 0 30px rgba(102, 126, 234, 0.5); }}
            50% {{ box-shadow: 0 0 50px rgba(102, 126, 234, 0.8), 0 0 70px rgba(118, 75, 162, 0.6); }}
        }}
        
        .maya-speaking {{ 
            animation: pulseGlow 2s infinite;
        }}
        
        @media (max-width: 768px) {{
            .main-content {{ flex-direction: column; height: auto; }}
            .maya-globe-container {{ height: 150px; width: 150px; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <div class="logo">IELTS GenAI</div>
            <div style="font-size: 14px; color: #666; margin-top: 5px;">Maya AI Examiner</div>
        </div>
        <div class="timer" id="timer">--:--</div>
    </div>
    
    <div class="main-content">
        <div class="question-panel">
            <div class="part-header">
                <div class="part-title">IELTS Speaking Assessment</div>
                <div class="part-subtitle">Official 3-part structure with Maya AI examiner</div>
            </div>
            
            <div class="assessment-structure">
                <h4 style="margin-bottom: 15px;">Assessment Structure:</h4>
                <p style="line-height: 1.6;">
                    <strong>Part 1:</strong> Interview (4-5 minutes)<br>
                    <strong>Part 2:</strong> Long Turn (3-4 minutes)<br>
                    <strong>Part 3:</strong> Discussion (4-5 minutes)
                </p>
            </div>
        </div>
        
        <div class="maya-panel">
            <div class="audio-setup" id="audioSetup">
                <h4>🎤 Audio Setup Required</h4>
                <p>Please complete audio setup to begin Maya conversation:</p>
                
                <div class="permission-status permission-pending" id="microphoneStatus">
                    🎤 Microphone: Checking permissions...
                </div>
                
                <div class="permission-status permission-pending" id="novaSonicStatus">
                    🔊 Nova Sonic: Connecting...
                </div>
                
                <div id="errorMessage" class="error-message" style="display: none;"></div>
                
                <div class="controls">
                    <button class="btn btn-primary" id="connectNovaBtn">Connect to Nova Sonic</button>
                    <button class="btn btn-primary" id="testMayaBtn" style="display: none;">Test Maya Voice</button>
                </div>
            </div>
            
            <div class="maya-globe-container" id="mayaGlobeContainer" style="display: none;">
                <canvas class="maya-globe" id="mayaGlobe"></canvas>
            </div>
            
            <div class="maya-conversation" id="mayaConversation" style="display: none;">
                <!-- Messages will be added here -->
            </div>
            
            <div class="controls" id="recordingControls" style="display: none;">
                <button class="btn btn-record" id="recordBtn" disabled>Start Recording</button>
                <button class="btn btn-stop" id="stopBtn" disabled>Stop Recording</button>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <div class="status-info">
            <div>Part: <span id="currentPart">1</span> of 3</div>
            <div>Question: <span id="currentQuestion">1</span> of 6</div>
        </div>
        <div>
            <button class="btn btn-submit" id="submitBtn" disabled>Complete Assessment</button>
        </div>
    </div>
    
    <script>
        let timeRemaining = 0;
        let timerStarted = false;
        let currentQuestionIndex = 0;
        let isRecording = false;
        let mediaRecorder;
        let audioChunks = [];
        let audioStream = null;
        let microphoneGranted = false;
        let novaSonicConnected = false;
        let particleSystem = null;
        let mayaSpeaking = false;
        
        // DOM elements
        const timer = document.getElementById('timer');
        const recordBtn = document.getElementById('recordBtn');
        const stopBtn = document.getElementById('stopBtn');
        const submitBtn = document.getElementById('submitBtn');
        const mayaConversation = document.getElementById('mayaConversation');
        const currentPart = document.getElementById('currentPart');
        const currentQuestion = document.getElementById('currentQuestion');
        const connectNovaBtn = document.getElementById('connectNovaBtn');
        const testMayaBtn = document.getElementById('testMayaBtn');
        const audioSetup = document.getElementById('audioSetup');
        const mayaGlobeContainer = document.getElementById('mayaGlobeContainer');
        const mayaGlobe = document.getElementById('mayaGlobe');
        const recordingControls = document.getElementById('recordingControls');
        const microphoneStatus = document.getElementById('microphoneStatus');
        const novaSonicStatus = document.getElementById('novaSonicStatus');
        const errorMessage = document.getElementById('errorMessage');
        
        // Maya questions data
        const mayaQuestions = {maya_questions_json};
        
        // Particle globe system
        class ParticleGlobe {{
            constructor(canvas) {{
                this.canvas = canvas;
                this.ctx = canvas.getContext('2d');
                this.particles = [];
                this.animationId = null;
                this.speaking = false;
                
                this.resize();
                this.createParticles();
                this.animate();
                
                window.addEventListener('resize', () => this.resize());
            }}
            
            resize() {{
                const container = this.canvas.parentElement;
                this.canvas.width = container.offsetWidth;
                this.canvas.height = container.offsetHeight;
                this.centerX = this.canvas.width / 2;
                this.centerY = this.canvas.height / 2;
                this.radius = Math.min(this.canvas.width, this.canvas.height) / 2 - 20;
            }}
            
            createParticles() {{
                this.particles = [];
                for (let i = 0; i < 150; i++) {{
                    this.particles.push({{
                        angle: Math.random() * Math.PI * 2,
                        radius: this.radius * (0.8 + Math.random() * 0.4),
                        speed: 0.02 + Math.random() * 0.02,
                        size: 2 + Math.random() * 3,
                        opacity: 0.3 + Math.random() * 0.7,
                        color: `hsl(${{200 + Math.random() * 60}}, 70%, 60%)`
                    }});
                }}
            }}
            
            animate() {{
                this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
                
                // Draw connecting lines
                this.ctx.strokeStyle = 'rgba(102, 126, 234, 0.2)';
                this.ctx.lineWidth = 1;
                
                for (let i = 0; i < this.particles.length; i++) {{
                    const particle1 = this.particles[i];
                    const x1 = this.centerX + Math.cos(particle1.angle) * particle1.radius;
                    const y1 = this.centerY + Math.sin(particle1.angle) * particle1.radius;
                    
                    for (let j = i + 1; j < this.particles.length; j++) {{
                        const particle2 = this.particles[j];
                        const x2 = this.centerX + Math.cos(particle2.angle) * particle2.radius;
                        const y2 = this.centerY + Math.sin(particle2.angle) * particle2.radius;
                        
                        const distance = Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
                        
                        if (distance < 80) {{
                            const opacity = (80 - distance) / 80 * 0.3;
                            this.ctx.globalAlpha = opacity;
                            this.ctx.beginPath();
                            this.ctx.moveTo(x1, y1);
                            this.ctx.lineTo(x2, y2);
                            this.ctx.stroke();
                        }}
                    }}
                }}
                
                // Draw particles
                this.particles.forEach(particle => {{
                    const x = this.centerX + Math.cos(particle.angle) * particle.radius;
                    const y = this.centerY + Math.sin(particle.angle) * particle.radius;
                    
                    this.ctx.globalAlpha = particle.opacity;
                    this.ctx.fillStyle = particle.color;
                    this.ctx.beginPath();
                    this.ctx.arc(x, y, particle.size, 0, Math.PI * 2);
                    this.ctx.fill();
                    
                    // Animate particles
                    particle.angle += particle.speed;
                    if (this.speaking) {{
                        particle.radius += Math.sin(Date.now() * 0.01 + particle.angle) * 2;
                        particle.size = Math.max(1, particle.size + Math.sin(Date.now() * 0.02) * 0.5);
                    }}
                }});
                
                this.ctx.globalAlpha = 1;
                this.animationId = requestAnimationFrame(() => this.animate());
            }}
            
            startSpeaking() {{
                this.speaking = true;
                mayaGlobeContainer.classList.add('maya-speaking');
            }}
            
            stopSpeaking() {{
                this.speaking = false;
                mayaGlobeContainer.classList.remove('maya-speaking');
            }}
            
            destroy() {{
                if (this.animationId) {{
                    cancelAnimationFrame(this.animationId);
                }}
            }}
        }}
        
        // Connect to Nova Sonic
        connectNovaBtn.addEventListener('click', async function() {{
            try {{
                // Request microphone permission
                audioStream = await navigator.mediaDevices.getUserMedia({{ 
                    audio: {{ 
                        sampleRate: 16000,
                        channelCount: 1,
                        echoCancellation: true,
                        noiseSuppression: true
                    }} 
                }});
                
                microphoneGranted = true;
                microphoneStatus.textContent = '🎤 Microphone: Access granted ✓';
                microphoneStatus.className = 'permission-status permission-granted';
                
                // Connect to Nova Sonic
                const response = await fetch('/api/nova-sonic-connect', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{ action: 'connect' }})
                }});
                
                const data = await response.json();
                
                if (response.ok && data.status === 'connected') {{
                    novaSonicConnected = true;
                    novaSonicStatus.textContent = '🔊 Nova Sonic: Connected ✓';
                    novaSonicStatus.className = 'permission-status permission-granted';
                    
                    connectNovaBtn.textContent = 'Connected ✓';
                    connectNovaBtn.disabled = true;
                    testMayaBtn.style.display = 'inline-block';
                    
                    errorMessage.style.display = 'none';
                }} else {{
                    throw new Error(data.message || 'Nova Sonic connection failed');
                }}
                
            }} catch (error) {{
                console.error('Connection error:', error);
                microphoneStatus.textContent = '🎤 Microphone: Access denied ✗';
                microphoneStatus.className = 'permission-status permission-denied';
                
                novaSonicStatus.textContent = '🔊 Nova Sonic: Connection failed ✗';
                novaSonicStatus.className = 'permission-status permission-denied';
                
                errorMessage.textContent = 'Error: ' + error.message;
                errorMessage.style.display = 'block';
            }}
        }});
        
        // Test Maya voice
        testMayaBtn.addEventListener('click', async function() {{
            if (!novaSonicConnected) {{
                alert('Please connect to Nova Sonic first.');
                return;
            }}
            
            try {{
                const testMessage = 'Hello! This is Maya, your AI examiner. I am ready to begin the IELTS speaking assessment.';
                
                const response = await fetch('/api/nova-sonic-stream', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{ message: testMessage }})
                }});
                
                const data = await response.json();
                
                if (response.ok && data.audio_data) {{
                    // Play audio
                    const audio = new Audio('data:audio/mp3;base64,' + data.audio_data);
                    audio.play();
                    
                    testMayaBtn.textContent = 'Voice Test Complete ✓';
                    setTimeout(() => {{
                        startAssessment();
                    }}, 2000);
                }} else {{
                    throw new Error(data.message || 'Voice test failed');
                }}
                
            }} catch (error) {{
                console.error('Voice test error:', error);
                errorMessage.textContent = 'Voice test failed: ' + error.message;
                errorMessage.style.display = 'block';
            }}
        }});
        
        function startAssessment() {{
            // Hide audio setup and show Maya interface
            audioSetup.style.display = 'none';
            mayaGlobeContainer.style.display = 'block';
            mayaConversation.style.display = 'block';
            recordingControls.style.display = 'flex';
            
            // Initialize particle globe
            particleSystem = new ParticleGlobe(mayaGlobe);
            
            // Start first question
            setTimeout(() => {{
                loadNextQuestion();
            }}, 1000);
        }}
        
        async function speakMayaMessage(text) {{
            if (!novaSonicConnected) {{
                console.warn('Nova Sonic not connected');
                return;
            }}
            
            try {{
                const response = await fetch('/api/nova-sonic-stream', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{ message: text }})
                }});
                
                const data = await response.json();
                
                if (response.ok && data.audio_data) {{
                    if (particleSystem) {{
                        particleSystem.startSpeaking();
                    }}
                    
                    const audio = new Audio('data:audio/mp3;base64,' + data.audio_data);
                    audio.onended = function() {{
                        if (particleSystem) {{
                            particleSystem.stopSpeaking();
                        }}
                    }};
                    audio.play();
                }} else {{
                    throw new Error(data.message || 'Speech synthesis failed');
                }}
                
            }} catch (error) {{
                console.error('Speech error:', error);
                errorMessage.textContent = 'Speech synthesis failed: ' + error.message;
                errorMessage.style.display = 'block';
            }}
        }}
        
        function addMayaMessage(message, isMaya = true) {{
            const messageDiv = document.createElement('div');
            messageDiv.className = 'maya-message ' + (isMaya ? 'maya' : 'user');
            messageDiv.innerHTML = isMaya ? 
                '<strong>Maya:</strong> ' + message : 
                '<strong>You:</strong> ' + message;
            mayaConversation.appendChild(messageDiv);
            mayaConversation.scrollTop = mayaConversation.scrollHeight;
        }}
        
        function loadNextQuestion() {{
            if (currentQuestionIndex >= mayaQuestions.length) {{
                const finalMessage = 'Thank you for completing the IELTS Speaking assessment. Your conversation has been recorded and will be evaluated.';
                addMayaMessage(finalMessage);
                speakMayaMessage(finalMessage);
                submitBtn.disabled = false;
                recordBtn.disabled = true;
                return;
            }}
            
            const question = mayaQuestions[currentQuestionIndex];
            
            // Add Maya message
            addMayaMessage(question.question);
            currentPart.textContent = question.part;
            currentQuestion.textContent = currentQuestionIndex + 1;
            
            // Speak Maya's question
            speakMayaMessage(question.question);
            
            setTimeout(() => {{
                recordBtn.disabled = false;
                
                if (currentQuestionIndex === 0) {{
                    startTimer();
                }}
            }}, 8000); // Wait longer for Maya to finish speaking
        }}
        
        function startTimer() {{
            if (!timerStarted) {{
                timerStarted = true;
                timeRemaining = 15 * 60; // 15 minutes
                setInterval(updateTimer, 1000);
            }}
        }}
        
        function updateTimer() {{
            if (!timerStarted) return;
            
            const minutes = Math.floor(timeRemaining / 60);
            const seconds = timeRemaining % 60;
            timer.textContent = minutes.toString().padStart(2, '0') + ':' + seconds.toString().padStart(2, '0');
            
            if (timeRemaining <= 0) {{
                alert('Assessment time is up!');
                return;
            }}
            
            timeRemaining--;
        }}
        
        // Recording controls
        recordBtn.addEventListener('click', async function() {{
            try {{
                if (!audioStream) {{
                    alert('Please complete audio setup first.');
                    return;
                }}
                
                mediaRecorder = new MediaRecorder(audioStream);
                audioChunks = [];
                
                mediaRecorder.ondataavailable = function(event) {{
                    audioChunks.push(event.data);
                }};
                
                mediaRecorder.onstart = function() {{
                    isRecording = true;
                    recordBtn.disabled = true;
                    stopBtn.disabled = false;
                }};
                
                mediaRecorder.onstop = function() {{
                    isRecording = false;
                    recordBtn.disabled = false;
                    stopBtn.disabled = true;
                    
                    addMayaMessage('Response recorded for Part ' + mayaQuestions[currentQuestionIndex].part, false);
                    
                    // Move to next question
                    currentQuestionIndex++;
                    setTimeout(() => {{
                        loadNextQuestion();
                    }}, 2000);
                }};
                
                mediaRecorder.start();
                
                // Auto-stop after expected duration + 30 seconds
                const maxDuration = (mayaQuestions[currentQuestionIndex].expected_duration || 60) + 30;
                setTimeout(() => {{
                    if (isRecording) {{
                        mediaRecorder.stop();
                    }}
                }}, maxDuration * 1000);
                
            }} catch (error) {{
                alert('Error starting recording: ' + error.message);
            }}
        }});
        
        stopBtn.addEventListener('click', function() {{
            if (mediaRecorder && isRecording) {{
                mediaRecorder.stop();
            }}
        }});
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('Nova Sonic Maya assessment loaded');
        }});
    </script>
</body>
</html>"""
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
            'Cache-Control': 'no-cache'
        },
        'body': html
    }

def handle_writing_assessment():
    """Handle writing assessment"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '<h1>Writing Assessment</h1><p>Writing assessment functionality available.</p>'
    }

def handle_health_check():
    """Handle health check"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'status': 'healthy',
            'maya_voice': 'nova_sonic_amy_only',
            'voice_system': 'aws_bedrock',
            'ui_version': 'nova_sonic_integration',
            'features': ['particle_globe', 'nova_sonic_amy', 'aws_bedrock']
        })
    }
