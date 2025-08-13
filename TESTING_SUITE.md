# Complete Testing Suite Documentation

## Unit Tests for Core Functions

### Authentication Testing
```python
import pytest
import bcrypt
from unittest.mock import Mock, patch

def test_user_registration():
    """Test complete user registration flow"""
    user_data = {
        'email': 'test@example.com',
        'password': 'SecurePass123!',
        'first_name': 'John',
        'last_name': 'Doe'
    }
    
    result = register_user(user_data)
    assert result['success'] == True
    assert 'user_id' in result
    assert bcrypt.checkpw(user_data['password'].encode(), result['password_hash'].encode())

def test_qr_authentication():
    """Test QR code generation and verification"""
    user_id = 'test-user-123'
    
    # Generate QR code
    qr_code = generate_qr_auth_code(user_id)
    assert len(qr_code) == 36  # UUID length
    
    # Verify QR code
    session = verify_qr_code(qr_code, 'device-fingerprint')
    assert session is not None
    assert session['user_id'] == user_id

def test_purchase_validation():
    """Test mobile purchase validation"""
    ios_receipt = "base64-encoded-receipt-data"
    android_token = "google-play-purchase-token"
    
    # Test iOS validation
    ios_result = validate_ios_purchase(ios_receipt, 'academic_writing_assessment')
    assert ios_result['valid'] == True
    
    # Test Android validation  
    android_result = validate_android_purchase(android_token, 'academic_writing_assessment')
    assert android_result['valid'] == True
```

### Assessment Engine Testing
```python
def test_writing_assessment():
    """Test AI writing assessment with Nova Micro"""
    essay = """
    Some people believe that technology has made our lives more complex. 
    However, I strongly disagree with this statement. Technology has actually 
    simplified many aspects of our daily lives and made tasks more efficient.
    
    Firstly, communication has become much easier through smartphones and social media.
    In the past, people had to write letters and wait days for responses. Now, we can
    instantly connect with anyone around the world through messaging apps and video calls.
    
    Secondly, access to information has been revolutionized by the internet.
    Students can now research any topic within seconds, while in the past they had to
    visit libraries and search through physical books for hours.
    
    In conclusion, while technology may seem complex on the surface, it has
    fundamentally simplified how we communicate, learn, and work in modern society.
    """
    
    result = assess_writing(essay, 'academic_task2')
    
    assert result['overall_band'] >= 6.0
    assert result['overall_band'] <= 9.0
    assert 'task_achievement' in result
    assert 'coherence_cohesion' in result
    assert 'lexical_resource' in result
    assert 'grammatical_range' in result
    assert len(result['feedback']) > 100

def test_speaking_assessment():
    """Test AI speaking assessment with Nova Sonic"""
    conversation_data = {
        'part1_responses': ['My name is John.', 'I am from London.', 'I work as a teacher.'],
        'part2_response': 'I would like to describe my favorite book...',
        'part3_responses': ['Education is very important because...', 'In my country, schools...']
    }
    
    result = assess_speaking(conversation_data, 'academic_speaking')
    
    assert result['overall_band'] >= 4.0
    assert result['overall_band'] <= 9.0
    assert 'fluency_coherence' in result
    assert 'pronunciation' in result
    assert 'lexical_resource' in result
    assert 'grammatical_range' in result
```

### Database Testing
```python
def test_dynamodb_operations():
    """Test all DynamoDB table operations"""
    # Test user creation
    user_data = {
        'email': 'test@example.com',
        'user_id': 'test-123',
        'password_hash': 'hashed-password'
    }
    
    result = dynamodb_put_user(user_data)
    assert result == True
    
    # Test user retrieval
    user = dynamodb_get_user('test@example.com')
    assert user['user_id'] == 'test-123'
    
    # Test assessment storage
    assessment_data = {
        'assessment_id': 'assessment-123',
        'user_id': 'test-123',
        'assessment_type': 'academic_writing',
        'ai_feedback': {'overall_band': 7.0}
    }
    
    result = dynamodb_put_assessment(assessment_data)
    assert result == True
    
    # Test GDPR data export
    export_data = dynamodb_export_user_data('test-123')
    assert 'user_profile' in export_data
    assert 'assessment_history' in export_data
    assert 'purchase_history' in export_data

def test_ttl_functionality():
    """Test Time-To-Live functionality for sessions and QR codes"""
    import time
    
    # Create session with 1-second TTL for testing
    session_data = {
        'session_id': 'test-session',
        'user_id': 'test-user',
        'expires_at': int(time.time()) + 1
    }
    
    dynamodb_put_session(session_data)
    
    # Immediately retrieve - should exist
    session = dynamodb_get_session('test-session')
    assert session is not None
    
    # Wait for TTL expiry
    time.sleep(2)
    
    # Should be automatically deleted
    session = dynamodb_get_session('test-session')
    assert session is None
```

## Integration Tests

### End-to-End User Flow
```python
def test_complete_user_journey():
    """Test complete user journey from registration to assessment"""
    
    # Step 1: Mobile app registration
    user_data = {
        'email': 'e2e_test@example.com',
        'password': 'TestPassword123!',
        'first_name': 'E2E',
        'last_name': 'Test'
    }
    
    registration_result = mobile_register(user_data)
    assert registration_result['success'] == True
    user_id = registration_result['user_id']
    
    # Step 2: Purchase assessment
    purchase_data = {
        'user_id': user_id,
        'product_id': 'academic_writing_assessment',
        'transaction_id': 'test-transaction-123',
        'receipt_data': 'mock-receipt-data'
    }
    
    purchase_result = process_purchase(purchase_data)
    assert purchase_result['success'] == True
    assert purchase_result['attempts_granted'] == 4
    
    # Step 3: Generate QR code for web access
    qr_code = generate_qr_auth_code(user_id)
    assert qr_code is not None
    
    # Step 4: Verify QR code and create web session
    web_session = verify_qr_code(qr_code, 'test-device-fingerprint')
    assert web_session is not None
    assert web_session['user_id'] == user_id
    
    # Step 5: Access assessment on web platform
    assessment_access = check_assessment_access(user_id, 'academic_writing')
    assert assessment_access['allowed'] == True
    assert assessment_access['attempts_remaining'] == 4
    
    # Step 6: Complete writing assessment
    essay = generate_test_essay()
    assessment_result = complete_writing_assessment(user_id, essay, 'academic_writing')
    
    assert assessment_result['success'] == True
    assert 'overall_band' in assessment_result
    assert 'detailed_feedback' in assessment_result
    
    # Step 7: Verify attempts decremented
    remaining_attempts = get_remaining_attempts(user_id, 'academic_writing')
    assert remaining_attempts == 3
    
    # Step 8: Test GDPR data export
    gdpr_request = request_data_export(user_id)
    assert gdpr_request['success'] == True
    
    export_data = get_exported_data(gdpr_request['request_id'])
    assert 'user_profile' in export_data
    assert 'assessment_history' in export_data
    assert len(export_data['assessment_history']) == 1

def test_cross_platform_session_management():
    """Test session management across mobile and web platforms"""
    user_id = 'cross-platform-test-user'
    
    # Create mobile session
    mobile_session = create_mobile_session(user_id, 'mobile-device-id')
    assert mobile_session['session_id'] is not None
    
    # Generate QR for web access
    qr_code = generate_qr_auth_code(user_id)
    
    # Verify QR and create web session
    web_session = verify_qr_code(qr_code, 'web-device-fingerprint')
    assert web_session['user_id'] == user_id
    
    # Both sessions should be valid
    assert validate_session(mobile_session['session_id']) == True
    assert validate_session(web_session['session_id']) == True
    
    # Logout from mobile should not affect web session
    logout_session(mobile_session['session_id'])
    assert validate_session(mobile_session['session_id']) == False
    assert validate_session(web_session['session_id']) == True
```

### AI Service Integration Tests
```python
def test_bedrock_integration():
    """Test AWS Bedrock Nova models integration"""
    
    # Test Nova Micro for writing assessment
    writing_prompt = "Evaluate this IELTS essay and provide band scores"
    nova_micro_response = call_nova_micro(writing_prompt)
    
    assert nova_micro_response is not None
    assert 'overall_band' in nova_micro_response
    assert isinstance(nova_micro_response['overall_band'], (int, float))
    
    # Test Nova Sonic for speaking assessment
    speaking_input = "Tell me about your hometown"
    nova_sonic_response = call_nova_sonic(speaking_input, voice='en-GB-feminine')
    
    assert nova_sonic_response is not None
    assert 'audio_response' in nova_sonic_response
    assert 'text_response' in nova_sonic_response

def test_ses_email_integration():
    """Test AWS SES email sending"""
    
    # Test welcome email
    welcome_result = send_welcome_email('test@example.com', 'Test User')
    assert welcome_result['success'] == True
    assert welcome_result['message_id'] is not None
    
    # Test account deletion email
    deletion_result = send_account_deletion_email('test@example.com')
    assert deletion_result['success'] == True
    assert deletion_result['message_id'] is not None
```

## Load Testing Scripts

### Concurrent User Simulation
```python
import asyncio
import aiohttp
import time
from concurrent.futures import ThreadPoolExecutor

async def simulate_user_session(session_id):
    """Simulate a complete user session"""
    async with aiohttp.ClientSession() as session:
        
        # Login
        login_data = {
            'email': f'loadtest_{session_id}@example.com',
            'password': 'LoadTest123!'
        }
        async with session.post('/api/login', json=login_data) as resp:
            login_result = await resp.json()
            assert resp.status == 200
        
        # Access dashboard
        async with session.get('/dashboard') as resp:
            assert resp.status == 200
        
        # Start assessment
        async with session.get('/assessment/academic-writing') as resp:
            assert resp.status == 200
        
        # Submit assessment
        assessment_data = {
            'essay': generate_test_essay(),
            'assessment_type': 'academic_writing'
        }
        async with session.post('/api/submit-assessment', json=assessment_data) as resp:
            result = await resp.json()
            assert resp.status == 200
            assert 'overall_band' in result

async def load_test_concurrent_users(num_users=100):
    """Test platform with concurrent users"""
    start_time = time.time()
    
    tasks = []
    for i in range(num_users):
        task = asyncio.create_task(simulate_user_session(i))
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    end_time = time.time()
    duration = end_time - start_time
    
    successful_sessions = sum(1 for r in results if not isinstance(r, Exception))
    failed_sessions = len(results) - successful_sessions
    
    print(f"Load Test Results:")
    print(f"Duration: {duration:.2f} seconds")
    print(f"Successful sessions: {successful_sessions}/{num_users}")
    print(f"Failed sessions: {failed_sessions}/{num_users}")
    print(f"Success rate: {(successful_sessions/num_users)*100:.1f}%")
    
    assert successful_sessions >= num_users * 0.95  # 95% success rate minimum

# Run load test
asyncio.run(load_test_concurrent_users(100))
```

### Database Performance Testing
```python
def test_database_performance():
    """Test DynamoDB query performance under load"""
    import time
    
    # Test batch user creation
    start_time = time.time()
    user_ids = []
    
    for i in range(1000):
        user_data = {
            'email': f'perftest_{i}@example.com',
            'user_id': f'perf-user-{i}',
            'password_hash': 'hashed-password'
        }
        result = dynamodb_put_user(user_data)
        assert result == True
        user_ids.append(user_data['user_id'])
    
    creation_time = time.time() - start_time
    print(f"Created 1000 users in {creation_time:.2f} seconds")
    
    # Test batch user retrieval
    start_time = time.time()
    
    for user_id in user_ids[:100]:  # Test 100 random retrievals
        user = dynamodb_get_user_by_id(user_id)
        assert user is not None
    
    retrieval_time = time.time() - start_time
    print(f"Retrieved 100 users in {retrieval_time:.2f} seconds")
    
    # Performance assertions
    assert creation_time < 30  # Should create 1000 users in under 30 seconds
    assert retrieval_time < 5   # Should retrieve 100 users in under 5 seconds
```

## Security Testing

### Penetration Testing Scenarios
```python
def test_sql_injection_protection():
    """Test protection against SQL injection attacks"""
    malicious_inputs = [
        "'; DROP TABLE users; --",
        "1' OR '1'='1",
        "admin'--",
        "1' UNION SELECT * FROM users--"
    ]
    
    for malicious_input in malicious_inputs:
        # Test login endpoint
        response = post('/api/login', {
            'email': malicious_input,
            'password': 'password'
        })
        assert response.status_code != 200  # Should be rejected
        
        # Test assessment submission
        response = post('/api/submit-assessment', {
            'essay': malicious_input,
            'assessment_type': 'academic_writing'
        })
        # Should handle safely without exposing database structure

def test_xss_protection():
    """Test protection against Cross-Site Scripting"""
    xss_payloads = [
        "<script>alert('XSS')</script>",
        "javascript:alert('XSS')",
        "<img src=x onerror=alert('XSS')>",
        "<svg onload=alert('XSS')>"
    ]
    
    for payload in xss_payloads:
        # Test essay submission
        response = post('/api/submit-assessment', {
            'essay': payload,
            'assessment_type': 'academic_writing'
        })
        
        # Response should not contain executable script
        assert '<script>' not in response.text
        assert 'javascript:' not in response.text

def test_rate_limiting():
    """Test API rate limiting protection"""
    
    # Test login rate limiting
    for i in range(10):  # Attempt 10 rapid logins
        response = post('/api/login', {
            'email': 'test@example.com',
            'password': 'wrong-password'
        })
    
    # Should be rate limited after multiple attempts
    response = post('/api/login', {
        'email': 'test@example.com', 
        'password': 'any-password'
    })
    assert response.status_code == 429  # Too Many Requests

def test_authentication_bypass():
    """Test authentication cannot be bypassed"""
    
    protected_endpoints = [
        '/dashboard',
        '/assessment/academic-writing',
        '/my-profile',
        '/api/submit-assessment'
    ]
    
    for endpoint in protected_endpoints:
        # Try accessing without authentication
        response = get(endpoint)
        assert response.status_code in [401, 403, 302]  # Should redirect or deny
        
        # Try with invalid session
        response = get(endpoint, headers={'Authorization': 'Bearer invalid-token'})
        assert response.status_code in [401, 403]
```

## Automated Testing Pipeline

### GitHub Actions Workflow
```yaml
name: IELTS GenAI Prep Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    - name: Install dependencies
      run: |
        pip install -r requirements-test.txt
    - name: Run unit tests
      run: |
        pytest tests/unit/ -v --cov=app
    - name: Upload coverage reports
      run: |
        codecov

  integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests
    steps:
    - uses: actions/checkout@v2
    - name: Set up test environment
      run: |
        docker-compose -f docker-compose.test.yml up -d
    - name: Run integration tests
      run: |
        pytest tests/integration/ -v
    - name: Cleanup
      run: |
        docker-compose -f docker-compose.test.yml down

  security-tests:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Run security scan
      run: |
        bandit -r app/
        safety check
    - name: Run OWASP ZAP scan
      run: |
        docker run -v $(pwd):/zap/wrk/:rw -t owasp/zap2docker-stable zap-baseline.py -t http://localhost:5000

  performance-tests:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Run load tests
      run: |
        locust -f tests/performance/locustfile.py --headless -u 100 -r 10 -t 300s --host http://localhost:5000
```

### Test Data Management
```python
def setup_test_data():
    """Set up test data for comprehensive testing"""
    
    # Create test users
    test_users = [
        {
            'email': 'student1@test.com',
            'password': 'TestPass123!',
            'assessment_type': 'academic_writing',
            'expected_band': 7.0
        },
        {
            'email': 'student2@test.com', 
            'password': 'TestPass123!',
            'assessment_type': 'general_speaking',
            'expected_band': 6.5
        }
    ]
    
    for user in test_users:
        create_test_user(user)
    
    # Create test questions
    test_questions = load_test_questions_from_files()
    for question in test_questions:
        create_test_question(question)
    
    # Create test purchase data
    test_purchases = [
        {
            'user_email': 'student1@test.com',
            'product_id': 'academic_writing_assessment',
            'attempts': 4
        }
    ]
    
    for purchase in test_purchases:
        create_test_purchase(purchase)

def cleanup_test_data():
    """Clean up test data after testing"""
    delete_test_users()
    delete_test_questions()
    delete_test_purchases()
    delete_test_sessions()
```

This comprehensive testing suite ensures every component of the IELTS GenAI Prep platform is thoroughly tested and validated before deployment.