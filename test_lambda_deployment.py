"""
Test AWS Lambda Deployment for IELTS GenAI Prep
Validates regional routing and Nova Sonic functionality
"""

import requests
import json
import time
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LambdaDeploymentTester:
    """Tests Lambda deployment across regions"""
    
    def __init__(self):
        self.regional_endpoints = {
            'us-east-1': 'https://api-us-east-1.ieltsaiprep.com',
            'eu-west-1': 'https://api-eu-west-1.ieltsaiprep.com',
            'ap-southeast-1': 'https://api-ap-southeast-1.ieltsaiprep.com'
        }
        self.test_user = {
            'email': 'test@ieltsaiprep.com',
            'password': 'TestPassword123!'
        }
        
    def test_health_checks(self) -> Dict:
        """Test health endpoints across all regions"""
        results = {}
        
        for region, endpoint in self.regional_endpoints.items():
            try:
                response = requests.get(f"{endpoint}/health", timeout=10)
                results[region] = {
                    'status_code': response.status_code,
                    'response_time': response.elapsed.total_seconds(),
                    'healthy': response.status_code == 200,
                    'data': response.json() if response.content else {}
                }
                logger.info(f"Health check {region}: {response.status_code}")
            except Exception as e:
                results[region] = {
                    'healthy': False,
                    'error': str(e)
                }
                logger.error(f"Health check failed {region}: {e}")
        
        return results
    
    def test_user_registration(self, region: str) -> Dict:
        """Test user registration in specific region"""
        endpoint = self.regional_endpoints[region]
        
        try:
            # Create unique test user for this region
            test_email = f"test-{region}-{int(time.time())}@ieltsaiprep.com"
            
            response = requests.post(
                f"{endpoint}/api/auth/register",
                json={
                    'email': test_email,
                    'password': self.test_user['password']
                },
                timeout=10
            )
            
            return {
                'success': response.status_code == 201,
                'status_code': response.status_code,
                'data': response.json() if response.content else {},
                'test_email': test_email
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_user_login(self, region: str, email: str) -> Dict:
        """Test user login and session creation"""
        endpoint = self.regional_endpoints[region]
        
        try:
            response = requests.post(
                f"{endpoint}/api/auth/login",
                json={
                    'email': email,
                    'password': self.test_user['password']
                },
                timeout=10
            )
            
            data = response.json() if response.content else {}
            
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'session_id': data.get('session_id'),
                'data': data
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_nova_sonic_routing(self) -> Dict:
        """Test Nova Sonic always routes to us-east-1"""
        results = {}
        
        # Test from different regional endpoints
        for region, endpoint in self.regional_endpoints.items():
            try:
                # First register and login user
                reg_result = self.test_user_registration(region)
                if not reg_result['success']:
                    results[region] = {'error': 'Registration failed', 'details': reg_result}
                    continue
                
                login_result = self.test_user_login(region, reg_result['test_email'])
                if not login_result['success']:
                    results[region] = {'error': 'Login failed', 'details': login_result}
                    continue
                
                # Test Nova Sonic endpoint (should route to us-east-1)
                response = requests.post(
                    f"{endpoint}/api/nova-sonic/speaking",
                    json={
                        'audio_data': 'base64_encoded_test_audio',  # Mock data for testing
                        'session_id': login_result['session_id'],
                        'assessment_type': 'academic_speaking'
                    },
                    timeout=20  # Extended timeout for Nova Sonic
                )
                
                data = response.json() if response.content else {}
                
                results[region] = {
                    'request_region': region,
                    'status_code': response.status_code,
                    'routing_notice': data.get('_routing_notice', ''),
                    'routed_to_us_east_1': 'North America' in data.get('_routing_notice', ''),
                    'response_time': response.elapsed.total_seconds(),
                    'data': data
                }
                
                logger.info(f"Nova Sonic test from {region}: {response.status_code}")
                
            except Exception as e:
                results[region] = {
                    'error': str(e),
                    'request_region': region
                }
                logger.error(f"Nova Sonic test failed from {region}: {e}")
        
        return results
    
    def test_nova_micro_regional(self) -> Dict:
        """Test Nova Micro uses regional endpoints"""
        results = {}
        
        for region, endpoint in self.regional_endpoints.items():
            try:
                # Register and login
                reg_result = self.test_user_registration(region)
                if not reg_result['success']:
                    continue
                
                login_result = self.test_user_login(region, reg_result['test_email'])
                if not login_result['success']:
                    continue
                
                # Test Nova Micro endpoint (should use regional)
                response = requests.post(
                    f"{endpoint}/api/nova-micro/writing",
                    json={
                        'essay_text': 'This is a test essay for IELTS writing assessment.',
                        'prompt': 'Write about the advantages and disadvantages of technology.',
                        'session_id': login_result['session_id'],
                        'assessment_type': 'academic_writing'
                    },
                    timeout=15
                )
                
                results[region] = {
                    'request_region': region,
                    'status_code': response.status_code,
                    'response_time': response.elapsed.total_seconds(),
                    'regional_processing': response.status_code == 200,
                    'data': response.json() if response.content else {}
                }
                
                logger.info(f"Nova Micro test in {region}: {response.status_code}")
                
            except Exception as e:
                results[region] = {
                    'error': str(e),
                    'request_region': region
                }
                logger.error(f"Nova Micro test failed in {region}: {e}")
        
        return results
    
    def test_payment_verification(self) -> Dict:
        """Test app store payment verification"""
        results = {}
        
        # Test Apple payment verification
        try:
            response = requests.post(
                f"{self.regional_endpoints['us-east-1']}/api/purchase/verify-apple",
                json={
                    'receipt_data': 'test_receipt_data',
                    'session_id': 'test_session',
                    'product_id': 'academic_speaking'
                },
                timeout=10
            )
            
            results['apple'] = {
                'status_code': response.status_code,
                'data': response.json() if response.content else {}
            }
            
        except Exception as e:
            results['apple'] = {'error': str(e)}
        
        # Test Google payment verification
        try:
            response = requests.post(
                f"{self.regional_endpoints['us-east-1']}/api/purchase/verify-google",
                json={
                    'purchase_token': 'test_purchase_token',
                    'session_id': 'test_session',
                    'product_id': 'academic_writing'
                },
                timeout=10
            )
            
            results['google'] = {
                'status_code': response.status_code,
                'data': response.json() if response.content else {}
            }
            
        except Exception as e:
            results['google'] = {'error': str(e)}
        
        return results
    
    def run_comprehensive_test(self) -> Dict:
        """Run all tests and generate report"""
        logger.info("Starting comprehensive Lambda deployment tests...")
        
        test_results = {
            'timestamp': time.time(),
            'health_checks': self.test_health_checks(),
            'nova_sonic_routing': self.test_nova_sonic_routing(),
            'nova_micro_regional': self.test_nova_micro_regional(),
            'payment_verification': self.test_payment_verification()
        }
        
        # Generate summary
        summary = self.generate_test_summary(test_results)
        test_results['summary'] = summary
        
        return test_results
    
    def generate_test_summary(self, results: Dict) -> Dict:
        """Generate test summary and recommendations"""
        summary = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'regions_healthy': [],
            'regions_unhealthy': [],
            'nova_sonic_routing_correct': True,
            'nova_micro_regional_working': True,
            'recommendations': []
        }
        
        # Health check summary
        for region, health in results['health_checks'].items():
            if health.get('healthy', False):
                summary['regions_healthy'].append(region)
            else:
                summary['regions_unhealthy'].append(region)
        
        # Nova Sonic routing validation
        for region, test in results['nova_sonic_routing'].items():
            if not test.get('routed_to_us_east_1', False):
                summary['nova_sonic_routing_correct'] = False
                summary['recommendations'].append(f"Fix Nova Sonic routing from {region}")
        
        # Regional performance recommendations
        if len(summary['regions_unhealthy']) > 0:
            summary['recommendations'].append(f"Fix unhealthy regions: {summary['regions_unhealthy']}")
        
        if not summary['nova_sonic_routing_correct']:
            summary['recommendations'].append("Ensure all Nova Sonic calls route to us-east-1")
        
        logger.info(f"Test Summary: {summary['passed_tests']}/{summary['total_tests']} passed")
        
        return summary

def main():
    """Run deployment tests"""
    tester = LambdaDeploymentTester()
    results = tester.run_comprehensive_test()
    
    print("\n" + "="*60)
    print("AWS LAMBDA DEPLOYMENT TEST RESULTS")
    print("="*60)
    
    # Health checks
    print("\nHealth Checks:")
    for region, health in results['health_checks'].items():
        status = "✓" if health.get('healthy', False) else "✗"
        print(f"  {status} {region}: {health.get('response_time', 'N/A')}s")
    
    # Nova Sonic routing
    print("\nNova Sonic Routing (should all route to us-east-1):")
    for region, test in results['nova_sonic_routing'].items():
        routed = "✓" if test.get('routed_to_us_east_1', False) else "✗"
        print(f"  {routed} From {region}: {test.get('response_time', 'N/A')}s")
    
    # Summary
    summary = results['summary']
    print(f"\nSummary:")
    print(f"  Healthy regions: {summary['regions_healthy']}")
    print(f"  Nova Sonic routing: {'✓' if summary['nova_sonic_routing_correct'] else '✗'}")
    
    if summary['recommendations']:
        print(f"\nRecommendations:")
        for rec in summary['recommendations']:
            print(f"  - {rec}")
    
    # Save detailed results
    with open('lambda_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed results saved to: lambda_test_results.json")

if __name__ == "__main__":
    main()