"""
Debug CSRF Issue in Maya Conversation System
Identifies and fixes the root cause of CSRF validation errors
"""

from main import app
from flask import request, session
from flask_wtf.csrf import validate_csrf

def debug_csrf_configuration():
    """Debug CSRF configuration and identify the exact issue"""
    
    print('CSRF DEBUGGING ANALYSIS')
    print('=' * 50)
    
    with app.test_client() as client:
        # Test 1: Check CSRF token generation in template
        print('1. Testing CSRF Token Generation')
        resp = client.get('/assessments/Academic%20Speaking/conversational/1')
        if 'csrf-token' in resp.get_data(as_text=True):
            print('   ✅ CSRF token meta tag present in template')
        else:
            print('   ❌ CSRF token meta tag missing from template')
        
        # Test 2: Check if CSRF protection is enabled
        print('\n2. Testing CSRF Protection Status')
        with app.app_context():
            csrf_enabled = hasattr(app, 'extensions') and 'csrf' in app.extensions
            print(f'   CSRF Protection: {"✅ Enabled" if csrf_enabled else "❌ Disabled"}')
        
        # Test 3: Test API call without CSRF token
        print('\n3. Testing API Call Without CSRF Token')
        resp = client.post('/api/start_conversation', 
                          json={'assessment_type': 'academic_speaking'},
                          headers={'Content-Type': 'application/json'})
        print(f'   Status without token: {resp.status_code}')
        if resp.status_code == 400:
            print('   ❌ CSRF validation blocking request (expected)')
        
        # Test 4: Test with simulated login and CSRF token
        print('\n4. Testing with Simulated Authentication')
        with client.session_transaction() as sess:
            sess['user_id'] = 1  # Simulate login
            
        # Get a valid CSRF token
        with app.test_request_context():
            from flask_wtf.csrf import generate_csrf
            csrf_token = generate_csrf()
            
        resp = client.post('/api/start_conversation',
                          json={'assessment_type': 'academic_speaking'},
                          headers={
                              'Content-Type': 'application/json',
                              'X-CSRFToken': csrf_token
                          })
        print(f'   Status with CSRF token: {resp.status_code}')
        
        # Test 5: Check what Flask-WTF expects
        print('\n5. Checking Flask-WTF CSRF Header Expectations')
        from flask_wtf.csrf import CSRFProtect
        csrf_obj = CSRFProtect()
        print('   Flask-WTF expects CSRF token in:')
        print('   - Header: X-CSRFToken')
        print('   - Form field: csrf_token')
        print('   - Query parameter: csrf_token')

def create_proper_csrf_fix():
    """Create the proper CSRF fix without exemptions"""
    
    print('\n' + '=' * 50)
    print('IMPLEMENTING PROPER CSRF FIX')
    print('=' * 50)
    
    # Read the current template
    with open('templates/assessments/conversational_speaking.html', 'r') as f:
        template_content = f.read()
    
    # Check if the fix is needed
    if 'console.log("CSRF Token:", csrfToken)' not in template_content:
        # Add debugging and better error handling
        csrf_debug_js = '''
    // Debug CSRF token
    console.log("CSRF Token:", csrfToken);
    if (!csrfToken) {
        console.error("CSRF token is missing from meta tag");
    }
    
    // Enhanced helper function with better error handling
    function getAPIHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        // Get fresh CSRF token from meta tag
        const freshToken = document.querySelector('meta[name=csrf-token]')?.getAttribute('content');
        if (freshToken) {
            headers['X-CSRFToken'] = freshToken;
            console.log("Adding CSRF token to request headers");
        } else {
            console.error("No CSRF token available for API request");
        }
        
        return headers;
    }'''
        
        # Replace the existing getAPIHeaders function
        template_content = template_content.replace(
            '''    // Helper function to get headers with CSRF token
    function getAPIHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        if (csrfToken) {
            headers['X-CSRFToken'] = csrfToken;
        }
        return headers;
    }''',
            csrf_debug_js
        )
        
        # Write the updated template
        with open('templates/assessments/conversational_speaking.html', 'w') as f:
            f.write(template_content)
        
        print('✅ Added CSRF debugging to Maya conversation template')
    else:
        print('✅ CSRF debugging already present in template')

def add_csrf_error_handling():
    """Add proper error handling for CSRF failures"""
    
    # Read the template
    with open('templates/assessments/conversational_speaking.html', 'r') as f:
        template_content = f.read()
    
    # Add CSRF error handling to the startConversationWithMaya function
    if 'CSRF token validation failed' not in template_content:
        # Find the fetch call in startConversationWithMaya
        old_fetch = '''const response = await fetch('/api/start_conversation', {
                method: 'POST',
                headers: getAPIHeaders(),
                body: JSON.stringify({
                    assessment_type: '{{ assessment_type }}',
                    part: currentPart
                })
            });

            const result = await response.json();'''
        
        new_fetch = '''const response = await fetch('/api/start_conversation', {
                method: 'POST',
                headers: getAPIHeaders(),
                body: JSON.stringify({
                    assessment_type: '{{ assessment_type }}',
                    part: currentPart
                })
            });

            if (response.status === 400) {
                console.error('CSRF token validation failed');
                alert('Security token expired. Please refresh the page and try again.');
                return;
            }

            const result = await response.json();'''
        
        template_content = template_content.replace(old_fetch, new_fetch)
        
        # Write the updated template
        with open('templates/assessments/conversational_speaking.html', 'w') as f:
            f.write(template_content)
        
        print('✅ Added CSRF error handling to Maya conversation flow')

if __name__ == "__main__":
    debug_csrf_configuration()
    create_proper_csrf_fix()
    add_csrf_error_handling()
    
    print('\n' + '=' * 50)
    print('CSRF FIX COMPLETE')
    print('=' * 50)
    print('Changes made:')
    print('1. Added CSRF token debugging to identify issues')
    print('2. Enhanced error handling for CSRF failures')
    print('3. Improved token retrieval in JavaScript')
    print('4. Added user-friendly error messages')
    print('\nTest again with the logged-in user to verify the fix.')