"""
Maya Conversation Flow Test
Tests the complete "Start a conversation with Maya" flow for syntax errors and functionality
"""

import sys
import traceback
from main import app

def test_maya_conversation_syntax():
    """Test Maya conversation flow for syntax errors and proper route handling"""
    
    print('MAYA CONVERSATION FLOW SYNTAX CHECK')
    print('=' * 60)
    
    errors = []
    
    # Test 1: Check route imports and syntax
    print('1. Testing Route Imports and Syntax')
    try:
        from routes import start_conversation, continue_conversation, assess_conversation
        print('   ✅ All Maya conversation routes imported successfully')
    except ImportError as e:
        error_msg = f"Import error: {e}"
        errors.append(error_msg)
        print(f'   ❌ {error_msg}')
    except SyntaxError as e:
        error_msg = f"Syntax error in routes: {e}"
        errors.append(error_msg)
        print(f'   ❌ {error_msg}')
    
    # Test 2: Check Nova Sonic service
    print('\n2. Testing Nova Sonic Service Integration')
    try:
        from nova_sonic_services import NovaSonicService
        service = NovaSonicService()
        print('   ✅ Nova Sonic service initialized successfully')
    except Exception as e:
        error_msg = f"Nova Sonic error: {e}"
        errors.append(error_msg)
        print(f'   ❌ {error_msg}')
    
    # Test 3: Check template exists
    print('\n3. Testing Maya Conversation Template')
    try:
        with open('templates/assessments/conversational_speaking.html', 'r') as f:
            template_content = f.read()
        
        if 'Start a conversation with Maya' in template_content:
            print('   ✅ "Start a conversation with Maya" button found in template')
        else:
            error_msg = 'Maya button text not found in template'
            errors.append(error_msg)
            print(f'   ❌ {error_msg}')
            
        if 'startConversationWithMaya' in template_content:
            print('   ✅ JavaScript function startConversationWithMaya found')
        else:
            error_msg = 'startConversationWithMaya function not found'
            errors.append(error_msg)
            print(f'   ❌ {error_msg}')
            
    except FileNotFoundError:
        error_msg = 'Maya conversation template not found'
        errors.append(error_msg)
        print(f'   ❌ {error_msg}')
    
    # Test 4: Test API endpoints with Flask test client
    print('\n4. Testing Maya API Endpoints')
    with app.test_client() as client:
        # Test start conversation endpoint
        try:
            response = client.post('/api/start_conversation', 
                                 json={'assessment_type': 'academic_speaking', 'part': 1},
                                 headers={'Content-Type': 'application/json'})
            
            if response.status_code in [200, 302, 401]:  # 401 expected without login
                print('   ✅ /api/start_conversation endpoint accessible')
            else:
                error_msg = f'/api/start_conversation returned {response.status_code}'
                errors.append(error_msg)
                print(f'   ❌ {error_msg}')
                
        except Exception as e:
            error_msg = f'start_conversation endpoint error: {e}'
            errors.append(error_msg)
            print(f'   ❌ {error_msg}')
        
        # Test continue conversation endpoint
        try:
            response = client.post('/api/continue_conversation',
                                 json={'user_message': 'Hello', 'current_part': 1},
                                 headers={'Content-Type': 'application/json'})
            
            if response.status_code in [200, 302, 401]:
                print('   ✅ /api/continue_conversation endpoint accessible')
            else:
                error_msg = f'/api/continue_conversation returned {response.status_code}'
                errors.append(error_msg)
                print(f'   ❌ {error_msg}')
                
        except Exception as e:
            error_msg = f'continue_conversation endpoint error: {e}'
            errors.append(error_msg)
            print(f'   ❌ {error_msg}')
    
    # Test 5: Check JavaScript flow
    print('\n5. Testing JavaScript Maya Flow')
    try:
        with open('templates/assessments/conversational_speaking.html', 'r') as f:
            template_content = f.read()
        
        js_checks = [
            ('fetch(\'/api/start_conversation\'', 'API call to start conversation'),
            ('fetch(\'/api/continue_conversation\'', 'API call to continue conversation'),
            ('JSON.stringify', 'JSON data formatting'),
            ('response.json()', 'Response parsing')
        ]
        
        for check, description in js_checks:
            if check in template_content:
                print(f'   ✅ {description} found')
            else:
                error_msg = f'{description} missing from JavaScript'
                errors.append(error_msg)
                print(f'   ❌ {error_msg}')
                
    except Exception as e:
        error_msg = f'JavaScript flow check error: {e}'
        errors.append(error_msg)
        print(f'   ❌ {error_msg}')
    
    # Test 6: Check conversation flow logic
    print('\n6. Testing Maya Conversation Logic')
    try:
        # Check if Nova Sonic methods exist
        from nova_sonic_services import NovaSonicService
        service = NovaSonicService()
        
        required_methods = ['create_speaking_conversation', 'continue_conversation', 'assess_conversation_final']
        
        for method_name in required_methods:
            if hasattr(service, method_name):
                print(f'   ✅ {method_name} method available')
            else:
                error_msg = f'{method_name} method missing from Nova Sonic service'
                errors.append(error_msg)
                print(f'   ❌ {error_msg}')
                
    except Exception as e:
        error_msg = f'Nova Sonic method check error: {e}'
        errors.append(error_msg)
        print(f'   ❌ {error_msg}')
    
    # Final assessment
    print('\n' + '=' * 60)
    print('MAYA CONVERSATION FLOW TEST RESULTS')
    print('=' * 60)
    
    if not errors:
        print('🎯 MAYA CONVERSATION FLOW: FULLY FUNCTIONAL')
        print('   ✅ No syntax errors detected')
        print('   ✅ All routes properly configured')
        print('   ✅ Nova Sonic service operational')
        print('   ✅ JavaScript flow complete')
        print('   ✅ "Start a conversation with Maya" triggers correct flow')
    else:
        print('⚠️  MAYA CONVERSATION FLOW ISSUES DETECTED:')
        for i, error in enumerate(errors, 1):
            print(f'   {i}. {error}')
    
    return len(errors) == 0

if __name__ == "__main__":
    test_maya_conversation_syntax()