# AWS Lambda Production Deployment - Robots.txt Fix

## Deployment Package Ready
✅ `production_robots_fix_lambda.zip` - Contains fixed Lambda function

## AWS CLI Deployment Commands

### Option 1: AWS CLI Deployment
```bash
# Deploy to your production Lambda function
aws lambda update-function-code \
    --function-name ielts-genai-prep-production \
    --zip-file fileb://production_robots_fix_lambda.zip \
    --region us-east-1

# Verify deployment
aws lambda get-function \
    --function-name ielts-genai-prep-production \
    --region us-east-1
```

### Option 2: AWS Console Deployment
1. Download `production_robots_fix_lambda.zip` from this project
2. Go to AWS Lambda Console
3. Navigate to your production function (likely `ielts-genai-prep-production`)
4. Click "Upload from" → ".zip file"
5. Upload `production_robots_fix_lambda.zip`
6. Click "Save"

## What's Fixed
- **File:** `lambda_function.py` line 1751-1782
- **Function:** `handle_robots_txt()` with error handling
- **Endpoint:** `/robots.txt` will return proper content instead of 500 error
- **Impact:** Zero impact on other functionality

## Test After Deployment
```bash
curl -I https://www.ieltsaiprep.com/robots.txt
# Should return: HTTP/1.1 200 OK
```

## Expected Response
```
User-agent: *
Allow: /

User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Google-Extended
Allow: /

Sitemap: https://www.ieltsaiprep.com/sitemap.xml
```

Deploy immediately to restore SEO crawler access.