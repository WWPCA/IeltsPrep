"""
Regional API Router for IELTS GenAI Prep
Routes users to nearest regional endpoint except Nova Sonic (us-east-1 only)
"""

import requests
import json
from typing import Dict, Optional

class RegionalRouter:
    """Handles routing to appropriate regional endpoints"""
    
    def __init__(self):
        self.regions = {
            'us-east-1': 'https://api-us-east-1.ieltsaiprep.com',
            'eu-west-1': 'https://api-eu-west-1.ieltsaiprep.com', 
            'ap-southeast-1': 'https://api-ap-southeast-1.ieltsaiprep.com'
        }
        self.nova_sonic_endpoint = 'https://api-us-east-1.ieltsaiprep.com'  # Fixed to us-east-1
        
    def get_user_region(self, user_ip: str) -> str:
        """Determine user's optimal region based on IP geolocation"""
        try:
            # Use Route 53 health checks or IP geolocation service
            response = requests.get(f'http://ip-api.com/json/{user_ip}', timeout=3)
            if response.status_code == 200:
                data = response.json()
                country = data.get('countryCode', 'US')
                
                # Map countries to regions
                if country in ['US', 'CA', 'MX', 'BR', 'AR']:
                    return 'us-east-1'
                elif country in ['GB', 'FR', 'DE', 'IT', 'ES', 'NL', 'SE', 'NO']:
                    return 'eu-west-1'
                elif country in ['SG', 'MY', 'TH', 'ID', 'PH', 'VN', 'AU', 'NZ', 'JP', 'KR', 'IN']:
                    return 'ap-southeast-1'
                else:
                    return 'us-east-1'  # Default
        except:
            return 'us-east-1'  # Fallback
    
    def route_request(self, endpoint: str, user_ip: str, method: str = 'POST', 
                     data: Dict = None, headers: Dict = None) -> requests.Response:
        """Route request to appropriate regional endpoint"""
        
        # Nova Sonic always routes to us-east-1
        if '/nova-sonic/' in endpoint:
            base_url = self.nova_sonic_endpoint
            # Add user notification about potential latency
            if data:
                data['_routing_notice'] = 'Routed to North America for Nova Sonic - may experience latency'
        else:
            # Route to nearest region for other services
            region = self.get_user_region(user_ip)
            base_url = self.regions[region]
        
        full_url = f"{base_url}{endpoint}"
        
        # Add retry logic with exponential backoff
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if method.upper() == 'POST':
                    response = requests.post(
                        full_url, 
                        json=data, 
                        headers=headers,
                        timeout=15 if '/nova-sonic/' in endpoint else 10
                    )
                elif method.upper() == 'GET':
                    response = requests.get(
                        full_url, 
                        params=data, 
                        headers=headers,
                        timeout=15 if '/nova-sonic/' in endpoint else 10
                    )
                
                if response.status_code < 500:  # Don't retry client errors
                    return response
                    
            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    raise e
                # Exponential backoff: 1s, 2s, 4s
                import time
                time.sleep(2 ** attempt)
        
        return response

# Global router instance
router = RegionalRouter()

def make_regional_api_call(endpoint: str, user_ip: str, method: str = 'POST', 
                          data: Dict = None, headers: Dict = None) -> Dict:
    """Convenience function for making regional API calls"""
    try:
        response = router.route_request(endpoint, user_ip, method, data, headers)
        return {
            'success': response.status_code < 400,
            'status_code': response.status_code,
            'data': response.json() if response.content else {},
            'region_used': router.get_user_region(user_ip)
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'region_used': router.get_user_region(user_ip)
        }