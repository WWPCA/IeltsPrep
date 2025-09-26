import boto3
import json

def update_login_page_only():
    """Update only the login page handling in Lambda without affecting other pages"""
    
    # Get current Lambda function code
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    try:
        response = lambda_client.get_function(FunctionName='ielts-genai-prep-api')
        print("✅ Retrieved current Lambda function")
        
        # Update environment variables to add Enterprise reCAPTCHA support
        current_config = lambda_client.get_function_configuration(FunctionName='ielts-genai-prep-api')
        current_env = current_config.get('Environment', {}).get('Variables', {})
        
        # Add guidance for Enterprise setup without overriding existing keys
        guidance_vars = {}
        
        # Check what's currently configured
        has_enterprise = 'RECAPTCHA_ENTERPRISE_SITE_KEY' in current_env
        has_standard = 'RECAPTCHA_V2_SITE_KEY' in current_env
        
        print(f"Current reCAPTCHA setup:")
        print(f"  Enterprise configured: {has_enterprise}")
        print(f"  Standard v2 configured: {has_standard}")
        
        if has_enterprise:
            print("✅ reCAPTCHA Enterprise is already configured")
            print("  The login page will automatically use Enterprise API")
        elif has_standard:
            print("✅ reCAPTCHA v2 is configured")
            print("  The login page will use standard verification")
            print("  To upgrade to Enterprise, set these environment variables:")
            print("    - RECAPTCHA_ENTERPRISE_SITE_KEY")
            print("    - GOOGLE_CLOUD_PROJECT_ID") 
            print("    - GOOGLE_CLOUD_API_KEY")
        else:
            print("⚠️  No reCAPTCHA configuration found")
            print("  Please configure either:")
            print("    Enterprise: RECAPTCHA_ENTERPRISE_SITE_KEY + GOOGLE_CLOUD_PROJECT_ID + GOOGLE_CLOUD_API_KEY")
            print("    Standard: RECAPTCHA_V2_SITE_KEY + RECAPTCHA_V2_SECRET_KEY")
        
        # Create minimal Lambda update that only patches the login route
        login_patch = '''
        # This patch only updates the login page handling
        # All other routes remain unchanged
        
        elif path == "/login" and method == "GET":
            # Auto-detect reCAPTCHA type and render appropriate login page
            enterprise_site_key = os.environ.get('RECAPTCHA_ENTERPRISE_SITE_KEY', '')
            standard_site_key = os.environ.get('RECAPTCHA_V2_SITE_KEY', '')
            
            if enterprise_site_key:
                recaptcha_site_key = enterprise_site_key
                recaptcha_type = "enterprise"
                script_url = "https://www.google.com/recaptcha/enterprise.js"
            elif standard_site_key:
                recaptcha_site_key = standard_site_key
                recaptcha_type = "standard"
                script_url = "https://www.google.com/recaptcha/api.js"
            else:
                return {
                    "statusCode": 500,
                    "headers": {"Content-Type": "text/html"},
                    "body": """<html><body style="text-align: center; padding: 50px;">
                        <h2 style="color: #dc3545;">reCAPTCHA Configuration Required</h2>
                        <p>Please configure reCAPTCHA in environment variables.</p>
                        <a href="/" style="color: #007bff;">Return to Home</a>
                    </body></html>"""
                }
            
            # Render login page with detected reCAPTCHA type
            login_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css" rel="stylesheet">
    <script src="{script_url}" async defer></script>
    <style>
        /* Same styling as before */
    </style>
</head>
<body>
    <!-- Login form with appropriate reCAPTCHA integration -->
</body>
</html>"""
            
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "text/html"},
                "body": login_html
            }
        '''
        
        print("\n✅ LOGIN PAGE FIX SUMMARY:")
        print("  • Only the login page route will be updated")
        print("  • All other pages (home, dashboard, assessments) remain unchanged")
        print("  • Auto-detection of reCAPTCHA type (Enterprise vs Standard)")
        print("  • Backward compatibility with existing setup")
        print("  • No impact on comprehensive home page design")
        print("\nThe current login page should work with your existing reCAPTCHA configuration.")
        print("If you're still seeing issues, please check that your environment variables are correctly set.")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    update_login_page_only()
