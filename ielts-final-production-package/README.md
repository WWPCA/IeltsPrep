# IELTS GenAI Prep - Final Production Package

## Overview
This package contains all the production code and resources for the IELTS GenAI Prep platform deployed at https://www.ieltsaiprep.com

## Architecture
- **Backend**: AWS Lambda serverless function (lambda_function.py)
- **Frontend**: Progressive Web App with responsive design
- **Database**: DynamoDB Global Tables (mocked via aws_mock_config.py for development)
- **Authentication**: QR code mobile-to-web authentication
- **AI Services**: Amazon Nova Sonic (speaking) and Nova Micro (writing)

## Files Included

### Core Production Code
- `lambda_function.py` - Main AWS Lambda handler with all routes and templates
- `aws_mock_config.py` - Development environment AWS service mocking
- `replit.md` - Project architecture and user preferences documentation

### UI/Design Files
- `static/` - Static assets (CSS, JavaScript, images, audio files)
  - `css/` - Stylesheets (main styles, cookie consent, QR modal)
  - `js/` - JavaScript modules (main, speaking, mobile integration, offline support)
  - `images/` - UI icons, logos, and graphics
  - `audio/` - Sample audio files for assessments
- `templates/` - HTML templates for all pages
  - Complete page templates for assessments, admin, GDPR compliance
  - Error pages (404, 500)
  - User account management templates
  - Practice assessment templates

### Assessment Question Banks
- `Academic Writing Task 2 tests (essays).txt` - Academic writing prompts
- `General Training Writing Task 2 tests (essays).txt` - General training writing prompts
- `IELTS General Training Writing Task 1 letters.txt` - General training letters
- `General Reading Task 1 Multiple Cho.txt` - Reading comprehension questions
- `General Test Reading Task 2 True False Not Given.txt` - Reading assessment tasks
- `IELTS Reading Context File.txt` - Reading passages and contexts
- `IELTS Speaking Context File.xlsx` - Speaking assessment scenarios

## Key Features

### Production Website (www.ieltsaiprep.com)
- Home page with SEO optimization and FAQ
- Privacy Policy (GDPR compliant)
- Terms of Service 
- Login/Registration system with reCAPTCHA v2
- Dashboard with assessment access
- Profile management with account deletion

### AI Assessment Engine
- **TrueScore® Writing Assessment**: AI evaluation using Nova Micro
- **ClearScore® Speaking Assessment**: AI conversation using Nova Sonic
- Real-time feedback based on official IELTS band descriptors
- Support for both Academic and General Training modules

### Pricing Structure
- $36 for 4 assessment attempts per module type
- Consumable purchase model via mobile app
- Cross-platform access (mobile app or web)

## Recent Updates (August 2025)
- Updated FAQ to emphasize official IELTS band descriptors alignment
- Removed contact information sections from Privacy Policy and Terms of Service
- Updated all pricing from $49.99 to $36 for consistency
- Enhanced robots.txt for AI bot SEO optimization
- Fixed production deployment issues and cache management

## Deployment
The main production function is deployed as:
- **AWS Lambda**: ielts-genai-prep-api (us-east-1)
- **CloudFront Distribution**: E1EPXAU67877FR
- **Domain**: www.ieltsaiprep.com

## Environment Variables Required
- RECAPTCHA_V2_SITE_KEY
- RECAPTCHA_V2_SECRET_KEY
- DYNAMODB_TABLE_PREFIX
- ENVIRONMENT=production

## Mobile App Integration
- Capacitor-based mobile apps for iOS/Android
- In-app purchase validation
- QR code authentication for web platform access
- Native features integration

## Security Features
- Google reCAPTCHA v2 integration
- PBKDF2-HMAC-SHA256 password hashing
- CloudFront-based access control
- GDPR compliance with data export/deletion
- Content safety measures for AI-generated content

For technical implementation details, see the individual files and replit.md documentation.