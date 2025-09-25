# IELTS GenAI Prep - Production Deployment Package

## Overview
This package contains the production-ready code for the IELTS GenAI Prep platform, ready to deploy to https://github.com/WWPCA/IELTS-Web-Platform.

## What's Changed
- **Removed AWS mock configuration** - Now uses real AWS services
- **Environment-based configuration** - All AWS credentials via environment variables
- **Production-ready handlers** - Real DynamoDB, Nova Sonic, Nova Micro integration
- **Cleaned template structure** - Only includes the 6 active templates from preview session

## Files Included

### Core Application
- `app.py` - Production Lambda handler (no mock services)
- `requirements.txt` - Production dependencies (boto3, urllib3, requests)
- `robots.txt` - SEO-optimized robots.txt

### Active Templates (6 files)
- `working_template_backup_20250714_192410.html` - Main template
- `mobile_registration_flow.html` - Mobile registration
- `test_mobile_home_screen.html` - Mobile home screen
- `test_maya_voice.html` - Maya voice test
- `database_schema_demo.html` - Database schema demo
- `nova_assessment_demo.html` - Nova assessment demo

## Deployment Instructions

### Method 1: Manual GitHub Upload
1. Go to https://github.com/WWPCA/IELTS-Web-Platform
2. Navigate to `IELTS-Web-Platform/lambda_functions/`
3. Replace `main_handler.py` with the production `app.py`
4. Update `requirements.txt` in the root directory
5. Upload templates to `src/pages/` directory

### Method 2: Git Clone and Push
```bash
git clone https://github.com/WWPCA/IELTS-Web-Platform.git
cd IELTS-Web-Platform/IELTS-Web-Platform

# Copy production files
cp /path/to/production_code/app.py lambda_functions/main_handler.py
cp /path/to/production_code/requirements.txt requirements.txt
cp /path/to/production_code/*.html src/pages/

# Commit and push
git add .
git commit -m "Update production code with current preview templates"
git push origin main
```

## Environment Variables Required
Ensure these environment variables are set in production AWS Lambda:

```
AWS_REGION=us-east-1
RECAPTCHA_V2_SECRET_KEY=your_recaptcha_secret
```

## Security Notes
- No hardcoded AWS credentials - uses IAM roles
- No mock services - real AWS production services
- reCAPTCHA v2 integration for security
- Proper error handling and logging

## Testing
After deployment, test these endpoints:
- `/api/health` - Health check
- `/api/nova-sonic-connect` - Nova Sonic connectivity
- `/robots.txt` - SEO optimization

## AWS Services Used
- **DynamoDB**: User data, assessment questions, results
- **Bedrock**: Nova Sonic (voice), Nova Micro (text analysis)
- **Lambda**: Serverless compute
- **API Gateway**: HTTP/WebSocket APIs

## Template Changes
Removed 150+ unused templates, keeping only the 6 active templates from current preview session. This significantly reduces repository size and complexity.

## Support
For deployment issues, refer to the INSTALLATION_GUIDE.md and DEPLOYMENT_GUIDE.md in the production repository.