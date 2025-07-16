#!/usr/bin/env python3
"""
Deploy Enhanced Robots.txt to Production Lambda
Direct deployment to ielts-genai-prep-api function
"""

import boto3
import json
import zipfile
import io
import os
from datetime import datetime

def create_production_lambda_update():
    """Create and deploy enhanced robots.txt to production Lambda"""
    
    # Enhanced robots.txt content for production
    enhanced_robots_content = '''User-agent: *
Allow: /

# AI Search Engine Bots - Enhanced SEO Optimization
User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: Bingbot
Allow: /

User-agent: BingPreview
Allow: /

User-agent: SlackBot
Allow: /

User-agent: facebookexternalhit
Allow: /

User-agent: Twitterbot
Allow: /

User-agent: LinkedInBot
Allow: /

User-agent: WhatsApp
Allow: /

User-agent: Applebot
Allow: /

User-agent: DuckDuckBot
Allow: /

User-agent: YandexBot
Allow: /

User-agent: BaiduSpider
Allow: /

User-agent: NaverBot
Allow: /

# AI Model Training Bots
User-agent: ChatGPT-User
Allow: /

User-agent: Claude-Web
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: YouBot
Allow: /

User-agent: Anthropic-AI
Allow: /

User-agent: OpenAI-SearchBot
Allow: /

User-agent: Meta-ExternalAgent
Allow: /

User-agent: Gemini-Pro
Allow: /

Sitemap: https://www.ieltsaiprep.com/sitemap.xml'''

    # Lambda function code with enhanced robots.txt
    lambda_code = f'''
def handle_robots_txt() -> Dict[str, Any]:
    """Handle robots.txt endpoint with enhanced AI SEO optimization"""
    robots_content = """{enhanced_robots_content}"""
    
    return {{
        'statusCode': 200,
        'headers': {{
            'Content-Type': 'text/plain',
            'Cache-Control': 'public, max-age=86400'
        }},
        'body': robots_content
    }}
'''
    
    try:
        # Initialize AWS Lambda client
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        # Function name from previous discovery
        function_name = 'ielts-genai-prep-api'
        
        print(f"🚀 Deploying enhanced robots.txt to {function_name}...")
        
        # Get current function configuration
        response = lambda_client.get_function(FunctionName=function_name)
        current_config = response['Configuration']
        
        print(f"📋 Current function size: {current_config.get('CodeSize', 'Unknown')} bytes")
        
        # Get current function code
        code_response = lambda_client.get_function(FunctionName=function_name)
        code_location = code_response['Code']['Location']
        
        # Download current code
        import urllib.request
        with urllib.request.urlopen(code_location) as response:
            current_code = response.read()
        
        print(f"📥 Downloaded current function code ({len(current_code)} bytes)")
        
        # Create modified code with enhanced robots.txt
        # This is a simplified approach - we'll create a patch
        with open('enhanced_robots_patch.py', 'w') as f:
            f.write(f'''
# Enhanced Robots.txt Handler - Production Deployment
# Deploy this to replace the existing handle_robots_txt function

def handle_robots_txt() -> Dict[str, Any]:
    """Handle robots.txt endpoint with enhanced AI SEO optimization"""
    robots_content = """{enhanced_robots_content}"""
    
    return {{
        'statusCode': 200,
        'headers': {{
            'Content-Type': 'text/plain',
            'Cache-Control': 'public, max-age=86400'
        }},
        'body': robots_content
    }}

# Deployment timestamp: {datetime.utcnow().isoformat()}
''')
        
        print("✅ Enhanced robots.txt handler code generated")
        print("📄 Saved as: enhanced_robots_patch.py")
        print("🔄 Ready for production deployment")
        
        # Create deployment package
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr('enhanced_robots_patch.py', open('enhanced_robots_patch.py', 'r').read())
            zip_file.writestr('deployment_info.json', json.dumps({
                'timestamp': datetime.utcnow().isoformat(),
                'function_name': function_name,
                'enhancement': 'Enhanced AI SEO robots.txt with 20+ bot permissions',
                'bots_added': [
                    'Bingbot', 'BingPreview', 'SlackBot', 'facebookexternalhit', 
                    'Twitterbot', 'LinkedInBot', 'WhatsApp', 'Applebot', 
                    'DuckDuckBot', 'YandexBot', 'BaiduSpider', 'NaverBot',
                    'ChatGPT-User', 'Claude-Web', 'PerplexityBot', 'YouBot',
                    'Anthropic-AI', 'OpenAI-SearchBot', 'Meta-ExternalAgent', 'Gemini-Pro'
                ]
            }, indent=2))
        
        zip_buffer.seek(0)
        
        # Save deployment package
        with open('enhanced_robots_deployment.zip', 'wb') as f:
            f.write(zip_buffer.getvalue())
        
        print("📦 Deployment package created: enhanced_robots_deployment.zip")
        
        # Note: Direct Lambda update would require the full function code
        # For now, create the patch file for manual deployment
        
        print("""
🎯 PRODUCTION DEPLOYMENT READY

The enhanced robots.txt handler is ready for production deployment.

📋 Deployment Summary:
- Function: ielts-genai-prep-api
- Enhancement: 20+ AI bot permissions added
- File: enhanced_robots_patch.py
- Package: enhanced_robots_deployment.zip

🚀 Next Steps:
1. Apply the enhanced_robots_patch.py to the production Lambda function
2. Test: curl https://www.ieltsaiprep.com/robots.txt
3. Verify all 20+ bot permissions are listed

Expected Result: www.ieltsaiprep.com/robots.txt will show comprehensive AI SEO optimization
""")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during deployment preparation: {str(e)}")
        return False

if __name__ == "__main__":
    create_production_lambda_update()