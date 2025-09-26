# IELTS GenAI Prep - Production Deployment Guide

## Quick Deploy
```bash
python3 deploy_production_fixed.py
```

## What This Deploys

### Complete Lambda Function
The deployment script creates a complete AWS Lambda function with:
- All HTML templates embedded
- Complete routing system
- API endpoints for Nova Sonic and assessment submission
- reCAPTCHA integration
- CloudFront security validation

### Templates Included
1. **Home Page** (`working_template.html`)
2. **Login Page** with GDPR consent checkboxes
3. **Privacy Policy** with data rights
4. **Terms of Service** with no-refund policy
5. **Dashboard** with 4 assessment cards
6. **My Profile** with GDPR data management
7. **Assessment Pages** (4 types) with Maya AI integration
8. **Robots.txt** optimized for AI search

### API Endpoints
- `/api/nova-sonic-connect` - Test Maya voice connection
- `/api/nova-sonic-stream` - Handle Maya conversation
- `/api/submit-assessment` - Process assessment submissions

## Environment Variables Required
```
RECAPTCHA_V2_SITE_KEY=your_site_key
RECAPTCHA_V2_SECRET_KEY=your_secret_key
```

## CloudFront Configuration
The function expects CloudFront header: `cf-secret: CF-Secret-3140348d`

## Test Credentials
- Email: test@ieltsgenaiprep.com
- Password: test123

## Production URLs
- Website: https://www.ieltsaiprep.com
- Function: ielts-genai-prep-api (us-east-1)
- CloudFront: E1EPXAU67877FR

## Features Confirmed Working
✅ All 4 assessment pages (HTTP 200)
✅ Maya AI examiner with Nova Sonic voice
✅ Real-time word counting and timers
✅ GDPR compliance checkboxes
✅ AI search optimization
✅ Session-based security

## Troubleshooting
- If login page shows 502: Check Lambda function logs
- If assessments don't load: Verify CloudFront headers
- If reCAPTCHA fails: Check environment variables

---
*Last successful deployment: July 14, 2025*