"""
Maya Conversation System Diagnostic Report
Comprehensive analysis of the "Start a conversation with Maya" trigger and flow
"""

import os
import sys
from datetime import datetime

def run_maya_diagnostic():
    """Run comprehensive diagnostic on Maya conversation system"""
    
    print("=" * 60)
    print("MAYA CONVERSATION SYSTEM DIAGNOSTIC REPORT")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. Check route definitions
    print("\n1. ROUTE ANALYSIS")
    print("-" * 30)
    
    routes_found = check_maya_routes()
    print(f"✓ Found {len(routes_found)} Maya-related routes:")
    for route in routes_found:
        print(f"  - {route}")
    
    # 2. Check Nova Sonic service
    print("\n2. NOVA SONIC SERVICE ANALYSIS")
    print("-" * 30)
    
    service_status = check_nova_sonic_service()
    print(f"Service Status: {service_status}")
    
    # 3. Check template integration
    print("\n3. TEMPLATE INTEGRATION ANALYSIS")
    print("-" * 30)
    
    template_status = check_conversational_template()
    print(f"Template Status: {template_status}")
    
    # 4. Check authentication flow
    print("\n4. AUTHENTICATION FLOW ANALYSIS")
    print("-" * 30)
    
    auth_status = check_authentication_integration()
    print(f"Authentication Status: {auth_status}")
    
    # 5. Check AWS credentials
    print("\n5. AWS CREDENTIALS ANALYSIS")
    print("-" * 30)
    
    aws_status = check_aws_credentials()
    print(f"AWS Status: {aws_status}")
    
    # 6. Identify potential issues
    print("\n6. POTENTIAL ISSUES IDENTIFIED")
    print("-" * 30)
    
    issues = identify_potential_issues()
    if issues:
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")
    else:
        print("✓ No critical issues identified")
    
    # 7. Flow summary
    print("\n7. COMPLETE FLOW SUMMARY")
    print("-" * 30)
    
    print_flow_summary()
    
    print("\n" + "=" * 60)

def check_maya_routes():
    """Check Maya-related routes in routes.py"""
    routes = []
    try:
        with open('routes.py', 'r') as f:
            content = f.read()
            
        if '/api/start_conversation' in content:
            routes.append('/api/start_conversation - Start Maya conversation')
        if '/api/continue_conversation' in content:
            routes.append('/api/continue_conversation - Continue conversation')
        if '/api/assess_conversation' in content:
            routes.append('/api/assess_conversation - Final assessment')
        if '/api/generate_speech' in content:
            routes.append('/api/generate_speech - Generate Maya voice')
        if 'conversational_speaking_assessment' in content:
            routes.append('/assessments/.../conversational - Main interface')
            
    except Exception as e:
        routes.append(f"Error reading routes: {e}")
        
    return routes

def check_nova_sonic_service():
    """Check Nova Sonic service implementation"""
    try:
        if os.path.exists('nova_sonic_services.py'):
            with open('nova_sonic_services.py', 'r') as f:
                content = f.read()
                
            checks = {
                'Class definition': 'class NovaSonicService' in content,
                'AWS client init': 'boto3.client' in content,
                'Speech generation': 'generate_speech' in content,
                'Conversation creation': 'create_speaking_conversation' in content,
                'Conversation continuation': 'continue_conversation' in content,
                'Assessment method': 'assess_browser_transcript' in content,
                'Error handling': 'ClientError' in content and 'try:' in content
            }
            
            passed = sum(checks.values())
            total = len(checks)
            
            status = f"✓ {passed}/{total} components found"
            for check, result in checks.items():
                symbol = "✓" if result else "✗"
                print(f"  {symbol} {check}")
                
            return status
        else:
            return "✗ nova_sonic_services.py not found"
            
    except Exception as e:
        return f"✗ Error checking service: {e}"

def check_conversational_template():
    """Check conversational speaking template"""
    try:
        template_path = 'templates/assessments/conversational_speaking.html'
        if os.path.exists(template_path):
            with open(template_path, 'r') as f:
                content = f.read()
                
            checks = {
                'Maya references': 'Maya' in content,
                'Start conversation button': 'startConversationBtn' in content or 'start' in content.lower(),
                'Speech recognition': 'speechRecognition' in content or 'webkitSpeechRecognition' in content,
                'Audio playback': 'audio' in content.lower() and 'play' in content,
                'API calls': '/api/start_conversation' in content,
                'Error handling': 'catch' in content and 'error' in content,
                'Voice visualization': 'voiceGlobe' in content or 'canvas' in content
            }
            
            passed = sum(checks.values())
            total = len(checks)
            
            for check, result in checks.items():
                symbol = "✓" if result else "✗"
                print(f"  {symbol} {check}")
                
            return f"✓ {passed}/{total} template features found"
        else:
            return "✗ conversational_speaking.html not found"
            
    except Exception as e:
        return f"✗ Error checking template: {e}"

def check_authentication_integration():
    """Check authentication requirements"""
    try:
        with open('routes.py', 'r') as f:
            content = f.read()
            
        checks = {
            'Login required decorator': '@login_required' in content,
            'User context': 'current_user' in content,
            'CSRF protection': 'csrf' in content.lower() or 'CSRFProtect' in content,
            'Session management': 'session' in content.lower()
        }
        
        passed = sum(checks.values())
        total = len(checks)
        
        for check, result in checks.items():
            symbol = "✓" if result else "✗"
            print(f"  {symbol} {check}")
            
        return f"✓ {passed}/{total} auth features found"
        
    except Exception as e:
        return f"✗ Error checking auth: {e}"

def check_aws_credentials():
    """Check AWS credentials availability"""
    credentials = {
        'AWS_ACCESS_KEY_ID': os.environ.get('AWS_ACCESS_KEY_ID'),
        'AWS_SECRET_ACCESS_KEY': os.environ.get('AWS_SECRET_ACCESS_KEY'),
        'AWS_REGION': os.environ.get('AWS_REGION')
    }
    
    available = sum(1 for v in credentials.values() if v)
    total = len(credentials)
    
    for key, value in credentials.items():
        symbol = "✓" if value else "✗"
        status = "Set" if value else "Missing"
        print(f"  {symbol} {key}: {status}")
    
    return f"✓ {available}/{total} credentials available"

def identify_potential_issues():
    """Identify potential issues in the system"""
    issues = []
    
    # Check for common problems
    try:
        # CSRF token issue
        if os.path.exists('routes.py'):
            with open('routes.py', 'r') as f:
                routes_content = f.read()
            if 'csrf.exempt' not in routes_content and '/api/' in routes_content:
                issues.append("CSRF protection may block API calls - consider adding @csrf.exempt to API routes")
        
        # AWS credentials
        if not os.environ.get('AWS_ACCESS_KEY_ID'):
            issues.append("AWS credentials missing - Nova Sonic will not function")
        
        # Template issues
        template_path = 'templates/assessments/conversational_speaking.html'
        if os.path.exists(template_path):
            with open(template_path, 'r') as f:
                template_content = f.read()
            if 'fetch(' in template_content and 'csrf' not in template_content.lower():
                issues.append("API calls in template may lack CSRF tokens")
        
    except Exception as e:
        issues.append(f"Error during issue detection: {e}")
    
    return issues

def print_flow_summary():
    """Print complete Maya conversation flow"""
    flow_steps = [
        "1. User clicks 'Start Conversation with Maya' button",
        "2. Frontend calls /api/start_conversation with assessment_type and part",
        "3. Backend creates Nova Sonic conversation session",
        "4. Maya responds with opening message using British voice",
        "5. User speaks → Browser speech recognition → Text transcript",
        "6. Frontend calls /api/continue_conversation with user transcript",
        "7. Nova Sonic processes conversation and generates response",
        "8. Maya responds with follow-up questions/comments",
        "9. Cycle continues through IELTS speaking parts 1, 2, 3",
        "10. Final assessment via /api/assess_conversation"
    ]
    
    for step in flow_steps:
        print(f"  {step}")

if __name__ == '__main__':
    run_maya_diagnostic()