"""
AI SEO Optimized Lambda Function
Deploys the comprehensive AI SEO template with all optimizations
"""

import json
import os
import uuid
from typing import Dict, Any, Optional
from urllib.parse import unquote
import base64
import hashlib
import hmac
import time
import urllib.request
import urllib.parse

# Simple user storage for testing
USERS_DB = {
    "test@ieltsgenaiprep.com": {
        "password": "test123",
        "first_name": "Test",
        "last_name": "User"
    },
    "prodtest@ieltsgenaiprep.com": {
        "password": "prodtest123",
        "first_name": "Production",
        "last_name": "Test"
    }
}

def lambda_handler(event, context):
    """Main AWS Lambda handler"""
    try:
        # Get request details
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        headers = event.get('headers', {})
        query_params = event.get('queryStringParameters') or {}
        
        # Parse body for POST requests
        body = event.get('body', '')
        if body:
            if event.get('isBase64Encoded', False):
                body = base64.b64decode(body).decode('utf-8')
        
        # Check CloudFront security header
        cf_secret = headers.get('cf-secret', '')
        if cf_secret != 'CF-Secret-3140348d':
            return {
                'statusCode': 403,
                'body': json.dumps({'error': 'Forbidden - Direct access not allowed'})
            }
        
        # Route requests
        if path == '/':
            return handle_home_page()
        elif path == '/login':
            if http_method == 'GET':
                return handle_login_page()
            elif http_method == 'POST':
                return handle_login_post(body)
        elif path == '/privacy-policy':
            return handle_privacy_policy()
        elif path == '/terms-of-service':
            return handle_terms_of_service()
        elif path == '/dashboard':
            return handle_dashboard()
        elif path.startswith('/assessment/'):
            return handle_assessment(path)
        elif path == '/robots.txt':
            return handle_robots_txt()
        elif path == '/gdpr/my-data':
            return handle_gdpr_my_data()
        elif path == '/gdpr/consent-settings':
            return handle_gdpr_consent_settings()
        elif path == '/gdpr/cookie-preferences':
            return handle_gdpr_cookie_preferences()
        elif path == '/gdpr/data-export':
            return handle_gdpr_data_export()
        elif path == '/gdpr/data-deletion':
            return handle_gdpr_data_deletion()
        else:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'text/html'},
                'body': get_404_page()
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': f'<h1>500 - Internal Server Error</h1><p>{str(e)}</p>'
        }

def handle_home_page():
    """Serve AI SEO optimized home page"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': get_ai_seo_home_template()
    }

def handle_login_page():
    """Serve login page"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': get_login_template()
    }

def handle_login_post(body):
    """Handle login POST request"""
    try:
        # Parse form data
        form_data = urllib.parse.parse_qs(body)
        email = form_data.get('email', [''])[0]
        password = form_data.get('password', [''])[0]
        
        # Check credentials
        if email in USERS_DB and USERS_DB[email]['password'] == password:
            # Login successful
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': True,
                    'session_id': str(uuid.uuid4()),
                    'redirect': '/dashboard'
                })
            }
        else:
            # Login failed
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Invalid credentials'
                })
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }

def handle_privacy_policy():
    """Serve privacy policy page"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': get_privacy_policy_template()
    }

def handle_terms_of_service():
    """Serve terms of service page"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': get_terms_template()
    }

def handle_dashboard():
    """Serve dashboard page"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': get_dashboard_template()
    }

def handle_assessment(path):
    """Serve assessment pages"""
    assessment_type = path.split('/')[-1]
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': get_assessment_template(assessment_type)
    }

def handle_robots_txt():
    """Serve robots.txt for AI SEO"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/plain'},
        'body': """User-agent: *
Allow: /

# AI Crawlers
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

User-agent: ChatGPT-User
Allow: /

Sitemap: https://www.ieltsaiprep.com/sitemap.xml"""
    }

def handle_gdpr_my_data():
    """Handle GDPR My Data dashboard"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': get_gdpr_my_data_template()
    }

def handle_gdpr_consent_settings():
    """Handle GDPR consent settings"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': get_gdpr_consent_template()
    }

def handle_gdpr_cookie_preferences():
    """Handle GDPR cookie preferences"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': get_gdpr_cookie_template()
    }

def handle_gdpr_data_export():
    """Handle GDPR data export"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': get_gdpr_export_template()
    }

def handle_gdpr_data_deletion():
    """Handle GDPR data deletion"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': get_gdpr_deletion_template()
    }

def get_ai_seo_home_template():
    """AI SEO optimized home page template"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="The only AI-powered IELTS assessment platform with standardized band scoring. Prepare for IELTS Writing and Speaking with TrueScore® and ClearScore® technologies.">
    <meta name="keywords" content="IELTS AI Assessment, IELTS Writing Feedback, IELTS Speaking Evaluation, GenAI IELTS App, TrueScore IELTS, ClearScore IELTS, AI Band Score, IELTS Band Descriptors, Academic IELTS, General Training IELTS, AI IELTS Practice, Online IELTS Preparation, AI Language Assessment, IELTS Prep App, IELTS writing preparation, IELTS speaking practice test, IELTS writing practice test, IELTS practice test with feedback">
    <meta property="og:title" content="IELTS GenAI Prep - AI-Powered IELTS Assessment Platform">
    <meta property="og:description" content="The only AI-powered IELTS assessment platform with standardized band scoring using TrueScore® and ClearScore® technologies.">
    <meta property="og:type" content="website">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="IELTS GenAI Prep - AI-Powered IELTS Assessment Platform">
    <meta name="twitter:description" content="The only AI-powered IELTS assessment platform with standardized band scoring using TrueScore® and ClearScore® technologies.">
    <title>IELTS GenAI Prep - AI-Powered IELTS Assessment Platform</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Font Awesome for icons -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css" rel="stylesheet">
    
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    
    <!-- Schema.org Organization Markup -->
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "Organization",
      "name": "IELTS GenAI Prep",
      "url": "https://www.ieltsaiprep.com",
      "logo": "https://www.ieltsaiprep.com/logo.png",
      "description": "IELTS GenAI Prep is an AI-powered IELTS assessment platform offering instant band-aligned feedback for Writing and Speaking modules.",
      "sameAs": [
        "https://www.linkedin.com/company/ieltsgenaiprep",
        "https://www.twitter.com/ieltsgenaiprep"
      ]
    }
    </script>
    
    <!-- FAQ Schema Markup -->
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "FAQPage",
      "mainEntity": [
        {
          "@type": "Question",
          "name": "What is IELTS GenAI Prep?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "IELTS GenAI Prep is an AI-powered assessment platform that delivers standardized, examiner-aligned band scores for IELTS Writing and Speaking, using official IELTS scoring criteria."
          }
        },
        {
          "@type": "Question",
          "name": "What makes IELTS GenAI Prep different from other IELTS prep tools?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "It is the only platform using TrueScore® and ClearScore® technologies to provide instant, AI-generated feedback that mirrors official IELTS band descriptors for both Academic and General Training modules."
          }
        },
        {
          "@type": "Question",
          "name": "How does TrueScore® assess IELTS Writing tasks?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "TrueScore® uses GenAI models trained on IELTS scoring rubrics to assess Task Achievement, Coherence & Cohesion, Lexical Resource, and Grammatical Range & Accuracy. Each submission receives band-aligned feedback."
          }
        },
        {
          "@type": "Question",
          "name": "How is ClearScore® used to evaluate IELTS Speaking?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "ClearScore® simulates a live speaking test using AI voice assessment technology. It scores fluency, pronunciation, grammar, and vocabulary in real-time, based on official IELTS speaking criteria."
          }
        },
        {
          "@type": "Question",
          "name": "Do you offer Academic and General Training modules?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Yes. IELTS GenAI Prep supports both Academic and General Training formats for Writing and Speaking, allowing users to choose modules aligned with their test goals."
          }
        },
        {
          "@type": "Question",
          "name": "How much does it cost to use IELTS GenAI Prep?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Each module (Writing or Speaking) is priced at $49.99 for four AI-graded assessments. This includes band scores and detailed feedback on every attempt."
          }
        },
        {
          "@type": "Question",
          "name": "Is this a mobile-only platform?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "IELTS GenAI Prep is optimized for mobile and desktop. Users can create an account on the website and access assessments on the IELTS GenAI mobile app anytime, anywhere."
          }
        },
        {
          "@type": "Question",
          "name": "How fast is the scoring process?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "All AI assessments are completed within seconds to a few minutes, providing instant band scores and feedback so users can improve quickly and effectively."
          }
        },
        {
          "@type": "Question",
          "name": "How reliable are the AI-generated IELTS scores?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Our GenAI scores show a 96% alignment with certified IELTS examiners. The technology is built to mimic human scoring standards while ensuring consistency and speed."
          }
        },
        {
          "@type": "Question",
          "name": "Can I track my performance over time?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Yes. Your personalized dashboard allows you to review past assessments, track band score improvements, and identify focus areas for continued practice."
          }
        }
      ]
    }
    </script>
    
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            line-height: 1.6;
        }
        
        .pricing-card {
            border: 1px solid rgba(0, 0, 0, 0.125);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s;
        }
        
        .pricing-card:hover {
            transform: translateY(-5px);
        }
        
        .genai-brand-section {
            margin-bottom: 60px;
        }
        
        .brand-icon {
            font-size: 2.5rem;
            margin-bottom: 15px;
        }
        
        .brand-title {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        
        .brand-tagline {
            color: #666;
            margin-bottom: 2rem;
            font-size: 1.1rem;
        }
        
        .hero {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 80px 0;
        }
        
        .features {
            padding: 80px 0;
            background: #f8f9fa;
        }
        
        .navbar {
            background-color: #fff !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .navbar-brand {
            font-weight: bold;
            color: #4361ee !important;
        }
        
        .navbar-nav .nav-link {
            color: #333 !important;
            font-weight: 500;
        }
        
        .navbar-nav .nav-link:hover {
            color: #4361ee !important;
        }
        
        /* Enhanced animations and interactivity */
        .hero h1 {
            animation: fadeInUp 0.8s ease-out;
        }
        
        .hero h2 {
            animation: fadeInUp 0.8s ease-out 0.2s both;
        }
        
        .hero .mb-4 > div {
            animation: fadeInLeft 0.6s ease-out 0.4s both;
        }
        
        .hero .mb-4 > div:nth-child(2) {
            animation-delay: 0.6s;
        }
        
        .hero .mb-4 > div:nth-child(3) {
            animation-delay: 0.8s;
        }
        
        .hero p {
            animation: fadeInUp 0.8s ease-out 1s both;
        }
        
        .hero-buttons {
            animation: fadeInUp 0.8s ease-out 1.2s both;
        }
        
        .hero .col-lg-6:last-child {
            animation: fadeInRight 0.8s ease-out 0.5s both;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes fadeInLeft {
            from {
                opacity: 0;
                transform: translateX(-30px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes fadeInRight {
            from {
                opacity: 0;
                transform: translateX(30px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        /* Button hover effects */
        .hero-buttons .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        }
        
        .btn-success:hover {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            box-shadow: 0 6px 20px rgba(40, 167, 69, 0.6);
        }
        
        .btn-outline-light:hover {
            background: rgba(255,255,255,0.1);
            border-color: rgba(255,255,255,1);
            backdrop-filter: blur(10px);
        }
        
        /* Icon container hover effects */
        .hero .me-3:hover {
            background: rgba(255,255,255,0.3);
            transform: scale(1.1);
            transition: all 0.3s ease;
        }
        
        /* Improved typography for better readability and spacing */
        @media (max-width: 768px) {
            .hero {
                padding: 60px 0;
            }
            
            .hero h1 {
                font-size: 2.5rem !important;
                line-height: 1.3 !important;
            }
            
            .hero h2 {
                font-size: 1.3rem !important;
            }
            
            .hero-buttons .btn {
                display: block;
                width: 100%;
                margin-bottom: 15px;
                margin-right: 0 !important;
            }
            
            .hero .col-lg-6:first-child {
                text-align: center !important;
            }
        }
        
        @media (max-width: 576px) {
            .hero h1 {
                font-size: 2rem !important;
                line-height: 1.2 !important;
            }
            
            .hero h2 {
                font-size: 1.1rem !important;
            }
            
            .hero .mb-4 span {
                font-size: 1rem !important;
            }
        }
    </style>
</head>

<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-light bg-light fixed-top">
        <div class="container">
            <a class="navbar-brand" href="/">IELTS GenAI Prep</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="#how-it-works">How it Works</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#assessments">Assessments</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#faq">FAQ</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/login">Login</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero" style="margin-top: 76px; padding: 80px 0; position: relative; overflow: hidden;">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-lg-6 text-center text-lg-start mb-5 mb-lg-0">
                    <!-- SEO-Optimized H1 and Introduction -->
                    <h1 class="display-3 fw-bold mb-3" style="font-size: 3.5rem; line-height: 1.2; letter-spacing: -0.02em; color: #ffffff; text-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        AI-Powered IELTS Writing and Speaking Assessments with Official Band Scoring
                    </h1>
                    
                    <p class="h4 mb-4" style="font-size: 1.3rem; line-height: 1.4; font-weight: 500; color: rgba(255,255,255,0.95); margin-bottom: 2rem;">
                        IELTS GenAI Prep is the only AI-based IELTS preparation platform offering instant band-aligned feedback on Writing and Speaking. Powered by TrueScore® and ClearScore®, we replicate official examiner standards using GenAI technology.
                    </p>
                    
                    <!-- Benefits with icons -->
                    <div class="mb-4">
                        <div class="d-flex align-items-center justify-content-center justify-content-lg-start mb-3">
                            <div class="me-3" style="width: 40px; height: 40px; background: rgba(255,255,255,0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(10px);">
                                <i class="fas fa-brain text-white" style="font-size: 1.1rem;"></i>
                            </div>
                            <span class="text-white" style="font-size: 1.1rem; font-weight: 500;">AI-Powered Scoring Technology</span>
                        </div>
                        
                        <div class="d-flex align-items-center justify-content-center justify-content-lg-start mb-3">
                            <div class="me-3" style="width: 40px; height: 40px; background: rgba(255,255,255,0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(10px);">
                                <i class="fas fa-check-circle text-white" style="font-size: 1.1rem;"></i>
                            </div>
                            <span class="text-white" style="font-size: 1.1rem; font-weight: 500;">Official IELTS Criteria Alignment</span>
                        </div>
                        
                        <div class="d-flex align-items-center justify-content-center justify-content-lg-start mb-4">
                            <div class="me-3" style="width: 40px; height: 40px; background: rgba(255,255,255,0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(10px);">
                                <i class="fas fa-bullseye text-white" style="font-size: 1.1rem;"></i>
                            </div>
                            <span class="text-white" style="font-size: 1.1rem; font-weight: 500;">Instant Detailed Feedback</span>
                        </div>
                    </div>
                    
                    <div class="hero-buttons">
                        <a href="/login" class="btn btn-success btn-lg me-3 mb-3" style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); border: none; padding: 15px 40px; font-size: 1.1rem; border-radius: 50px; transition: all 0.3s ease;">
                            Get Started Now
                        </a>
                        <a href="#how-it-works" class="btn btn-outline-light btn-lg mb-3" style="padding: 15px 40px; font-size: 1.1rem; border-radius: 50px; transition: all 0.3s ease;">
                            Learn More
                        </a>
                    </div>
                </div>
                
                <div class="col-lg-6 text-center">
                    <div class="position-relative">
                        <!-- Sample Assessment Badge -->
                        <div class="card border-0 shadow-lg mx-auto" style="max-width: 450px; background: rgba(255,255,255,0.95); backdrop-filter: blur(10px);">
                            <div class="card-header bg-primary text-white text-center">
                                <h5 class="mb-0"><i class="fas fa-award me-2"></i>Academic Writing Assessment Sample</h5>
                            </div>
                            <div class="card-body">
                                <div class="row text-center">
                                    <div class="col-6 mb-3">
                                        <h6 class="text-primary mb-1">Task Achievement</h6>
                                        <div class="badge bg-success fs-6">Band 7.5</div>
                                        <p class="small text-muted mt-1">Addresses all parts with clear ideas</p>
                                    </div>
                                    <div class="col-6 mb-3">
                                        <h6 class="text-primary mb-1">Coherence & Cohesion</h6>
                                        <div class="badge bg-success fs-6">Band 7.0</div>
                                        <p class="small text-muted mt-1">Logical organization with linking</p>
                                    </div>
                                    <div class="col-6 mb-3">
                                        <h6 class="text-primary mb-1">Lexical Resource</h6>
                                        <div class="badge bg-success fs-6">Band 8.0</div>
                                        <p class="small text-muted mt-1">Wide range of vocabulary</p>
                                    </div>
                                    <div class="col-6 mb-3">
                                        <h6 class="text-primary mb-1">Grammar Range</h6>
                                        <div class="badge bg-success fs-6">Band 7.5</div>
                                        <p class="small text-muted mt-1">Variety of complex structures</p>
                                    </div>
                                </div>
                                <div class="text-center mt-3">
                                    <h4 class="text-primary mb-2">Overall Band Score: 7.5</h4>
                                    <p class="small text-muted">See exactly how your IELTS score will look</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- How It Works Section -->
    <section id="how-it-works" class="py-5 bg-light">
        <div class="container">
            <h2 class="text-center mb-5">How It Works</h2>
            <div class="row">
                <div class="col-lg-4 text-center mb-4">
                    <div class="mb-4">
                        <div class="bg-primary text-white rounded-circle d-inline-flex align-items-center justify-content-center" style="width: 80px; height: 80px;">
                            <span class="h3 mb-0">1</span>
                        </div>
                    </div>
                    <h4>Download Mobile App</h4>
                    <p class="text-muted">Get the IELTS GenAI Prep app from App Store or Google Play Store and create your account.</p>
                </div>
                <div class="col-lg-4 text-center mb-4">
                    <div class="mb-4">
                        <div class="bg-success text-white rounded-circle d-inline-flex align-items-center justify-content-center" style="width: 80px; height: 80px;">
                            <span class="h3 mb-0">2</span>
                        </div>
                    </div>
                    <h4>Choose Your Assessment</h4>
                    <p class="text-muted">Select Academic or General Training modules. Each assessment pack costs $49.99 for 4 comprehensive evaluations.</p>
                </div>
                <div class="col-lg-4 text-center mb-4">
                    <div class="mb-4">
                        <div class="bg-info text-white rounded-circle d-inline-flex align-items-center justify-content-center" style="width: 80px; height: 80px;">
                            <span class="h3 mb-0">3</span>
                        </div>
                    </div>
                    <h4>Take Assessments</h4>
                    <p class="text-muted">Complete assessments on mobile or login here for desktop access. Your progress syncs automatically.</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Assessments Section -->
    <section id="assessments" class="py-5">
        <div class="container">
            <h2 class="text-center mb-5">GenAI Assessed IELTS Modules</h2>
            <div class="row">
                <div class="col-md-6 mb-4">
                    <div class="card h-100 pricing-card">
                        <div class="card-body text-center">
                            <i class="fas fa-pen-nib text-primary brand-icon"></i>
                            <h4 class="card-title brand-title text-primary">TrueScore® Writing Assessment</h4>
                            <p class="brand-tagline">Advanced AI evaluation of your writing skills with detailed feedback across all IELTS criteria.</p>
                            <ul class="list-unstyled text-start mb-4">
                                <li class="mb-2"><i class="fas fa-check text-success me-2"></i>Task Achievement Analysis</li>
                                <li class="mb-2"><i class="fas fa-check text-success me-2"></i>Coherence & Cohesion Review</li>
                                <li class="mb-2"><i class="fas fa-check text-success me-2"></i>Lexical Resource Assessment</li>
                                <li class="mb-2"><i class="fas fa-check text-success me-2"></i>Grammar Range & Accuracy</li>
                            </ul>
                            <h5 class="text-success mb-3">$49.99 for 4 Assessments</h5>
                            <p class="text-muted small">Available in Academic and General Training formats</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-6 mb-4">
                    <div class="card h-100 pricing-card">
                        <div class="card-body text-center">
                            <i class="fas fa-microphone text-info brand-icon"></i>
                            <h4 class="card-title brand-title text-info">ClearScore® Speaking Assessment</h4>
                            <p class="brand-tagline">AI-powered speaking evaluation with Maya, your personal IELTS examiner.</p>
                            <ul class="list-unstyled text-start mb-4">
                                <li class="mb-2"><i class="fas fa-check text-info me-2"></i>Fluency & Coherence Analysis</li>
                                <li class="mb-2"><i class="fas fa-check text-info me-2"></i>Lexical Resource Evaluation</li>
                                <li class="mb-2"><i class="fas fa-check text-info me-2"></i>Grammar Range Assessment</li>
                                <li class="mb-2"><i class="fas fa-check text-info me-2"></i>Pronunciation Review</li>
                            </ul>
                            <h5 class="text-info mb-3">$49.99 for 4 Assessments</h5>
                            <p class="text-muted small">Interactive AI examiner with real-time feedback</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- FAQ Section -->
    <section id="faq" class="py-5 bg-light">
        <div class="container">
            <h2 class="text-center mb-5">Frequently Asked Questions</h2>
            <div class="row">
                <div class="col-lg-8 mx-auto">
                    <div class="accordion" id="faqAccordion">
                        <div class="accordion-item">
                            <h2 class="accordion-header">
                                <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#faq1">
                                    What is IELTS GenAI Prep?
                                </button>
                            </h2>
                            <div id="faq1" class="accordion-collapse collapse show" data-bs-parent="#faqAccordion">
                                <div class="accordion-body">
                                    IELTS GenAI Prep is an AI-powered assessment platform that delivers standardized, examiner-aligned band scores for IELTS Writing and Speaking, using official IELTS scoring criteria.
                                </div>
                            </div>
                        </div>
                        <div class="accordion-item">
                            <h2 class="accordion-header">
                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#faq2">
                                    How does TrueScore® assess IELTS Writing tasks?
                                </button>
                            </h2>
                            <div id="faq2" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
                                <div class="accordion-body">
                                    TrueScore® uses GenAI models trained on IELTS scoring rubrics to assess Task Achievement, Coherence & Cohesion, Lexical Resource, and Grammatical Range & Accuracy. Each submission receives band-aligned feedback.
                                </div>
                            </div>
                        </div>
                        <div class="accordion-item">
                            <h2 class="accordion-header">
                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#faq3">
                                    How much does it cost to use IELTS GenAI Prep?
                                </button>
                            </h2>
                            <div id="faq3" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
                                <div class="accordion-body">
                                    Each module (Writing or Speaking) is priced at $49.99 for four AI-graded assessments. This includes band scores and detailed feedback on every attempt.
                                </div>
                            </div>
                        </div>
                        <div class="accordion-item">
                            <h2 class="accordion-header">
                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#faq4">
                                    How reliable are the AI-generated IELTS scores?
                                </button>
                            </h2>
                            <div id="faq4" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
                                <div class="accordion-body">
                                    Our GenAI scores show a 96% alignment with certified IELTS examiners. The technology is built to mimic human scoring standards while ensuring consistency and speed.
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="bg-dark text-white py-4">
        <div class="container">
            <div class="row">
                <div class="col-md-8">
                    <h5>IELTS GenAI Prep</h5>
                    <p class="mb-0">AI-powered IELTS assessment platform with official band scoring</p>
                </div>
                <div class="col-md-4 text-md-end">
                    <p class="mb-2">&copy; 2025 IELTS GenAI Prep. All rights reserved.</p>
                    <div>
                        <a href="/privacy-policy" class="text-white me-3">Privacy Policy</a>
                        <a href="/terms-of-service" class="text-white me-3">Terms of Service</a>
                        <a href="/gdpr/my-data" class="text-white">My Data Rights</a>
                    </div>
                </div>
            </div>
        </div>
    </footer>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""

def get_login_template():
    """Professional login page template"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .login-container {
            max-width: 450px;
            margin: 50px auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .login-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .mobile-info {
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            border-left: 4px solid #2196f3;
            padding: 20px;
            margin: 20px 0;
        }
        .app-buttons {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        .app-btn {
            flex: 1;
            padding: 10px;
            border: none;
            border-radius: 8px;
            color: white;
            text-decoration: none;
            text-align: center;
            font-weight: bold;
        }
        .app-store {
            background: #000;
        }
        .google-play {
            background: #01875f;
        }
        .form-section {
            padding: 30px;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 25px;
            padding: 12px 30px;
            width: 100%;
        }
        .home-btn {
            position: absolute;
            top: 15px;
            left: 15px;
            background: rgba(255,255,255,0.2);
            border: none;
            color: white;
            padding: 8px 12px;
            border-radius: 8px;
            text-decoration: none;
            backdrop-filter: blur(10px);
        }
        .home-btn:hover {
            background: rgba(255,255,255,0.3);
            color: white;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <a href="/" class="home-btn">
                <i class="fas fa-home me-2"></i>Home
            </a>
            <h2><i class="fas fa-brain me-2"></i>Welcome Back</h2>
            <p class="mb-0">Sign in to your IELTS GenAI Prep account</p>
        </div>
        
        <div class="mobile-info">
            <h5><i class="fas fa-mobile-alt me-2"></i>New to IELTS GenAI Prep?</h5>
            <p class="mb-2">Download our mobile app to purchase assessments and create your account. You can then login here to practice on desktop/laptop.</p>
            <div class="app-buttons">
                <a href="#" class="app-btn app-store">
                    <i class="fab fa-apple me-2"></i>App Store
                </a>
                <a href="#" class="app-btn google-play">
                    <i class="fab fa-google-play me-2"></i>Google Play
                </a>
            </div>
        </div>
        
        <div class="form-section">
            <form id="loginForm">
                <div class="mb-3">
                    <label for="email" class="form-label">Email</label>
                    <input type="email" class="form-control" id="email" name="email" required>
                </div>
                <div class="mb-3">
                    <label for="password" class="form-label">Password</label>
                    <input type="password" class="form-control" id="password" name="password" required>
                </div>
                <button type="submit" class="btn btn-primary">Sign In</button>
            </form>
            <div class="text-center mt-3">
                <a href="#" class="text-muted">Forgot your password?</a>
            </div>
        </div>
    </div>

    <footer class="text-center text-white mt-5">
        <p>&copy; 2025 IELTS GenAI Prep. All rights reserved.</p>
        <a href="/privacy-policy" class="text-white me-3">Privacy Policy</a>
        <a href="/terms-of-service" class="text-white">Terms of Service</a>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.getElementById('loginForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const data = new URLSearchParams(formData);
            
            fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: data
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = '/dashboard';
                } else {
                    alert('Login failed: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred during login');
            });
        });
    </script>
</body>
</html>"""

def get_privacy_policy_template():
    """Privacy policy page template"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Privacy Policy - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .header-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 60px 0;
        }
        .back-btn {
            background: rgba(255,255,255,0.2);
            border: none;
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            text-decoration: none;
            backdrop-filter: blur(10px);
        }
        .back-btn:hover {
            background: rgba(255,255,255,0.3);
            color: white;
        }
        .content-section {
            padding: 60px 0;
        }
    </style>
</head>
<body>
    <div class="header-section">
        <div class="container">
            <a href="/" class="back-btn mb-3 d-inline-block">
                <i class="fas fa-arrow-left me-2"></i>Back to Home
            </a>
            <h1 class="display-4">Privacy Policy</h1>
            <p class="lead">Last Updated: July 14, 2025</p>
        </div>
    </div>

    <div class="content-section">
        <div class="container">
            <div class="row">
                <div class="col-lg-8 mx-auto">
                    <div class="card">
                        <div class="card-body">
                            <h2>Information We Collect</h2>
                            <p>We collect information you provide directly to us, such as when you create an account, make a purchase, or use our assessment services including TrueScore® Writing Assessment and ClearScore® Speaking Assessment.</p>
                            
                            <h2>How We Use Your Information</h2>
                            <p>We use the information we collect to provide, maintain, and improve our services, including our AI-powered IELTS assessment technologies. Your assessment data helps us deliver accurate band scores and personalized feedback.</p>
                            
                            <h2>TrueScore® and ClearScore® Technologies</h2>
                            <p>Our proprietary AI assessment technologies analyze your writing and speaking responses to provide instant feedback aligned with official IELTS band descriptors. Assessment data is processed securely and used only for scoring purposes.</p>
                            
                            <h2>Data Security</h2>
                            <p>We implement appropriate security measures to protect your personal information against unauthorized access, alteration, disclosure, or destruction. All assessment data is encrypted and stored securely.</p>
                            
                            <h2>Mobile App Integration</h2>
                            <p>Your account information syncs between the mobile app and web platform. Purchase information is handled through Apple App Store and Google Play Store according to their respective privacy policies.</p>
                            
                            <h2>Contact Us</h2>
                            <p>If you have any questions about this Privacy Policy, please contact us through our mobile app or website support system.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <footer class="bg-dark text-white py-4">
        <div class="container">
            <div class="row">
                <div class="col-md-6">
                    <p>&copy; 2025 IELTS GenAI Prep. All rights reserved.</p>
                </div>
                <div class="col-md-6 text-md-end">
                    <a href="/privacy-policy" class="text-white me-3">Privacy Policy</a>
                    <a href="/terms-of-service" class="text-white">Terms of Service</a>
                </div>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""

def get_terms_template():
    """Terms of service page template"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Terms of Service - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .header-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 60px 0;
        }
        .back-btn {
            background: rgba(255,255,255,0.2);
            border: none;
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            text-decoration: none;
            backdrop-filter: blur(10px);
        }
        .back-btn:hover {
            background: rgba(255,255,255,0.3);
            color: white;
        }
        .content-section {
            padding: 60px 0;
        }
    </style>
</head>
<body>
    <div class="header-section">
        <div class="container">
            <a href="/" class="back-btn mb-3 d-inline-block">
                <i class="fas fa-arrow-left me-2"></i>Back to Home
            </a>
            <h1 class="display-4">Terms of Service</h1>
            <p class="lead">Last Updated: July 14, 2025</p>
        </div>
    </div>

    <div class="content-section">
        <div class="container">
            <div class="row">
                <div class="col-lg-8 mx-auto">
                    <div class="card">
                        <div class="card-body">
                            <h2>Service Description</h2>
                            <p>IELTS GenAI Prep provides AI-powered IELTS assessment services including TrueScore® Writing Assessment and ClearScore® Speaking Assessment for both Academic and General Training modules.</p>
                            
                            <h2>Pricing and Payment</h2>
                            <p>Each assessment product is priced at $49.99 CAD and includes 4 assessment attempts with detailed AI-generated feedback. All purchases are processed through Apple App Store or Google Play Store in-app purchase systems.</p>
                            
                            <h2>Assessment Services</h2>
                            <p>Our AI assessment technologies provide instant feedback aligned with official IELTS band descriptors. Each assessment includes detailed analysis across all IELTS criteria including Task Achievement, Coherence & Cohesion, Lexical Resource, and Grammatical Range & Accuracy.</p>
                            
                            <h2>Refund Policy</h2>
                            <p>All purchases are non-refundable as per standard digital content policies. For refund requests, please contact Apple App Store or Google Play Store support directly as they handle all payment processing.</p>
                            
                            <h2>User Responsibilities</h2>
                            <p>You are responsible for maintaining the confidentiality of your account credentials and for all activities under your account. You must provide accurate information during assessment registration and use the service only for legitimate IELTS preparation purposes.</p>
                            
                            <h2>Intellectual Property</h2>
                            <p>TrueScore® and ClearScore® are proprietary AI assessment technologies. All assessment content, scoring algorithms, and feedback systems are protected by intellectual property rights.</p>
                            
                            <h2>Contact Information</h2>
                            <p>For questions about these terms or technical support, please contact us through our mobile app support system or website contact form.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <footer class="bg-dark text-white py-4">
        <div class="container">
            <div class="row">
                <div class="col-md-6">
                    <p>&copy; 2025 IELTS GenAI Prep. All rights reserved.</p>
                </div>
                <div class="col-md-6 text-md-end">
                    <a href="/privacy-policy" class="text-white me-3">Privacy Policy</a>
                    <a href="/terms-of-service" class="text-white">Terms of Service</a>
                </div>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""

def get_dashboard_template():
    """Dashboard page template"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .dashboard-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 0;
        }
        .assessment-card {
            border: none;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        .assessment-card:hover {
            transform: translateY(-5px);
        }
        .btn-start {
            background: linear-gradient(135deg, #28a745, #20c997);
            border: none;
            border-radius: 25px;
            padding: 12px 30px;
            color: white;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark" style="background-color: #2c3e50;">
        <div class="container">
            <a class="navbar-brand" href="/"><i class="fas fa-brain me-2"></i>IELTS GenAI Prep</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/">Home</a>
                <a class="nav-link" href="/dashboard">Dashboard</a>
                <a class="nav-link" href="#" onclick="logout()">Logout</a>
            </div>
        </div>
    </nav>

    <div class="dashboard-header">
        <div class="container">
            <h1><i class="fas fa-tachometer-alt me-3"></i>Assessment Dashboard</h1>
            <p class="lead">Choose your IELTS assessment type to begin practicing</p>
        </div>
    </div>

    <div class="container my-5">
        <div class="row">
            <div class="col-md-6 mb-4">
                <div class="card assessment-card">
                    <div class="card-body text-center">
                        <i class="fas fa-pen-nib text-primary" style="font-size: 3rem;"></i>
                        <h4 class="card-title mt-3">Academic Writing</h4>
                        <p class="card-text">Task 1 & Task 2 Academic Writing Assessment</p>
                        <p class="text-muted">Remaining: 4 attempts</p>
                        <a href="/assessment/academic-writing" class="btn btn-start">Start Assessment</a>
                    </div>
                </div>
            </div>
            <div class="col-md-6 mb-4">
                <div class="card assessment-card">
                    <div class="card-body text-center">
                        <i class="fas fa-pen-nib text-success" style="font-size: 3rem;"></i>
                        <h4 class="card-title mt-3">General Writing</h4>
                        <p class="card-text">Task 1 & Task 2 General Training Writing Assessment</p>
                        <p class="text-muted">Remaining: 4 attempts</p>
                        <a href="/assessment/general-writing" class="btn btn-start">Start Assessment</a>
                    </div>
                </div>
            </div>
            <div class="col-md-6 mb-4">
                <div class="card assessment-card">
                    <div class="card-body text-center">
                        <i class="fas fa-microphone text-info" style="font-size: 3rem;"></i>
                        <h4 class="card-title mt-3">Academic Speaking</h4>
                        <p class="card-text">Full Speaking Assessment with Maya AI Examiner</p>
                        <p class="text-muted">Remaining: 4 attempts</p>
                        <a href="/assessment/academic-speaking" class="btn btn-start">Start Assessment</a>
                    </div>
                </div>
            </div>
            <div class="col-md-6 mb-4">
                <div class="card assessment-card">
                    <div class="card-body text-center">
                        <i class="fas fa-microphone text-warning" style="font-size: 3rem;"></i>
                        <h4 class="card-title mt-3">General Speaking</h4>
                        <p class="card-text">Full Speaking Assessment with Maya AI Examiner</p>
                        <p class="text-muted">Remaining: 4 attempts</p>
                        <a href="/assessment/general-speaking" class="btn btn-start">Start Assessment</a>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <footer class="bg-dark text-white py-4">
        <div class="container">
            <div class="row">
                <div class="col-md-6">
                    <p>&copy; 2025 IELTS GenAI Prep. All rights reserved.</p>
                </div>
                <div class="col-md-6 text-md-end">
                    <a href="/privacy-policy" class="text-white me-3">Privacy Policy</a>
                    <a href="/terms-of-service" class="text-white">Terms of Service</a>
                </div>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function logout() {
            alert('Logout functionality coming soon!');
        }
    </script>
</body>
</html>"""

def get_assessment_template(assessment_type):
    """Assessment page template"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{assessment_type.title()} Assessment - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .assessment-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 0;
        }}
        .timer {{
            font-size: 2rem;
            font-weight: bold;
            color: #dc3545;
        }}
        .question-panel {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            height: 500px;
            overflow-y: auto;
        }}
        .answer-panel {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #dee2e6;
            height: 500px;
        }}
        .word-count {{
            font-size: 0.9rem;
            color: #6c757d;
        }}
        .submit-btn {{
            background: linear-gradient(135deg, #28a745, #20c997);
            border: none;
            border-radius: 25px;
            padding: 12px 30px;
            color: white;
        }}
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark" style="background-color: #2c3e50;">
        <div class="container">
            <a class="navbar-brand" href="/"><i class="fas fa-brain me-2"></i>IELTS GenAI Prep</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/dashboard">Dashboard</a>
                <span class="nav-link">|</span>
                <span class="nav-link timer" id="timer">20:00</span>
            </div>
        </div>
    </nav>

    <div class="assessment-header">
        <div class="container">
            <h1><i class="fas fa-file-alt me-3"></i>{assessment_type.replace('-', ' ').title()} Assessment</h1>
            <p class="lead">Complete your IELTS assessment with AI-powered feedback</p>
        </div>
    </div>

    <div class="container my-5">
        <div class="row">
            <div class="col-md-6">
                <div class="question-panel">
                    <h4>Task 1</h4>
                    <p>Write a description of the chart below. You should write at least 150 words.</p>
                    <div class="text-center">
                        <div class="border p-3 bg-light">
                            <p>[Sample Chart/Graph would appear here]</p>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="answer-panel">
                    <h4>Your Answer</h4>
                    <textarea class="form-control" rows="18" placeholder="Write your answer here..." id="answer" oninput="updateWordCount()"></textarea>
                    <div class="d-flex justify-content-between mt-3">
                        <span class="word-count" id="wordCount">Words: 0</span>
                        <button class="btn submit-btn" onclick="submitAnswer()">Submit Answer</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <footer class="bg-dark text-white py-4">
        <div class="container">
            <div class="row">
                <div class="col-md-6">
                    <p>&copy; 2025 IELTS GenAI Prep. All rights reserved.</p>
                </div>
                <div class="col-md-6 text-md-end">
                    <a href="/privacy-policy" class="text-white me-3">Privacy Policy</a>
                    <a href="/terms-of-service" class="text-white">Terms of Service</a>
                </div>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let timeLeft = 20 * 60; // 20 minutes in seconds
        
        function updateTimer() {{
            const minutes = Math.floor(timeLeft / 60);
            const seconds = timeLeft % 60;
            document.getElementById('timer').textContent = 
                `${{minutes.toString().padStart(2, '0')}}:${{seconds.toString().padStart(2, '0')}}`;
            
            if (timeLeft > 0) {{
                timeLeft--;
                setTimeout(updateTimer, 1000);
            }} else {{
                alert('Time is up! Submitting your answer...');
                submitAnswer();
            }}
        }}
        
        function updateWordCount() {{
            const text = document.getElementById('answer').value;
            const wordCount = text.trim().split(/\s+/).filter(word => word.length > 0).length;
            document.getElementById('wordCount').textContent = `Words: ${{wordCount}}`;
        }}
        
        function submitAnswer() {{
            const answer = document.getElementById('answer').value;
            if (answer.trim().length < 10) {{
                alert('Please write a longer answer before submitting.');
                return;
            }}
            
            alert('Assessment submitted! You will receive detailed feedback shortly.');
            window.location.href = '/dashboard';
        }}
        
        // Start the timer when the page loads
        updateTimer();
    </script>
</body>
</html>"""

def get_gdpr_my_data_template():
    """GDPR My Data dashboard template"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Data Rights - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .gdpr-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 60px 0;
        }
        .gdpr-card {
            border: none;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        .gdpr-icon {
            font-size: 3rem;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="gdpr-header">
        <div class="container">
            <a href="/" class="btn btn-light mb-3">
                <i class="fas fa-arrow-left me-2"></i>Back to Home
            </a>
            <h1 class="display-4">My Data Rights</h1>
            <p class="lead">Manage your personal data and privacy preferences</p>
        </div>
    </div>

    <div class="container my-5">
        <div class="row">
            <div class="col-md-6 mb-4">
                <div class="card gdpr-card">
                    <div class="card-body text-center">
                        <i class="fas fa-shield-alt text-primary gdpr-icon"></i>
                        <h4 class="card-title">Consent Settings</h4>
                        <p class="card-text">Manage your data processing consent preferences</p>
                        <a href="/gdpr/consent-settings" class="btn btn-primary">Manage Consent</a>
                    </div>
                </div>
            </div>
            <div class="col-md-6 mb-4">
                <div class="card gdpr-card">
                    <div class="card-body text-center">
                        <i class="fas fa-cookie-bite text-success gdpr-icon"></i>
                        <h4 class="card-title">Cookie Preferences</h4>
                        <p class="card-text">Control your cookie and tracking preferences</p>
                        <a href="/gdpr/cookie-preferences" class="btn btn-success">Cookie Settings</a>
                    </div>
                </div>
            </div>
            <div class="col-md-6 mb-4">
                <div class="card gdpr-card">
                    <div class="card-body text-center">
                        <i class="fas fa-download text-info gdpr-icon"></i>
                        <h4 class="card-title">Data Export</h4>
                        <p class="card-text">Download a copy of your personal data</p>
                        <a href="/gdpr/data-export" class="btn btn-info">Export Data</a>
                    </div>
                </div>
            </div>
            <div class="col-md-6 mb-4">
                <div class="card gdpr-card">
                    <div class="card-body text-center">
                        <i class="fas fa-trash-alt text-danger gdpr-icon"></i>
                        <h4 class="card-title">Data Deletion</h4>
                        <p class="card-text">Request deletion of your personal data</p>
                        <a href="/gdpr/data-deletion" class="btn btn-danger">Delete Data</a>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <footer class="bg-dark text-white py-4">
        <div class="container">
            <div class="row">
                <div class="col-md-8">
                    <p>&copy; 2025 IELTS GenAI Prep. All rights reserved.</p>
                </div>
                <div class="col-md-4 text-md-end">
                    <a href="/privacy-policy" class="text-white me-3">Privacy Policy</a>
                    <a href="/terms-of-service" class="text-white">Terms of Service</a>
                </div>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""

def get_gdpr_consent_template():
    """GDPR consent settings template"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Consent Settings - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .gdpr-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 60px 0;
        }
        .consent-form {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
    <div class="gdpr-header">
        <div class="container">
            <a href="/gdpr/my-data" class="btn btn-light mb-3">
                <i class="fas fa-arrow-left me-2"></i>Back to My Data
            </a>
            <h1 class="display-4">Consent Settings</h1>
            <p class="lead">Manage your data processing consent preferences</p>
        </div>
    </div>

    <div class="container my-5">
        <div class="row">
            <div class="col-lg-8 mx-auto">
                <div class="consent-form">
                    <h3 class="mb-4">Data Processing Consent</h3>
                    
                    <div class="mb-4">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="essential" checked disabled>
                            <label class="form-check-label" for="essential">
                                <strong>Essential Data Processing</strong>
                                <p class="text-muted mb-0">Required for account management and assessment delivery. Cannot be disabled.</p>
                            </label>
                        </div>
                    </div>

                    <div class="mb-4">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="assessment" checked>
                            <label class="form-check-label" for="assessment">
                                <strong>Assessment Data Processing</strong>
                                <p class="text-muted mb-0">Process writing and speaking responses for AI-powered feedback and scoring.</p>
                            </label>
                        </div>
                    </div>

                    <div class="mb-4">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="analytics" checked>
                            <label class="form-check-label" for="analytics">
                                <strong>Analytics and Improvement</strong>
                                <p class="text-muted mb-0">Use anonymized data to improve AI models and platform performance.</p>
                            </label>
                        </div>
                    </div>

                    <div class="mb-4">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="marketing">
                            <label class="form-check-label" for="marketing">
                                <strong>Marketing Communications</strong>
                                <p class="text-muted mb-0">Receive updates about new features and assessment improvements.</p>
                            </label>
                        </div>
                    </div>

                    <div class="text-center">
                        <button class="btn btn-primary btn-lg" onclick="updateConsent()">Update Consent Settings</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function updateConsent() {
            alert('Consent settings updated successfully!');
        }
    </script>
</body>
</html>"""

def get_gdpr_cookie_template():
    """GDPR cookie preferences template"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cookie Preferences - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .gdpr-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 60px 0;
        }
        .cookie-form {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
    <div class="gdpr-header">
        <div class="container">
            <a href="/gdpr/my-data" class="btn btn-light mb-3">
                <i class="fas fa-arrow-left me-2"></i>Back to My Data
            </a>
            <h1 class="display-4">Cookie Preferences</h1>
            <p class="lead">Control your cookie and tracking preferences</p>
        </div>
    </div>

    <div class="container my-5">
        <div class="row">
            <div class="col-lg-8 mx-auto">
                <div class="cookie-form">
                    <h3 class="mb-4">Cookie Settings</h3>
                    
                    <div class="mb-4">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="necessary" checked disabled>
                            <label class="form-check-label" for="necessary">
                                <strong>Necessary Cookies</strong>
                                <p class="text-muted mb-0">Required for website functionality and security. Cannot be disabled.</p>
                            </label>
                        </div>
                    </div>

                    <div class="mb-4">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="functional" checked>
                            <label class="form-check-label" for="functional">
                                <strong>Functional Cookies</strong>
                                <p class="text-muted mb-0">Remember your preferences and settings for a better experience.</p>
                            </label>
                        </div>
                    </div>

                    <div class="mb-4">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="analytics" checked>
                            <label class="form-check-label" for="analytics">
                                <strong>Analytics Cookies</strong>
                                <p class="text-muted mb-0">Help us understand how you use our platform to improve performance.</p>
                            </label>
                        </div>
                    </div>

                    <div class="text-center">
                        <button class="btn btn-success btn-lg" onclick="updateCookies()">Update Cookie Preferences</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function updateCookies() {
            alert('Cookie preferences updated successfully!');
        }
    </script>
</body>
</html>"""

def get_gdpr_export_template():
    """GDPR data export template"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Export - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .gdpr-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 60px 0;
        }
        .export-form {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
    <div class="gdpr-header">
        <div class="container">
            <a href="/gdpr/my-data" class="btn btn-light mb-3">
                <i class="fas fa-arrow-left me-2"></i>Back to My Data
            </a>
            <h1 class="display-4">Data Export</h1>
            <p class="lead">Download a copy of your personal data</p>
        </div>
    </div>

    <div class="container my-5">
        <div class="row">
            <div class="col-lg-8 mx-auto">
                <div class="export-form">
                    <h3 class="mb-4">Export Your Data</h3>
                    
                    <div class="alert alert-info">
                        <i class="fas fa-info-circle me-2"></i>
                        Your data export will include account information, assessment history, and preferences.
                    </div>

                    <div class="mb-4">
                        <label class="form-label">Export Format</label>
                        <select class="form-select" id="exportFormat">
                            <option value="json">JSON (Structured Data)</option>
                            <option value="csv">CSV (Spreadsheet)</option>
                            <option value="pdf">PDF (Human Readable)</option>
                        </select>
                    </div>

                    <div class="mb-4">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="includeAssessments" checked>
                            <label class="form-check-label" for="includeAssessments">
                                Include assessment history and scores
                            </label>
                        </div>
                    </div>

                    <div class="text-center">
                        <button class="btn btn-info btn-lg" onclick="requestExport()">
                            <i class="fas fa-download me-2"></i>Request Data Export
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function requestExport() {
            alert('Data export request submitted! You will receive a download link via email within 24 hours.');
        }
    </script>
</body>
</html>"""

def get_gdpr_deletion_template():
    """GDPR data deletion template"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Deletion - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .gdpr-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 60px 0;
        }
        .deletion-form {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
    <div class="gdpr-header">
        <div class="container">
            <a href="/gdpr/my-data" class="btn btn-light mb-3">
                <i class="fas fa-arrow-left me-2"></i>Back to My Data
            </a>
            <h1 class="display-4">Data Deletion</h1>
            <p class="lead">Request deletion of your personal data</p>
        </div>
    </div>

    <div class="container my-5">
        <div class="row">
            <div class="col-lg-8 mx-auto">
                <div class="deletion-form">
                    <h3 class="mb-4">Delete Your Data</h3>
                    
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        <strong>Warning:</strong> This action cannot be undone. All your data will be permanently deleted.
                    </div>

                    <div class="mb-4">
                        <label class="form-label">Deletion Type</label>
                        <select class="form-select" id="deletionType">
                            <option value="complete">Complete Account Deletion</option>
                            <option value="assessments">Assessment Data Only</option>
                            <option value="profile">Profile Information Only</option>
                        </select>
                    </div>

                    <div class="mb-4">
                        <label class="form-label">Reason for Deletion (Optional)</label>
                        <textarea class="form-control" rows="3" id="deletionReason" placeholder="Please let us know why you're deleting your data..."></textarea>
                    </div>

                    <div class="mb-4">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="confirmDeletion" required>
                            <label class="form-check-label" for="confirmDeletion">
                                I understand that this action cannot be undone and all selected data will be permanently deleted.
                            </label>
                        </div>
                    </div>

                    <div class="text-center">
                        <button class="btn btn-danger btn-lg" onclick="requestDeletion()">
                            <i class="fas fa-trash-alt me-2"></i>Request Data Deletion
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function requestDeletion() {
            if (!document.getElementById('confirmDeletion').checked) {
                alert('Please confirm that you understand this action cannot be undone.');
                return;
            }
            if (confirm('Are you absolutely sure you want to delete your data? This action cannot be undone.')) {
                alert('Data deletion request submitted. You will receive a confirmation email within 24 hours.');
            }
        }
    </script>
</body>
</html>"""

def get_404_page():
    """404 error page"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>404 - Page Not Found</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .error-page {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
    </style>
</head>
<body>
    <div class="error-page">
        <div class="container text-center">
            <h1 class="display-1">404</h1>
            <h2>Page Not Found</h2>
            <p class="lead">The page you're looking for doesn't exist.</p>
            <a href="/" class="btn btn-light btn-lg">Go Home</a>
        </div>
    </div>
</body>
</html>"""