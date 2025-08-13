# IELTS AI Prep - Web Platform

[![Production Status](https://img.shields.io/badge/status-production-green.svg)](https://www.ieltsaiprep.com)
[![AI Technology](https://img.shields.io/badge/AI-AWS%20Nova%20Sonic-blue.svg)](https://aws.amazon.com/bedrock)
[![GDPR Compliant](https://img.shields.io/badge/GDPR-compliant-success.svg)](docs/guides/GDPR_COMPLIANCE.md)

An advanced AI-powered IELTS test preparation platform delivering intelligent, secure, and adaptive language assessment experiences through cutting-edge cloud-native technologies and mobile-first design.

## 🎯 Overview

IELTS AI Prep provides comprehensive IELTS test preparation using AI technology with official band descriptors alignment. The platform features Maya, an AI speaking examiner powered by AWS Nova Sonic, and TrueScore® writing assessments using Nova Micro.

### Live Platform
**Production Website:** [www.ieltsaiprep.com](https://www.ieltsaiprep.com)

## ✨ Key Features

### 🤖 AI-Powered Assessments
- **TrueScore® Writing Assessment** - AI evaluation using AWS Nova Micro
- **ClearScore® Speaking Assessment** - Real-time conversation with Maya AI examiner
- **Official IELTS Criteria** - Aligned with authentic band descriptors
- **4 Assessment Types** - Academic & General Training for Speaking & Writing

### 🔐 Security & Compliance
- **Google reCAPTCHA v2** integration for bot protection
- **GDPR Compliant** privacy policy with AI disclosure
- **bcrypt Password Hashing** for secure authentication
- **Content Safety Monitoring** with user reporting system

### 📱 Cross-Platform Access
- **Mobile-First Registration** via iOS/Android apps
- **QR Authentication** for seamless mobile-to-web access
- **App Store Integration** with purchase validation
- **Progressive Web App** design for responsive experience

### 🌐 SEO & Performance
- **AI Bot Optimization** - Supports GPTBot, ClaudeBot, Google-Extended
- **Schema.org Markup** for rich search results
- **CloudFront CDN** for global performance
- **Serverless Architecture** with AWS Lambda

## 📁 Project Structure

```
/
├── README.md                    # Project documentation
├── replit.md                    # Project architecture and configuration
├── requirements-lambda.txt      # Python dependencies
├── src/                        # Source code
│   ├── lambda_function.py      # Main AWS Lambda handler (2,067 lines)
│   ├── main.py                 # Application entry point
│   ├── app.py                  # Flask application setup
│   ├── aws_mock_config.py      # Local development AWS mock
│   ├── css/                    # Stylesheets
│   │   ├── style.css           # Main application styles
│   │   ├── qr-purchase-modal.css # QR modal styling
│   │   └── cookie-consent.css  # Cookie consent styles
│   ├── js/                     # JavaScript modules
│   │   ├── main.js             # Core functionality
│   │   ├── speaking.js         # Speaking assessment
│   │   ├── mobile_*.js         # Mobile integration
│   │   └── assessment_*.js     # Assessment features
│   └── assets/                 # Static assets
│       ├── images/             # UI graphics and logos
│       ├── icons/              # SVG icons
│       ├── audio/              # Sample audio files
│       └── *.txt               # IELTS question banks (4,000+ questions)
├── templates/                  # HTML templates (production-verified)
│   ├── index.html              # Home page
│   ├── login.html              # Authentication
│   ├── profile.html            # User profile
│   ├── assessment_details.html # Assessment interface
│   └── *.html                  # Additional pages
├── config/                     # Configuration files
│   ├── capacitor.config.ts     # Mobile app configuration
│   └── deployment/             # Deployment configurations
│       ├── android_play_store_config.json
│       ├── ai_seo_gdpr_lambda.zip
│       ├── clean_lambda_with_deps.zip
│       └── BRANCH_COMMIT_COMMANDS.sh
├── docs/                       # Documentation
│   ├── guides/                 # Setup and deployment guides
│   │   ├── COMPLETE_REBUILD_GUIDE.md
│   │   ├── ANDROID_DEPLOYMENT_GUIDE.md
│   │   ├── AWS_PRODUCTION_DEPLOYMENT_INSTRUCTIONS.md
│   │   └── *.md
│   └── api/                    # API documentation
│       ├── API_ENDPOINTS.md
│       ├── API_INTEGRATION_GUIDE.md
│       └── DATABASE_SCHEMA.md
```

## 🚀 Getting Started

### Prerequisites
- AWS Account with Lambda, DynamoDB, Bedrock access
- Node.js 18+ (for mobile app development)
- Python 3.9+ (for Lambda functions)

### Quick Start
1. **Clone Repository**
   ```bash
   git clone https://github.com/WWPCA/ReplitRepo.git
   cd ReplitRepo
   ```

2. **Deploy to AWS Lambda**
   ```bash
   # Follow the complete rebuild guide
   # See: docs/guides/COMPLETE_REBUILD_GUIDE.md
   ```

3. **Configure Environment Variables**
   ```bash
   # Set required environment variables
   # See: docs/guides/ENVIRONMENT_VARIABLES.md
   ```

4. **Set Up Database**
   ```bash
   # Create DynamoDB tables
   # See: docs/api/DATABASE_SCHEMA.md
   ```

### Environment Variables Required
```env
DATABASE_URL=your_dynamodb_connection
RECAPTCHA_V2_SITE_KEY=your_recaptcha_site_key
RECAPTCHA_V2_SECRET_KEY=your_recaptcha_secret_key
AWS_REGION=us-east-1
SES_REGION=us-east-1
```

## 🏗️ Architecture

### Backend (AWS Serverless)
- **AWS Lambda** - Serverless compute for all backend operations
- **DynamoDB Global Tables** - Cross-region data replication
- **AWS Bedrock** - Nova Sonic (speaking) & Nova Micro (writing)
- **API Gateway** - REST and WebSocket endpoints
- **CloudFront** - Global CDN and security

### Frontend (Progressive Web App)
- **Responsive Design** - Mobile-first approach
- **Real-time Communication** - WebSocket for speaking assessments
- **Cross-platform** - Works on mobile browsers and desktop

### Mobile Apps (Capacitor)
- **iOS App** - Native iOS application
- **Android App** - Native Android application
- **In-App Purchases** - App Store and Google Play integration

## 🎯 Assessment Features

### Writing Assessment (TrueScore®)
- AI-powered evaluation using AWS Nova Micro
- Official IELTS band descriptors (1-9 scale)
- Academic and General Training tasks
- Detailed feedback on grammar, vocabulary, coherence

### Speaking Assessment (ClearScore®)
- Real-time conversation with Maya AI examiner
- AWS Nova Sonic en-GB-feminine voice
- Interactive speaking test simulation
- Pronunciation and fluency evaluation

## 🔒 Security Features

- **Authentication**: bcrypt password hashing, reCAPTCHA v2 protection
- **GDPR Compliance**: Privacy policy with AI disclosure, user consent tracking
- **Content Safety**: AI content monitoring, user reporting system
- **Session Management**: Secure token-based sessions with DynamoDB storage

## 🌍 Production Deployment

**Live Website:** [www.ieltsaiprep.com](https://www.ieltsaiprep.com)
- AWS Lambda function: `ielts-genai-prep-api`
- CloudFront distribution: Global CDN
- Multi-region deployment: us-east-1, eu-west-1, ap-southeast-1

## 📊 Pricing

- **$36 per assessment package** (4 attempts per module type)
- **Mobile app purchases** with cross-platform access
- **Academic and General Training** modules available

## 📖 Documentation

### Quick Links
- [Complete Rebuild Guide](docs/guides/COMPLETE_REBUILD_GUIDE.md)
- [API Documentation](docs/api/API_ENDPOINTS.md)
- [Database Schema](docs/api/DATABASE_SCHEMA.md)
- [Android Deployment](docs/guides/ANDROID_DEPLOYMENT_GUIDE.md)
- [AWS Deployment](docs/guides/AWS_PRODUCTION_DEPLOYMENT_INSTRUCTIONS.md)

### Assessment Content
- **4,000+ Questions** - Academic and General Training
- **Speaking Scenarios** - Real IELTS test situations
- **Writing Prompts** - Essays, letters, and task-specific content
- **Reading Passages** - Comprehensive context files

## 🤝 Contributing

This is a production platform. For deployment and configuration questions, refer to the documentation in the `docs/` directory.

## 📄 License

Proprietary software for IELTS test preparation. All rights reserved.

## 🆘 Support

For technical support and deployment assistance, refer to the comprehensive guides in the `docs/guides/` directory.

---

**Built with ❤️ using AWS Serverless Technologies**