# Mobile App Store Deployment Guide
Generated: 2025-07-17 18:56:12

## Pre-Deployment Checklist

### 1. Production Website Verification
- ✅ Deploy comprehensive_production_20250717_185438.zip to AWS Lambda
- ✅ Test all endpoints at https://www.ieltsaiprep.com
- ✅ Verify login with test credentials: prodtest@ieltsgenaiprep.com / test123
- ✅ Confirm all 4 assessment types accessible
- ✅ Verify $36.49 USD pricing consistency

### 2. Mobile App Configuration
- ✅ Update capacitor.config.json with production server URL
- ✅ Configure in-app purchase product IDs
- ✅ Set up Apple Developer Account and Google Play Console
- ✅ Generate app signing certificates

## iOS App Store Deployment

### Step 1: Xcode Configuration
```bash
# Install dependencies
npm install
npx cap add ios
npx cap sync ios

# Open in Xcode
npx cap open ios
```

### Step 2: App Store Connect Setup
1. Create app in App Store Connect
2. Set Bundle ID: com.ieltsaiprep.app
3. Configure in-app purchases:
   - academic_writing_assessment: $36.49 USD
   - general_writing_assessment: $36.49 USD
   - academic_speaking_assessment: $36.49 USD
   - general_speaking_assessment: $36.49 USD

### Step 3: Review Information
- Demo Account: prodtest@ieltsgenaiprep.com / test123
- Review Notes: "App requires in-app purchases for assessments. Demo account has pre-purchased access."

## Android Play Store Deployment

### Step 1: Android Build
```bash
# Build Android app
npx cap add android
npx cap sync android
npx cap open android
```

### Step 2: Google Play Console Setup
1. Create app in Google Play Console
2. Set Package Name: com.ieltsaiprep.app
3. Complete Data Safety form with provided responses
4. Configure in-app products with $36.49 USD pricing

### Step 3: Release Management
- Use internal testing track first
- Provide test account: prodtest@ieltsgenaiprep.com / test123
- Submit for review after successful testing

## Testing Protocol

### Production Website Testing
1. Navigate to https://www.ieltsaiprep.com
2. Test all pages: home, login, privacy-policy, terms-of-service
3. Login with test credentials
4. Verify dashboard shows all 4 assessment types
5. Test each assessment page loads correctly

### Mobile App Testing
1. Install app on test device
2. Complete in-app purchase flow
3. Verify cross-platform sync with website
4. Test assessment functionality
5. Verify receipt validation

## Security Considerations

### reCAPTCHA Configuration
- Site Key: 6LdD2VUrAAAAABG_Tt5fFYmWkRB4YFVHPdjggYzQ
- Secret Key: Configure in Lambda environment variables

### CloudFront Security
- Header: CF-Secret-3140348d
- Direct API Gateway access blocked

### Database Security
- PBKDF2 password hashing
- Session-based authentication
- GDPR compliance implemented

## Support Documentation

### Privacy Policy
- URL: https://www.ieltsaiprep.com/privacy-policy
- GDPR compliant with simplified data usage disclosure
- Voice recording policy clearly stated

### Terms of Service  
- URL: https://www.ieltsaiprep.com/terms-of-service
- Non-refundable purchase policy
- AI content usage guidelines

## Post-Deployment Monitoring

### Key Metrics to Track
- App store approval status
- User registration and purchase rates
- Assessment completion rates
- Cross-platform usage patterns

### Support Channels
- Website: https://www.ieltsaiprep.com
- Technical issues: Monitor CloudWatch logs
- User support: Email integration via AWS SES

## Emergency Procedures

### If App Rejected
1. Review rejection reason
2. Update app according to guidelines
3. Resubmit with detailed response
4. Use test account for reviewer demonstration

### If Website Issues
1. Check CloudWatch logs for errors
2. Verify CloudFront distribution status
3. Test Lambda function directly
4. Monitor DynamoDB table access

## Success Criteria

### App Store Approval
- Both iOS and Android apps approved
- In-app purchases configured correctly
- Cross-platform functionality verified

### Production Readiness
- All endpoints returning HTTP 200
- User authentication working
- Assessment delivery functional
- Payment processing operational

## Contact Information

For deployment support:
- Production website: https://www.ieltsaiprep.com
- Test credentials: prodtest@ieltsgenaiprep.com / test123
- AWS Lambda function: ielts-genai-prep-api
- CloudFront distribution: E1EPXAU67877FR
