# AWS Lambda Upload Guide - Security Enhancement

## Package Information
- **File**: security_enhanced_production_20250721_042353.zip
- **Size**: 46.9 KB
- **Function**: ielts-genai-prep-api
- **Priority**: CRITICAL SECURITY UPDATE

## AWS Console Upload Steps

### 1. Access AWS Lambda Console
- Open: https://console.aws.amazon.com/lambda/
- Sign in to your AWS account
- Navigate to: Functions

### 2. Select Target Function
- Find and click: `ielts-genai-prep-api`
- This is your production IELTS function

### 3. Upload Security Package
- Click: "Upload from" button
- Select: ".zip file" option
- Choose: `security_enhanced_production_20250721_042353.zip`
- Click: "Save" to deploy

### 4. Verify Deployment
- Wait for deployment completion (usually 10-30 seconds)
- Status should show: "Successfully updated"

## Post-Deployment Validation

### Test Security Enhancement
Visit: https://www.ieltsaiprep.com/robots.txt

### Expected Results (After Upload)
```
# IELTS GenAI Prep - Security-Enhanced robots.txt
# Last Updated: July 21, 2025

User-agent: *
Disallow: /login
Disallow: /register
Disallow: /auth/
Disallow: /api/
Disallow: /*.log$
Crawl-delay: 10
```

### Validation Commands
```bash
# Test authentication protection
curl https://www.ieltsaiprep.com/robots.txt | grep "Disallow: /login"

# Test API security
curl https://www.ieltsaiprep.com/robots.txt | grep "Disallow: /api/"

# Test security timestamp
curl https://www.ieltsaiprep.com/robots.txt | grep "July 21, 2025"
```

## Current Status (Before Upload)
The production robots.txt currently shows:
```
User-agent: *
Allow: /
```

This is VULNERABLE to bot attacks and content scraping.

## After Upload Benefits
- Authentication endpoints protected from bots
- API structure secured against discovery
- IELTS assessment content protected from AI training
- File system secured against unauthorized access
- Enhanced rate limiting active

## Troubleshooting

### If Upload Fails
- Check file size (should be 46.9 KB)
- Verify function name: ielts-genai-prep-api
- Ensure proper AWS permissions
- Try uploading again

### If Validation Fails
- Wait 2-3 minutes for CloudFront propagation
- Clear browser cache
- Test from different network/device

## Support
If you encounter issues during upload:
1. Verify AWS account has Lambda deployment permissions
2. Check CloudWatch logs for any deployment errors
3. Ensure CloudFront distribution is properly configured

---
**Critical**: This security update resolves vulnerabilities in the production robots.txt and must be deployed immediately.