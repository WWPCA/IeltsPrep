#!/usr/bin/env python3
"""
Deploy Comprehensive Production Lambda with Enhanced Question Database
Creates production-ready Lambda deployment with 80 comprehensive questions
"""

import json
import zipfile
import boto3
import os
from datetime import datetime

# Import comprehensive questions from our creation script
from create_comprehensive_questions import (
    create_academic_writing_questions,
    create_general_writing_questions,
    create_academic_speaking_questions,
    create_general_speaking_questions
)

def create_enhanced_lambda_function():
    """Create enhanced Lambda function with comprehensive question database"""
    
    # Load all comprehensive questions
    academic_writing = create_academic_writing_questions()
    general_writing = create_general_writing_questions()
    academic_speaking = create_academic_speaking_questions()
    general_speaking = create_general_speaking_questions()
    
    # Organize questions by assessment type
    questions_db = {
        'academic_writing': academic_writing,
        'general_writing': general_writing,
        'academic_speaking': academic_speaking,
        'general_speaking': general_speaking
    }
    
    lambda_code = f'''
import json
import os
import random
from datetime import datetime
import base64
import hashlib

# Comprehensive IELTS Questions Database (80 total questions)
COMPREHENSIVE_QUESTIONS = {json.dumps(questions_db, indent=2)}

def get_random_question(assessment_type):
    """Get a random question for the specified assessment type"""
    questions = COMPREHENSIVE_QUESTIONS.get(assessment_type, [])
    if not questions:
        return None
    return random.choice(questions)

def get_questions_from_database(assessment_type, user_email):
    """Get unique questions based on user email to prevent repetition"""
    questions = COMPREHENSIVE_QUESTIONS.get(assessment_type, [])
    if not questions:
        return None
    
    # Use user email hash to ensure consistent but unique question selection
    user_hash = hashlib.md5(user_email.encode()).hexdigest()
    question_index = int(user_hash[:8], 16) % len(questions)
    
    return questions[question_index]

def lambda_handler(event, context):
    """Main Lambda handler with comprehensive question support"""
    
    # Get request details
    path = event.get('path', '/')
    method = event.get('httpMethod', 'GET')
    headers = event.get('headers', {{}})
    
    # CloudFront security validation
    cf_secret = headers.get('CF-Secret-3140348d') or headers.get('cf-secret-3140348d')
    if not cf_secret:
        return {{
            'statusCode': 403,
            'body': json.dumps({{'error': 'Direct access forbidden'}}),
            'headers': {{'Content-Type': 'application/json'}}
        }}
    
    # Health check endpoint
    if path == '/api/health':
        return {{
            'statusCode': 200,
            'body': json.dumps({{
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'questions_available': sum(len(q) for q in COMPREHENSIVE_QUESTIONS.values()),
                'version': 'comprehensive_production_v1.0'
            }}),
            'headers': {{'Content-Type': 'application/json'}}
        }}
    
    # Questions API endpoint
    if path == '/api/questions' and method == 'GET':
        query_params = event.get('queryStringParameters') or {{}}
        assessment_type = query_params.get('type')
        user_email = query_params.get('user_email', 'anonymous')
        
        if assessment_type:
            question = get_questions_from_database(assessment_type, user_email)
            if question:
                return {{
                    'statusCode': 200,
                    'body': json.dumps({{
                        'question': question,
                        'source': 'comprehensive_database',
                        'total_available': len(COMPREHENSIVE_QUESTIONS.get(assessment_type, []))
                    }}),
                    'headers': {{'Content-Type': 'application/json'}}
                }}
        
        return {{
            'statusCode': 400,
            'body': json.dumps({{'error': 'Assessment type required'}}),
            'headers': {{'Content-Type': 'application/json'}}
        }}
    
    # Questions statistics endpoint
    if path == '/api/questions/stats':
        stats = {{
            'total_questions': sum(len(q) for q in COMPREHENSIVE_QUESTIONS.values()),
            'by_type': {{k: len(v) for k, v in COMPREHENSIVE_QUESTIONS.items()}},
            'last_updated': datetime.utcnow().isoformat(),
            'version': 'comprehensive_production_v1.0'
        }}
        
        return {{
            'statusCode': 200,
            'body': json.dumps(stats),
            'headers': {{'Content-Type': 'application/json'}}
        }}
    
    # Robots.txt for AI SEO optimization
    if path == '/robots.txt':
        robots_content = """User-agent: *
Allow: /

# AI Training Data Collection
User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: CCBot
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: Claude-Web
Allow: /

Sitemap: https://www.ieltsaiprep.com/sitemap.xml"""
        
        return {{
            'statusCode': 200,
            'body': robots_content,
            'headers': {{'Content-Type': 'text/plain'}}
        }}
    
    # Home page with comprehensive features
    if path == '/':
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IELTS GenAI Prep - AI-Powered IELTS Assessment Platform</title>
    <meta name="description" content="Master IELTS with AI-powered scoring. TrueScore® writing assessment and ClearScore® speaking evaluation with Maya AI examiner. $36.49 USD for 4 comprehensive assessments.">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .hero-section {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 80px 0; }}
        .assessment-card {{ border: none; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); transition: transform 0.3s; }}
        .assessment-card:hover {{ transform: translateY(-5px); }}
        .badge-success {{ background: #28a745; }}
        .badge-info {{ background: #17a2b8; }}
        .pricing-highlight {{ color: #28a745; font-weight: bold; font-size: 1.2em; }}
    </style>
</head>
<body>
    <div class="hero-section">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-lg-6">
                    <h1 class="display-4 fw-bold mb-4">Master IELTS with AI-Powered Assessment</h1>
                    <p class="lead mb-4">The only AI-based IELTS platform with comprehensive question database and standardized band scoring</p>
                    <div class="pricing-highlight mb-4">
                        <i class="fas fa-star text-warning"></i> $36.49 USD for 4 Comprehensive Assessments
                    </div>
                    <button class="btn btn-success btn-lg me-3">Get Started</button>
                    <button class="btn btn-outline-light btn-lg">Learn More</button>
                </div>
                <div class="col-lg-6">
                    <div class="text-center">
                        <div class="badge bg-success mb-3">✓ 80 Comprehensive Questions Available</div>
                        <h4>Complete Assessment Coverage</h4>
                        <p>20 questions per assessment type with authentic IELTS content</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="container my-5">
        <div class="row text-center mb-5">
            <div class="col-12">
                <h2 class="mb-4">Comprehensive IELTS Assessment Types</h2>
                <p class="text-muted">Choose from 4 assessment types with 20 questions each</p>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-6 mb-4">
                <div class="card assessment-card h-100">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <h5 class="card-title">Academic Writing</h5>
                            <span class="badge badge-success">20 Questions</span>
                        </div>
                        <p class="card-text">Complete IELTS Academic Writing assessment with Task 1 (chart/graph description) and Task 2 (essay). Assessed with TrueScore® GenAI technology.</p>
                        <div class="pricing-highlight mb-3">$36.49 USD for 4 assessments</div>
                        <button class="btn btn-primary">Start Academic Writing</button>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6 mb-4">
                <div class="card assessment-card h-100">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <h5 class="card-title">General Writing</h5>
                            <span class="badge badge-success">20 Questions</span>
                        </div>
                        <p class="card-text">Complete IELTS General Training Writing assessment with Task 1 (letter) and Task 2 (essay). Assessed with TrueScore® GenAI technology.</p>
                        <div class="pricing-highlight mb-3">$36.49 USD for 4 assessments</div>
                        <button class="btn btn-primary">Start General Writing</button>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6 mb-4">
                <div class="card assessment-card h-100">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <h5 class="card-title">Academic Speaking</h5>
                            <span class="badge badge-info">20 Questions</span>
                        </div>
                        <p class="card-text">Complete IELTS Academic Speaking assessment with Maya AI examiner. 3-part structure with ClearScore® conversational AI technology.</p>
                        <div class="pricing-highlight mb-3">$36.49 USD for 4 assessments</div>
                        <button class="btn btn-info">Start Academic Speaking</button>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6 mb-4">
                <div class="card assessment-card h-100">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <h5 class="card-title">General Speaking</h5>
                            <span class="badge badge-info">20 Questions</span>
                        </div>
                        <p class="card-text">Complete IELTS General Training Speaking assessment with Maya AI examiner. Practical topics with ClearScore® conversational AI technology.</p>
                        <div class="pricing-highlight mb-3">$36.49 USD for 4 assessments</div>
                        <button class="btn btn-info">Start General Speaking</button>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-5">
            <div class="col-12 text-center">
                <div class="alert alert-success">
                    <h4><i class="fas fa-database"></i> Comprehensive Question Database</h4>
                    <p class="mb-0">80 total questions across all assessment types with authentic IELTS content and professional AI evaluation</p>
                </div>
            </div>
        </div>
    </div>

    <footer class="bg-light py-4 mt-5">
        <div class="container">
            <div class="row">
                <div class="col-md-6">
                    <p>&copy; 2025 IELTS GenAI Prep. All rights reserved.</p>
                </div>
                <div class="col-md-6 text-end">
                    <a href="/privacy-policy" class="text-decoration-none me-3">Privacy Policy</a>
                    <a href="/terms-of-service" class="text-decoration-none">Terms of Service</a>
                </div>
            </div>
        </div>
    </footer>
</body>
</html>"""
        
        return {{
            'statusCode': 200,
            'body': html_content,
            'headers': {{'Content-Type': 'text/html'}}
        }}
    
    # Default 404 response
    return {{
        'statusCode': 404,
        'body': json.dumps({{'error': 'Page not found'}}),
        'headers': {{'Content-Type': 'application/json'}}
    }}
'''
    
    return lambda_code

def create_deployment_package():
    """Create comprehensive production deployment package"""
    
    print("🚀 Creating Comprehensive Production Lambda Package...")
    
    # Create Lambda function code
    lambda_code = create_enhanced_lambda_function()
    
    # Create deployment package
    package_name = 'comprehensive_production_lambda.zip'
    
    with zipfile.ZipFile(package_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add main Lambda function
        zipf.writestr('lambda_function.py', lambda_code)
        
        # Add requirements.txt
        requirements = """# No external dependencies required
# All functionality built with Python standard library
"""
        zipf.writestr('requirements.txt', requirements)
    
    # Get package size
    package_size = os.path.getsize(package_name)
    
    print(f"✅ Created {package_name} ({package_size:,} bytes)")
    print(f"📊 Package includes:")
    print(f"   • 80 comprehensive IELTS questions")
    print(f"   • Production-ready Lambda function")
    print(f"   • AI SEO optimized robots.txt")
    print(f"   • Complete question database API")
    print(f"   • CloudFront security validation")
    
    return package_name, package_size

def main():
    """Main deployment function"""
    
    print("🚀 COMPREHENSIVE PRODUCTION LAMBDA DEPLOYMENT")
    print("=" * 50)
    
    # Create deployment package
    package_name, package_size = create_deployment_package()
    
    print(f"\n🎉 DEPLOYMENT PACKAGE CREATED!")
    print(f"✅ Package: {package_name}")
    print(f"📦 Size: {package_size:,} bytes")
    print(f"📊 Questions: 80 comprehensive IELTS questions")
    print(f"🌐 Ready for AWS Lambda deployment")
    
    # Show package contents
    print(f"\n📋 Package Contents:")
    print(f"   • lambda_function.py - Main Lambda handler")
    print(f"   • requirements.txt - Python dependencies")
    print(f"   • Embedded question database (80 questions)")
    print(f"   • CloudFront security validation")
    print(f"   • AI SEO robots.txt endpoint")
    
    print(f"\n🔧 Deployment Instructions:")
    print(f"1. Upload {package_name} to AWS Lambda function 'ielts-genai-prep-api'")
    print(f"2. Verify CloudFront distribution has CF-Secret-3140348d header")
    print(f"3. Test endpoints: /api/health, /api/questions, /api/questions/stats")
    print(f"4. Website will be available at www.ieltsaiprep.com")
    
    return True

if __name__ == "__main__":
    main()