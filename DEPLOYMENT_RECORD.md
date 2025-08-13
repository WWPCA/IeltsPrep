# Production Deployment Record

## Current Production Status
- **Live URL**: https://www.ieltsaiprep.com
- **AWS Lambda Function**: ielts-genai-prep-api
- **Region**: us-east-1
- **CloudFront Distribution**: E1EPXAU67877FR
- **Last Updated**: 2025-08-11T15:37:09.000+0000

## Recent Deployments

### August 11, 2025 - Content Updates
1. **FAQ Update**: Changed reliability answer to emphasize official IELTS band descriptors
2. **Contact Removal**: Removed Contact Information sections from Privacy Policy and Terms of Service
3. **Pricing Update**: Updated all pricing from $49.99 to $36 for consistency

### Key Production Features
- AI-powered IELTS assessments (Writing and Speaking)
- Mobile-first authentication with QR codes
- GDPR-compliant privacy controls
- Real-time AI feedback using Amazon Nova models
- Cross-platform access (mobile app + web)

### Production Environment
- **Database**: DynamoDB Global Tables
- **Authentication**: Google reCAPTCHA v2
- **AI Services**: Amazon Bedrock (Nova Sonic, Nova Micro)
- **Email**: Amazon SES
- **CDN**: CloudFront with global distribution

### Security Features
- Content safety measures for AI outputs
- Secure password hashing (PBKDF2-HMAC-SHA256)
- GDPR data rights implementation
- CloudFront-based access control
- In-app purchase validation (iOS/Android)

### Assessment Pricing
- Academic Writing: $36 for 4 attempts
- General Writing: $36 for 4 attempts  
- Academic Speaking: $36 for 4 attempts
- General Speaking: $36 for 4 attempts

### Mobile Integration
- Capacitor-based iOS/Android apps
- App Store/Play Store submission ready
- Native purchase processing
- Cross-platform session management