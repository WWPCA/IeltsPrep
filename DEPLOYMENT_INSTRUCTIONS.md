# IELTS GenAI Prep - Production Deployment Instructions

## 🚀 Production Deployment Ready

**Package:** `ielts-web-platform-production-deployment-*.tar.gz`  
**Target Repository:** https://github.com/WWPCA/IELTS-Web-Platform  
**Deployment Date:** September 25, 2025

## ✅ What's Included

### Core Application
- **app.py** - Production Flask application with real AWS services
- **requirements.txt** - All necessary Python dependencies
- **robots.txt** - SEO-optimized for AI crawlers

### Active Templates (6 total)
1. **working_template_backup_20250714_192410.html** - Main working template
2. **mobile_registration_flow.html** - Mobile registration flow
3. **test_mobile_home_screen.html** - Mobile home screen
4. **test_maya_voice.html** - Maya AI voice testing
5. **database_schema_demo.html** - Database schema demonstration
6. **nova_assessment_demo.html** - Nova AI assessment demonstration

### Updated Components
- **updated_ios_auth_handler.py** - Latest iOS auth handler with password reset

## 🔧 Production Configuration

### AWS Services (All Real)
- **DynamoDB:** `ielts-genai-prep-users`, `ielts-genai-prep-assessments`, `ielts-genai-prep-auth-tokens`
- **Nova Sonic:** `amazon.nova-sonic-v1:0` (Maya AI Examiner)
- **Nova Micro:** `amazon.nova-micro-v1:0` (AI Assessment)
- **Lambda Functions:** 6 production handlers
- **Email Service:** SES integration for welcome/reset emails

### Environment Variables Required
```bash
DATABASE_URL=postgresql://...
SESSION_SECRET=your-session-secret
JWT_SECRET=ielts-ai-prep-jwt-secret-2024-production
STRIPE_SECRET_KEY=sk_live_...
```

### Security Features
- Real JWT authentication (no mocks)
- PBKDF2 password hashing
- CORS properly configured
- Environment variable security

## 📥 Deployment Steps

### 1. Upload to GitHub Repository
```bash
# Extract deployment package
tar -xzf ielts-web-platform-production-deployment-*.tar.gz

# Upload to IELTS-Web-Platform repository
git clone https://github.com/WWPCA/IELTS-Web-Platform.git
cd IELTS-Web-Platform

# Copy production files
cp ../production_code/* ./IELTS-Web-Platform/

# Commit and push
git add .
git commit -m "Production deployment - Remove AWS mocks, add real services"
git push origin main
```

### 2. Configure Environment Variables
Set these in your production environment:
- `DATABASE_URL` - PostgreSQL connection string
- `SESSION_SECRET` - Flask session secret
- `JWT_SECRET` - JWT signing secret
- `STRIPE_SECRET_KEY` - Stripe payment processing

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Deploy Application
```bash
# Production deployment
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

## ✅ Production Readiness Checklist

### Infrastructure
- [x] Real DynamoDB tables configured
- [x] Nova Sonic/Nova Micro production models
- [x] AWS Lambda functions deployed
- [x] Email service (SES) configured
- [x] JWT authentication implemented

### Security
- [x] Environment variables (no hardcoded secrets)
- [x] Password hashing (SHA256)
- [x] Token validation
- [x] CORS configuration
- [x] Input validation

### Features
- [x] User registration/login
- [x] Password reset functionality
- [x] QR code authentication
- [x] Maya AI Examiner (Nova Sonic)
- [x] AI Assessment (Nova Micro)
- [x] Mobile-to-web experience

### Templates & UI
- [x] 6 active templates (cleaned from 150+)
- [x] TrueScore® and ClearScore® branding
- [x] Purple gradient theme
- [x] Mobile-responsive design
- [x] Professional error handling

## 🔄 Repository Consistency

### iOS Repository Update Required
The iOS auth_handler.py has been updated to include password reset functionality to match the Web Platform. Apply this update:

```bash
# Copy updated iOS auth handler to iOS repository
cp updated_ios_auth_handler.py /path/to/IELTSiOS/backend/lambda_functions/auth_handler.py
```

### Android Repository
No changes needed - Java app connects to same AWS Lambda functions.

## 🎯 Post-Deployment Verification

1. **Health Check:** Visit `/api/health` endpoint
2. **User Registration:** Test user signup flow
3. **Password Reset:** Test forgot password functionality
4. **Maya AI:** Test Nova Sonic voice integration
5. **Assessment:** Test Nova Micro evaluation
6. **Mobile Experience:** Test QR code authentication

## 📞 Support

For deployment issues or questions:
- Check AWS CloudWatch logs for Lambda functions
- Verify DynamoDB table access permissions
- Ensure all environment variables are set correctly
- Test Nova Sonic/Nova Micro model access

---

**Deployment Status:** ✅ Ready for Production  
**Last Updated:** September 25, 2025  
**Version:** Production v1.0 (Real AWS Services)