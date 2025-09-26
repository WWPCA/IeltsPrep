# Quick Test Guide - IELTS GenAI Prep

## Live Website
**URL**: https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod

Open this URL in any browser to see the live IELTS GenAI Prep website with:
- Professional homepage design
- Feature descriptions
- Pricing information
- App Store download sections
- Live API status indicator

## API Testing Commands

### Health Check
```bash
curl https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod/health
```

### Register New User
```bash
curl -X POST https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "your-test@email.com", "password": "YourPassword123", "name": "Test User"}'
```

### Login User
```bash
curl -X POST https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "your-test@email.com", "password": "YourPassword123"}'
```

### Test Assessment Access (use session_id from login response)
```bash
curl -X GET https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod/assessment/academic-writing \
  -H "Authorization: Bearer YOUR_SESSION_ID_HERE"
```

## App Store Configuration

Mobile apps should use this production endpoint:
```
https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod
```

All authentication, assessment access, and purchase verification endpoints are ready for testing.

## Ready for Deployment

The complete IELTS GenAI Prep platform is now live on AWS and ready for App Store submission and testing.