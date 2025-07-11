# CloudFront Cache Behavior Manual Fix Guide

## Issue Summary
The `/assessment/*` cache behavior in CloudFront distribution E1EPXAU67877FR has legacy TTL settings that are incompatible with modern cache policies, causing 403 Forbidden errors for assessment pages.

## Root Cause
- `/assessment/*` behavior has deprecated ForwardedValues and TTL configurations
- Modern CloudFront requires cache policies instead of legacy settings
- Automated API updates blocked by CallerReference restrictions

## Working Reference Configuration
The `/api/*` behavior works correctly with these settings:
- **Cache Policy**: CachingDisabled (4135ea2d-6df8-44a3-9df3-4b5a84be39ad)
- **Origin Request Policy**: CORS-S3Origin (88a5eaf4-2fd4-4709-b370-b4c650ea3fcf)
- **Viewer Protocol Policy**: redirect-to-https
- **Allowed HTTP Methods**: GET, HEAD, OPTIONS, PUT, POST, PATCH, DELETE

## Manual Fix Steps

### 1. Access AWS CloudFront Console
- Navigate to CloudFront in AWS Console
- Select distribution E1EPXAU67877FR
- Go to "Behaviors" tab

### 2. Edit /assessment/* Behavior
- Find the `/assessment/*` path pattern behavior
- Click "Edit"

### 3. Apply Working Configuration
Copy these exact settings from the working `/api/*` behavior:

**Cache Policy and Origin Request Policy:**
- Cache Policy: CachingDisabled (4135ea2d-6df8-44a3-9df3-4b5a84be39ad)
- Origin Request Policy: CORS-S3Origin (88a5eaf4-2fd4-4709-b370-b4c650ea3fcf)

**Viewer Settings:**
- Viewer Protocol Policy: Redirect HTTP to HTTPS
- Allowed HTTP Methods: GET, HEAD, OPTIONS, PUT, POST, PATCH, DELETE
- Cached HTTP Methods: GET, HEAD, OPTIONS

**Remove Legacy Settings:**
- Remove any TTL values (Default, Maximum, Minimum)
- Remove any ForwardedValues configurations
- Ensure cache policies are used instead

### 4. Save and Deploy
- Click "Save Changes"
- Wait 10-15 minutes for global propagation

## Verification
After propagation, test these URLs:
- https://www.ieltsaiprep.com/assessment/academic-writing
- https://www.ieltsaiprep.com/assessment/general-writing
- https://www.ieltsaiprep.com/assessment/academic-speaking
- https://www.ieltsaiprep.com/assessment/general-speaking

All should return HTTP 200 with proper assessment pages.

## Current Status
- Domain transfer: ✅ Complete
- Main pages: ✅ Working (home, login, dashboard, privacy, terms)
- API endpoints: ✅ Working (/api/login, /api/health)
- Assessment pages: ❌ Blocked by cache behavior (fixable with manual steps above)
- Direct API Gateway blocking: ✅ Working (returns 403 as expected)

## July 8, 2025 Functionality Preserved
All core assessment features remain intact:
- DynamoDB question migration (16 questions)
- Maya AI examiner integration
- Nova Micro/Sonic APIs
- Timer components and word counting
- Session management and authentication
- Assessment attempt tracking
- Real-time features and progress tracking