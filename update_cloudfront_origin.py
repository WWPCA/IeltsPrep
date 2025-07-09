#!/usr/bin/env python3
"""
Update CloudFront Origin to Correct API Gateway
"""

import boto3
import json
import time

def update_cloudfront_origin():
    """Update CloudFront to point to correct API Gateway"""
    
    cloudfront = boto3.client('cloudfront', region_name='us-east-1')
    
    print("🔧 Updating CloudFront Origin to Correct API Gateway")
    print("=" * 60)
    
    # The working API Gateway ID
    CORRECT_API_ID = "n0cpf1rmvc"
    CORRECT_DOMAIN = f"{CORRECT_API_ID}.execute-api.us-east-1.amazonaws.com"
    
    print(f"✅ Working API Gateway: {CORRECT_API_ID}")
    print(f"✅ Correct domain: {CORRECT_DOMAIN}")
    
    try:
        # Get current CloudFront distributions
        distributions = cloudfront.list_distributions()
        target_distribution = None
        
        for dist in distributions['DistributionList']['Items']:
            if 'www.ieltsaiprep.com' in dist.get('Aliases', {}).get('Items', []):
                target_distribution = dist
                break
        
        if not target_distribution:
            print("❌ CloudFront distribution for www.ieltsaiprep.com not found")
            return False
        
        distribution_id = target_distribution['Id']
        print(f"✅ Found CloudFront distribution: {distribution_id}")
        
        # Get current distribution config
        config_response = cloudfront.get_distribution_config(Id=distribution_id)
        distribution_config = config_response['DistributionConfig']
        etag = config_response['ETag']
        
        # Update lambda origin to point to correct API Gateway
        origin_updated = False
        for origin in distribution_config['Origins']['Items']:
            if origin['Id'] == 'lambda-origin':
                current_domain = origin['DomainName']
                print(f"📝 Current origin domain: {current_domain}")
                
                if current_domain != CORRECT_DOMAIN:
                    origin['DomainName'] = CORRECT_DOMAIN
                    origin['OriginPath'] = '/prod'
                    origin_updated = True
                    print(f"✅ Updated origin domain to: {CORRECT_DOMAIN}")
                else:
                    print("✅ Origin domain already correct")
                break
        
        if origin_updated:
            # Update distribution
            print("📝 Updating CloudFront distribution...")
            cloudfront.update_distribution(
                Id=distribution_id,
                DistributionConfig=distribution_config,
                IfMatch=etag
            )
            print("✅ CloudFront distribution updated")
            
            # Wait for deployment
            print("⏳ Waiting for CloudFront deployment...")
            time.sleep(60)  # Wait 1 minute for initial deployment
            
            # Check deployment status
            while True:
                dist_info = cloudfront.get_distribution(Id=distribution_id)
                status = dist_info['Distribution']['Status']
                print(f"   Status: {status}")
                
                if status == 'Deployed':
                    print("✅ CloudFront deployment complete")
                    break
                elif status == 'InProgress':
                    print("   Still deploying... waiting 30 seconds")
                    time.sleep(30)
                else:
                    print(f"   Unexpected status: {status}")
                    break
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating CloudFront origin: {str(e)}")
        return False

def test_updated_endpoints():
    """Test endpoints after CloudFront update"""
    
    print("\n🧪 Testing Updated Endpoints")
    print("=" * 35)
    
    import requests
    
    base_url = "https://www.ieltsaiprep.com"
    
    # Test API endpoints
    api_endpoints = [
        ("/api/maya/introduction", "Maya API"),
        ("/api/nova-micro/submit", "Nova Micro"),
        ("/api/nova-sonic/submit", "Nova Sonic")
    ]
    
    for endpoint, name in api_endpoints:
        try:
            response = requests.post(f"{base_url}{endpoint}", 
                                   json={}, 
                                   timeout=15)
            
            if response.status_code == 200:
                print(f"✅ {name}: {response.status_code}")
                data = response.json()
                if 'message' in data:
                    message = data['message'][:40] + "..." if len(data['message']) > 40 else data['message']
                    print(f"   Message: {message}")
                if 'band_score' in data:
                    print(f"   Band score: {data['band_score']}")
            else:
                print(f"❌ {name}: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('message', 'Unknown error')}")
                except:
                    print(f"   Raw response: {response.text[:100]}")
                    
        except Exception as e:
            print(f"❌ {name}: Error - {str(e)}")
    
    # Test login endpoint
    print("\n🔐 Testing Login Endpoint")
    try:
        login_data = {
            "email": "test@ieltsaiprep.com",
            "password": "password123"
        }
        response = requests.post(f"{base_url}/api/login", 
                               json=login_data, 
                               timeout=15)
        
        print(f"Login without reCAPTCHA: {response.status_code}")
        if response.status_code == 400:
            data = response.json()
            if "reCAPTCHA" in data.get('message', ''):
                print("✅ reCAPTCHA validation working correctly")
            else:
                print(f"   Message: {data.get('message', 'Unknown')}")
        else:
            print(f"   Unexpected response: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Login test error: {str(e)}")

if __name__ == "__main__":
    print("🚀 IELTS GenAI Prep - CloudFront Origin Update")
    print("=" * 50)
    
    success = update_cloudfront_origin()
    
    if success:
        print("\n✅ CLOUDFRONT ORIGIN UPDATED")
        print("🌐 Custom domain: www.ieltsaiprep.com")
        print("🎯 API Gateway: n0cpf1rmvc")
        print("🔑 Test credentials: test@ieltsaiprep.com / password123")
        
        # Test the updated endpoints
        test_updated_endpoints()
        
        print("\n🎉 www.ieltsaiprep.com API endpoints should now work!")
        print("📱 Ready for mobile app store deployment")
    else:
        print("\n❌ CLOUDFRONT ORIGIN UPDATE FAILED")