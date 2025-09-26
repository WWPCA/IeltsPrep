#!/usr/bin/env python3
"""
Manual production update - Extract the exact Lambda code for deployment
"""

import zipfile
import os

def extract_lambda_code():
    """Extract the Lambda function code from the deployment package"""
    
    try:
        with zipfile.ZipFile('production-all-fixes.zip', 'r') as zip_ref:
            # Extract lambda_function.py
            zip_ref.extract('lambda_function.py', '.')
            
        # Read the extracted code
        with open('lambda_function.py', 'r', encoding='utf-8') as f:
            lambda_code = f.read()
            
        print("=== PRODUCTION LAMBDA CODE EXTRACTED ===")
        print()
        print("The following code needs to be deployed to AWS Lambda:")
        print(f"Code length: {len(lambda_code)} characters")
        print()
        print("First 500 characters:")
        print("-" * 50)
        print(lambda_code[:500])
        print("-" * 50)
        print()
        
        # Also create a readable version
        with open('production-lambda-code.py', 'w', encoding='utf-8') as f:
            f.write(lambda_code)
            
        print("✅ Code extracted to: production-lambda-code.py")
        print()
        print("🚀 DEPLOYMENT OPTIONS:")
        print()
        print("1. AWS CLI (if available):")
        print("   aws lambda update-function-code \\")
        print("       --function-name ielts-genai-prep-prod \\")
        print("       --zip-file fileb://production-all-fixes.zip")
        print()
        print("2. AWS Console:")
        print("   - Go to Lambda console")
        print("   - Find function: ielts-genai-prep-prod")
        print("   - Upload production-all-fixes.zip")
        print()
        print("3. Manual code replacement:")
        print("   - Copy content from production-lambda-code.py")
        print("   - Replace entire Lambda function code")
        print()
        print("📋 ROUTES THAT WILL BE FIXED:")
        print("   ✓ /login")
        print("   ✓ /privacy-policy")
        print("   ✓ /terms-of-service")
        print("   ✓ /dashboard")
        print("   ✓ Mobile alignment fixes")
        
        # Clean up
        os.remove('lambda_function.py')
        
        return True
        
    except Exception as e:
        print(f"Error extracting code: {e}")
        return False

def main():
    """Main function"""
    success = extract_lambda_code()
    
    if success:
        print()
        print("🎯 IMMEDIATE ACTION NEEDED:")
        print("   The 404 errors will persist until the AWS Lambda function")
        print("   is updated with the code from production-all-fixes.zip")
        print()
        print("📁 Files ready for deployment:")
        print("   - production-all-fixes.zip (deployment package)")
        print("   - production-lambda-code.py (readable code)")
        print("   - deploy-to-production-now.md (deployment guide)")
    else:
        print("❌ Failed to extract deployment code")

if __name__ == "__main__":
    main()