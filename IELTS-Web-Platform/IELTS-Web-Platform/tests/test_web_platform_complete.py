#!/usr/bin/env python3
"""
Complete Web Platform Testing for IELTS GenAI Prep
Tests all web platform features including reCAPTCHA integration
"""

import json
import urllib.request
import urllib.parse
import urllib.error
import time
from datetime import datetime

class WebPlatformTester:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.session_cookies = {}
        self.test_results = []
    
    def make_request(self, endpoint, method='GET', data=None, headers=None):
        """Make HTTP request with session handling"""
        url = self.base_url + endpoint
        
        if headers is None:
            headers = {}
        
        # Add cookies for session management
        if self.session_cookies:
            cookie_header = '; '.join([f'{k}={v}' for k, v in self.session_cookies.items()])
            headers['Cookie'] = cookie_header
        
        try:
            if method == 'POST':
                if data:
                    if isinstance(data, dict):
                        data = json.dumps(data).encode('utf-8')
                        headers['Content-Type'] = 'application/json'
                    elif isinstance(data, str):
                        data = data.encode('utf-8')
                
                req = urllib.request.Request(url, data=data, headers=headers, method='POST')
            else:
                req = urllib.request.Request(url, headers=headers)
            
            response = urllib.request.urlopen(req, timeout=15)
            
            # Extract cookies from response
            if 'Set-Cookie' in response.headers:
                cookie_header = response.headers['Set-Cookie']
                # Simple cookie parsing
                for cookie in cookie_header.split(','):
                    if '=' in cookie:
                        key, value = cookie.split('=', 1)
                        self.session_cookies[key.strip()] = value.split(';')[0].strip()
            
            return {
                'status': response.getcode(),
                'headers': dict(response.headers),
                'body': response.read().decode('utf-8')
            }
            
        except urllib.error.HTTPError as e:
            return {
                'status': e.code,
                'headers': dict(e.headers) if hasattr(e, 'headers') else {},
                'body': e.read().decode('utf-8') if hasattr(e, 'read') else str(e),
                'error': True
            }
        except Exception as e:
            return {
                'status': 0,
                'headers': {},
                'body': str(e),
                'error': True
            }
    
    def test_home_page(self):
        """Test home page loads correctly"""
        print("🏠 Testing home page...")
        
        response = self.make_request('/')
        
        if response['status'] == 200:
            body = response['body']
            if 'IELTS GenAI Prep' in body and 'Master IELTS' in body:
                self.test_results.append(('Home Page', 'PASS', 'Page loads with correct branding'))
                print("✅ Home page loads correctly")
                return True
            else:
                self.test_results.append(('Home Page', 'FAIL', 'Missing expected content'))
                print("❌ Home page missing expected content")
                return False
        else:
            self.test_results.append(('Home Page', 'FAIL', f'HTTP {response["status"]}'))
            print(f"❌ Home page failed: HTTP {response['status']}")
            return False
    
    def test_login_page(self):
        """Test login page with reCAPTCHA"""
        print("🔐 Testing login page...")
        
        response = self.make_request('/login')
        
        if response['status'] == 200:
            body = response['body']
            checks = [
                ('reCAPTCHA script', 'www.google.com/recaptcha/api.js' in body),
                ('reCAPTCHA widget', 'g-recaptcha' in body),
                ('Site key', '6LdD2VUrAAAAABG_Tt5fFYmWkRB4YFVHPdjggYzQ' in body),
                ('Login form', 'method="POST"' in body),
                ('Email field', 'name="email"' in body),
                ('Password field', 'name="password"' in body)
            ]
            
            passed_checks = [check for check, result in checks if result]
            failed_checks = [check for check, result in checks if not result]
            
            if len(passed_checks) == len(checks):
                self.test_results.append(('Login Page', 'PASS', 'All components present'))
                print("✅ Login page with reCAPTCHA configured correctly")
                return True
            else:
                self.test_results.append(('Login Page', 'PARTIAL', f'Missing: {failed_checks}'))
                print(f"⚠️ Login page issues: {failed_checks}")
                return False
        else:
            self.test_results.append(('Login Page', 'FAIL', f'HTTP {response["status"]}'))
            print(f"❌ Login page failed: HTTP {response['status']}")
            return False
    
    def test_health_check(self):
        """Test health check endpoint"""
        print("💓 Testing health check...")
        
        response = self.make_request('/api/health', method='POST')
        
        if response['status'] == 200:
            try:
                data = json.loads(response['body'])
                if data.get('status') == 'healthy':
                    services = data.get('services', {})
                    recaptcha_status = services.get('recaptcha', 'unknown')
                    
                    self.test_results.append(('Health Check', 'PASS', f'reCAPTCHA: {recaptcha_status}'))
                    print(f"✅ Health check passed, reCAPTCHA: {recaptcha_status}")
                    return True
                else:
                    self.test_results.append(('Health Check', 'FAIL', 'Unhealthy status'))
                    print("❌ Health check reports unhealthy")
                    return False
            except json.JSONDecodeError:
                self.test_results.append(('Health Check', 'FAIL', 'Invalid JSON response'))
                print("❌ Health check returned invalid JSON")
                return False
        else:
            self.test_results.append(('Health Check', 'FAIL', f'HTTP {response["status"]}'))
            print(f"❌ Health check failed: HTTP {response['status']}")
            return False
    
    def test_recaptcha_validation(self):
        """Test reCAPTCHA validation endpoint"""
        print("🤖 Testing reCAPTCHA validation...")
        
        # Test with invalid reCAPTCHA response
        test_data = {
            'email': 'test@example.com',
            'password': 'testpassword123',
            'recaptcha_response': 'invalid_recaptcha_token'
        }
        
        response = self.make_request('/api/register', method='POST', data=test_data)
        
        if response['status'] in [400, 403]:
            try:
                data = json.loads(response['body'])
                if 'recaptcha' in data.get('error', '').lower() or 'captcha' in data.get('message', '').lower():
                    self.test_results.append(('reCAPTCHA Validation', 'PASS', 'Properly rejects invalid tokens'))
                    print("✅ reCAPTCHA validation working (rejects invalid tokens)")
                    return True
                else:
                    self.test_results.append(('reCAPTCHA Validation', 'PARTIAL', 'Rejects but unclear reason'))
                    print("⚠️ reCAPTCHA validation unclear")
                    return False
            except json.JSONDecodeError:
                self.test_results.append(('reCAPTCHA Validation', 'FAIL', 'Invalid response format'))
                print("❌ reCAPTCHA validation response invalid")
                return False
        else:
            self.test_results.append(('reCAPTCHA Validation', 'FAIL', f'Unexpected status: {response["status"]}'))
            print(f"❌ reCAPTCHA validation unexpected response: {response['status']}")
            return False
    
    def test_nova_ai_endpoints(self):
        """Test Nova AI integration endpoints"""
        print("🤖 Testing Nova AI endpoints...")
        
        endpoints = [
            ('/api/nova-sonic-connect', 'Nova Sonic Connection'),
            ('/api/questions/academic-writing', 'Academic Writing Questions'),
            ('/api/questions/general-writing', 'General Writing Questions'),
            ('/api/questions/academic-speaking', 'Academic Speaking Questions'),
            ('/api/questions/general-speaking', 'General Speaking Questions')
        ]
        
        passed = 0
        total = len(endpoints)
        
        for endpoint, name in endpoints:
            if endpoint.endswith('questions'):
                response = self.make_request(endpoint, method='GET')
            else:
                response = self.make_request(endpoint, method='POST')
            
            if response['status'] == 200:
                try:
                    data = json.loads(response['body'])
                    if data.get('status') == 'success' or 'questions' in data:
                        self.test_results.append((name, 'PASS', 'Endpoint working'))
                        print(f"✅ {name}: Working")
                        passed += 1
                    else:
                        self.test_results.append((name, 'FAIL', 'Unexpected response'))
                        print(f"❌ {name}: Unexpected response")
                except json.JSONDecodeError:
                    self.test_results.append((name, 'FAIL', 'Invalid JSON'))
                    print(f"❌ {name}: Invalid JSON response")
            else:
                self.test_results.append((name, 'FAIL', f'HTTP {response["status"]}'))
                print(f"❌ {name}: HTTP {response['status']}")
        
        return passed == total
    
    def test_static_assets(self):
        """Test static assets and templates"""
        print("📁 Testing static assets...")
        
        # Test template pages
        pages = [
            ('/privacy_policy', 'Privacy Policy'),
            ('/terms_of_service', 'Terms of Service'),
            ('/profile', 'Profile Page'),
            ('/dashboard', 'Dashboard')
        ]
        
        passed = 0
        
        for endpoint, name in pages:
            response = self.make_request(endpoint)
            
            if response['status'] in [200, 302, 401]:  # 401 for protected pages is OK
                self.test_results.append((name, 'PASS', f'HTTP {response["status"]}'))
                print(f"✅ {name}: Accessible")
                passed += 1
            else:
                self.test_results.append((name, 'FAIL', f'HTTP {response["status"]}'))
                print(f"❌ {name}: HTTP {response['status']}")
        
        return passed > 0
    
    def test_mobile_compatibility(self):
        """Test mobile-specific features"""
        print("📱 Testing mobile compatibility...")
        
        # Test with mobile user agent
        mobile_headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
        }
        
        response = self.make_request('/', headers=mobile_headers)
        
        if response['status'] == 200:
            body = response['body']
            mobile_features = [
                ('Viewport meta', 'viewport' in body),
                ('Bootstrap responsive', 'bootstrap' in body.lower()),
                ('Mobile-first design', 'mobile-first' in body.lower()),
                ('App store links', 'app-store' in body.lower() or 'google-play' in body.lower())
            ]
            
            passed_features = [feature for feature, present in mobile_features if present]
            
            if len(passed_features) >= 2:
                self.test_results.append(('Mobile Compatibility', 'PASS', f'{len(passed_features)}/4 features'))
                print(f"✅ Mobile compatibility: {len(passed_features)}/4 features present")
                return True
            else:
                self.test_results.append(('Mobile Compatibility', 'PARTIAL', f'{len(passed_features)}/4 features'))
                print(f"⚠️ Mobile compatibility: Only {len(passed_features)}/4 features")
                return False
        else:
            self.test_results.append(('Mobile Compatibility', 'FAIL', f'HTTP {response["status"]}'))
            print(f"❌ Mobile compatibility test failed: HTTP {response['status']}")
            return False
    
    def run_all_tests(self):
        """Run all tests and generate report"""
        print("🧪 IELTS GenAI Prep - Web Platform Testing")
        print("=" * 60)
        print(f"Testing URL: {self.base_url}")
        print(f"Started: {datetime.utcnow().isoformat()}")
        print()
        
        # Run all tests
        tests = [
            self.test_home_page,
            self.test_login_page,
            self.test_health_check,
            self.test_recaptcha_validation,
            self.test_nova_ai_endpoints,
            self.test_static_assets,
            self.test_mobile_compatibility
        ]
        
        passed_tests = 0
        
        for test in tests:
            try:
                if test():
                    passed_tests += 1
                print()  # Add spacing between tests
            except Exception as e:
                print(f"❌ Test {test.__name__} crashed: {str(e)}")
                self.test_results.append((test.__name__, 'CRASH', str(e)))
                print()
        
        # Generate summary report
        self.generate_report(passed_tests, len(tests))
    
    def generate_report(self, passed_tests, total_tests):
        """Generate comprehensive test report"""
        print("=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        print(f"\n🎯 Overall Results:")
        print(f"   Tests Passed: {passed_tests}/{total_tests}")
        print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Categorize results
        passed = [r for r in self.test_results if r[1] == 'PASS']
        failed = [r for r in self.test_results if r[1] == 'FAIL']
        partial = [r for r in self.test_results if r[1] == 'PARTIAL']
        crashed = [r for r in self.test_results if r[1] == 'CRASH']
        
        if passed:
            print(f"\n✅ Passed Tests ({len(passed)}):")
            for test, status, details in passed:
                print(f"   • {test}: {details}")
        
        if partial:
            print(f"\n⚠️ Partial Tests ({len(partial)}):")
            for test, status, details in partial:
                print(f"   • {test}: {details}")
        
        if failed:
            print(f"\n❌ Failed Tests ({len(failed)}):")
            for test, status, details in failed:
                print(f"   • {test}: {details}")
        
        if crashed:
            print(f"\n💥 Crashed Tests ({len(crashed)}):")
            for test, status, details in crashed:
                print(f"   • {test}: {details}")
        
        # reCAPTCHA specific summary
        recaptcha_tests = [r for r in self.test_results if 'recaptcha' in r[0].lower() or 'captcha' in r[2].lower()]
        if recaptcha_tests:
            print(f"\n🤖 reCAPTCHA Integration:")
            for test, status, details in recaptcha_tests:
                icon = "✅" if status == "PASS" else "⚠️" if status == "PARTIAL" else "❌"
                print(f"   {icon} {test}: {details}")
        
        # Recommendations
        print(f"\n📋 Recommendations:")
        
        if passed_tests == total_tests:
            print("   🎉 All tests passed! Your web platform is ready for production.")
        elif passed_tests >= total_tests * 0.8:
            print("   👍 Most tests passed. Address failing tests before production.")
        else:
            print("   ⚠️ Several tests failed. Review and fix issues before deployment.")
        
        if any('reCAPTCHA' in r[0] and r[1] == 'PASS' for r in self.test_results):
            print("   🔐 reCAPTCHA integration is working correctly.")
        else:
            print("   🔐 Verify reCAPTCHA configuration and secret key.")
        
        # Save detailed report
        report_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'base_url': self.base_url,
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'success_rate': (passed_tests/total_tests)*100
            },
            'detailed_results': self.test_results
        }
        
        with open('web_platform_test_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n💾 Detailed report saved to: web_platform_test_report.json")

def main():
    """Main testing function"""
    import sys
    
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        # Try to load from deployment info
        try:
            with open('web_deployment_info.json', 'r') as f:
                deployment_info = json.load(f)
                base_url = deployment_info.get('api_gateway', {}).get('api_url')
                if not base_url:
                    base_url = deployment_info.get('lambda_function', {}).get('function_url')
        except FileNotFoundError:
            base_url = None
        
        if not base_url:
            print("Usage: python test_web_platform_complete.py <base_url>")
            print("Or run deploy_web_platform_complete.py first to auto-detect URL")
            return
    
    # Initialize tester and run all tests
    tester = WebPlatformTester(base_url)
    tester.run_all_tests()

if __name__ == '__main__':
    main()