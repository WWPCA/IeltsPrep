#!/usr/bin/env python3
"""
Fix reCAPTCHA site key in Lambda function
Replace hardcoded key with environment variable
"""

import re
import zipfile
import os

def fix_recaptcha_in_lambda():
    """Fix hardcoded reCAPTCHA site key in Lambda function"""
    
    # Read the current Lambda code
    with open('production-lambda-code.py', 'r', encoding='utf-8') as f:
        lambda_code = f.read()
    
    # Find the hardcoded reCAPTCHA site key
    hardcoded_pattern = r'data-sitekey="[^"]*"'
    
    # Replace with environment variable lookup
    fixed_code = re.sub(
        hardcoded_pattern,
        'data-sitekey="' + '${os.environ.get("RECAPTCHA_V2_SITE_KEY", "")}' + '"',
        lambda_code
    )
    
    # Also need to add the environment variable lookup in the function
    # Find the handle_login_page function and add environment variable
    if 'os.environ.get("RECAPTCHA_V2_SITE_KEY"' not in fixed_code:
        # Add the proper template string formatting
        fixed_code = fixed_code.replace(
            'data-sitekey="${os.environ.get("RECAPTCHA_V2_SITE_KEY", "")}',
            f'data-sitekey="{os.environ.get("RECAPTCHA_V2_SITE_KEY", "")}"'
        )
        
        # Actually, we need to fix this properly by using f-string
        # Find the template assignment and modify it
        if 'template = """' in fixed_code:
            # Replace the template definition to use f-string
            fixed_code = fixed_code.replace(
                'template = """',
                f'recaptcha_site_key = os.environ.get("RECAPTCHA_V2_SITE_KEY", "")\n    template = f"""'
            )
            
            # Fix the data-sitekey to use the variable
            fixed_code = fixed_code.replace(
                'data-sitekey="${os.environ.get("RECAPTCHA_V2_SITE_KEY", "")}',
                'data-sitekey="{recaptcha_site_key}'
            )
    
    # Write the fixed code
    with open('production-lambda-code-fixed.py', 'w', encoding='utf-8') as f:
        f.write(fixed_code)
    
    print("✅ Fixed reCAPTCHA site key in Lambda code")
    print("📁 Created: production-lambda-code-fixed.py")
    
    # Create new deployment package
    with zipfile.ZipFile('production-recaptcha-fixed.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write('production-lambda-code-fixed.py', 'lambda_function.py')
    
    print("📦 Created: production-recaptcha-fixed.zip")
    print()
    print("🚀 Deploy with:")
    print("aws lambda update-function-code \\")
    print("    --function-name ielts-genai-prep-api \\")
    print("    --zip-file fileb://production-recaptcha-fixed.zip")
    
    return True

if __name__ == "__main__":
    fix_recaptcha_in_lambda()