# IELTS GenAI Prep - System Architecture

## Overview

IELTS GenAI Prep is a comprehensive AI-powered IELTS test preparation platform that has evolved from a Flask-based web application to a pure serverless AWS Lambda architecture. The system provides assessment services for both Academic and General Training IELTS with QR code authentication for seamless mobile-to-web user experiences.

## System Architecture

### Backend Infrastructure
- **Pure AWS Lambda Serverless**: Complete migration from Flask to serverless functions
- **Multi-Region Deployment**: Global deployment across us-east-1, eu-west-1, and ap-southeast-1
- **API Gateway**: Regional endpoints with automatic routing based on user location
- **WebSocket API**: Real-time bi-directional communication for Nova Sonic streaming

### Frontend Architecture
- **Progressive Web App**: Responsive design optimized for mobile and desktop
- **Capacitor Mobile App**: Native iOS/Android apps with App Store integration
- **QR Code Authentication**: Seamless authentication flow between mobile app and web platform

### AI Services Integration
- **Amazon Nova Sonic**: Bi-directional speech-to-speech conversations with AI examiner Maya (us-east-1 only)
- **Amazon Nova Micro**: Text processing and assessment evaluation
- **Real-time Streaming**: WebSocket-based audio streaming for speaking assessments

## Key Components

### Authentication System
- **Mobile-First Authentication**: Users must register and purchase through mobile app first
- **Cross-Platform Login**: Same credentials work on both mobile app and website
- **Session Management**: Standard web session with 1-hour duration after mobile app login
- **Purchase Verification**: Apple App Store and Google Play Store receipt validation in mobile app

### Assessment Engine
- **Four Assessment Types**: Academic Speaking, Academic Writing, General Speaking, General Writing
- **AI-Powered Evaluation**: Comprehensive feedback across all IELTS criteria
- **Multi-Modal Support**: Text, audio, and visual assessment capabilities

### Mobile App Integration
- **In-App Purchases**: $36.00 per assessment product across both platforms
- **Regional API Routing**: Automatic selection of nearest Lambda endpoint
- **Native Platform Features**: Leverages Capacitor 7.3.0 for device capabilities
- **Dual-Platform Access**: Users can complete assessments directly in mobile app OR access via desktop/laptop through QR code
- **Flexible User Experience**: One purchase enables access on both mobile and web platforms

## Data Flow

### Purchase-to-Assessment Flow
1. User downloads mobile app and creates account (iOS/Android)
2. User purchases assessment in mobile app with App Store/Google Play billing
3. App Store receipt validation via Lambda backend
4. User can complete assessments directly in mobile app OR login to website using same credentials
5. Website login creates standard web session for desktop access
6. Assessment completion with AI-powered evaluation on either platform

### Speech Assessment Flow
1. User initiates speaking assessment on web platform
2. WebSocket connection established to us-east-1 (global routing)
3. Bi-directional audio streaming with Nova Sonic
4. Real-time conversation with AI examiner Maya
5. Transcript generation and assessment scoring
6. Detailed feedback delivery (no voice data retention)

## External Dependencies

### AWS Services
- **Lambda**: Serverless compute for all backend operations
- **DynamoDB Global Tables**: Cross-region data replication
- **ElastiCache Redis**: Session storage and real-time data
- **Bedrock**: Nova Sonic and Nova Micro model access
- **API Gateway**: REST and WebSocket API management

### Third-Party Integrations
- **Apple App Store**: In-app purchase processing and receipt validation
- **Google Play Store**: Android purchase verification
- **Stripe**: Fallback payment processing (legacy)
- **Capacitor**: Mobile app framework and native device access

### Development Tools
- **Serverless Framework**: Infrastructure as code deployment
- **SAM CLI**: Local Lambda development and testing
- **AWS CLI**: Resource management and deployment automation

## Deployment Strategy

### Multi-Region Serverless Deployment
- **Primary Region**: us-east-1 (Nova Sonic availability)
- **Secondary Regions**: eu-west-1, ap-southeast-1 (reduced latency)
- **Global Tables**: Automatic DynamoDB replication across regions
- **CDN Integration**: Regional content delivery optimization

### Mobile App Distribution
- **Apple App Store**: iOS native app with TestFlight beta testing
- **Google Play Store**: Android app with staged rollout capability
- **Capacitor Build Pipeline**: Automated native app compilation

### Development Environment
- **Replit Integration**: Local development with AWS mock services
- **Flask Compatibility Layer**: Maintains existing template compatibility
- **Environment Switching**: Seamless transition between local and serverless modes

## Recent Changes

- June 20, 2025: SHARED USER DATABASE DEPLOYED - Mobile App and Website Authentication Unified
  - Implemented shared user database for seamless authentication between mobile app and website
  - Users can now register in mobile app and login to website with same credentials automatically
  - Deployed Lambda function with proper password hashing (PBKDF2-HMAC-SHA256) and session management
  - API Gateway direct endpoint confirmed working: https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod/api/login
  - CloudFront routing issue identified - API requests currently work via direct Lambda endpoint
  - Test account operational with shared authentication: test@ieltsgenaiprep.com / testpassword123
  - Mobile app purchases now properly linked to website dashboard access
  - Ready for App Store screenshot generation using working authentication system

- June 20, 2025: DNS SIMPLIFIED TO WWW-ONLY - Single Domain Configuration Complete
  - Removed DNS A record for ieltsaiprep.com from Route 53
  - Removed SSL validation CNAME records (certificates already validated)
  - Route 53 zone now contains only essential records: NS, SOA, and www A record
  - Only www.ieltsaiprep.com has DNS resolution (propagated globally)
  - CloudFront and DNS consistently serve single domain only
  - Mobile app correctly configured for www.ieltsaiprep.com backend

- June 20, 2025: iOS APP STORE DEPLOYMENT READY - Mobile App Configured for Apple App Store
  - Updated Capacitor configuration to use www.ieltsaiprep.com domain
  - iOS platform synced successfully with 6 Capacitor plugins
  - Created comprehensive App Store deployment guide and assets
  - Configured 4 in-app purchase products at $36 each (Academic/General Writing/Speaking)
  - App Store metadata, deployment script, and technical documentation completed
  - Ready for Apple Developer Account setup and Xcode archiving process

- June 20, 2025: CLOUDFRONT UPDATED TO WWW-ONLY DOMAIN - Single Domain Configuration Active
  - Updated CloudFront distribution to serve only www.ieltsaiprep.com (removed ieltsaiprep.com alias)
  - Distribution status: InProgress (propagating globally, 15-20 minutes)
  - Primary domain now exclusively: www.ieltsaiprep.com
  - Mobile app and all documentation should reference www.ieltsaiprep.com only

- June 20, 2025: MOBILE-FIRST AUTHENTICATION TEMPLATES DEPLOYED - All Preview Pages Now Live
  - Successfully migrated from QR code strategy to simple username/password authentication with Google reCAPTCHA
  - Deployed comprehensive login page matching exact preview design with mobile-first instructions
  - Implemented complete privacy policy and terms of service templates with detailed AI technology coverage
  - Removed legal links from navigation headers, kept only in footer as requested
  - All Lambda templates now reflect mobile-first architecture: users register in app → login on website
  - Authentication flow clearly guides users through 3-step process: Download app → Purchase → Login anywhere
  - Website ieltsaiprep.com now serves all comprehensive templates from preview with proper mobile-first guidance

- June 20, 2025: COMPREHENSIVE WEBSITE DESIGN DEPLOYED - Complete Preview Template Now Live
  - Successfully updated Lambda function to serve detailed home page design matching user's comprehensive preview template
  - Deployed enhanced website with complete TrueScore® Writing Assessment and ClearScore® Speaking Assessment sections
  - Implemented detailed pricing cards showing $36 for 4 assessments across all product types (Academic/General Writing/Speaking)
  - Added comprehensive "GenAI Assessed IELTS Modules" section with professional branding and feature descriptions
  - Enhanced "Why Choose IELTS GenAI Prep" section with detailed assessment preparation information
  - Professional domain ieltsaiprep.com now serves complete design matching user specifications exactly
  - Website ready for production with comprehensive Bootstrap styling, responsive design, and enhanced user experience
  - Mobile app can be confidently submitted to app stores with verified professional website design
  - Implemented complete HTTP method support (GET, POST, PUT, DELETE) for full API functionality
  - Configured path-specific cache behaviors for optimal serverless application performance
  - SSL certificate validated with TLSv1.2_2021 security protocol for production-grade encryption
  - Route 53 DNS propagated globally with CloudFront edge network active worldwide
  - Professional domain replaces AWS Lambda URLs across all mobile app and website configurations
  - Mobile app production-ready for App Store submission with verified ieltsaiprep.com endpoints

- June 18, 2025: CUSTOM DOMAIN SETUP IN PROGRESS - SSL Certificate Validation
  - Successfully requested SSL certificate for ieltsaiprep.com and www.ieltsaiprep.com through AWS Certificate Manager
  - Added required CNAME validation records to Namecheap DNS (pending propagation)
  - Created custom domain setup scripts and documentation
  - Next steps: Complete API Gateway custom domain mapping once certificate validates (24-48 hours)
  - Mobile app configuration ready to update with custom domain endpoints
  - App Store submission on hold pending custom domain completion

- June 18, 2025: CUSTOM DOMAIN CONFIGURATION - Updated for ieltsaiprep.com
  - Configured all legal links and privacy policy URLs to use custom domain ieltsaiprep.com
  - Updated App Store Connect configuration with professional domain URLs
  - Created custom domain setup scripts and documentation for AWS integration
  - Mobile app ready for App Store submission with professional domain references
  - Option provided to proceed with current Lambda URL or implement custom domain mapping

- June 18, 2025: WEBSITE DEPLOYMENT CORRECTED - AWS Lambda Frontend Fixed to Match Exact Design
  - Fixed critical deployment issue where Lambda function was serving incorrect HTML template
  - Replaced Lambda's HTML with exact Bootstrap-based template from working Replit preview
  - Verified deployed website now shows correct 4 separate assessment products at $36 each
  - Confirmed visual design matches user specifications: proper styling, colors, and layout
  - Production endpoint: https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod now serves correct design

- June 18, 2025: PRODUCTION DEPLOYMENT COMPLETE - AWS Lambda Backend Fully Operational
  - Successfully deployed complete AWS Lambda serverless backend to production environment
  - Implemented secure PBKDF2-HMAC-SHA256 password authentication with 100,000 iterations
  - Fixed DynamoDB table schema compatibility issues for auth-tokens and users tables
  - Verified complete authentication flow: registration, login, and session-based assessment access
  - Production API Gateway endpoint active: https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod
  - All AWS resources deployed and functional: Lambda function, 4 DynamoDB tables, API Gateway
  - Comprehensive production testing completed with full authentication and assessment access verification
  - Created detailed production deployment documentation with all endpoints and configuration details
  - Mobile app configuration updated with production AWS endpoints for App Store deployment readiness

- June 17, 2025: Created comprehensive AWS production deployment infrastructure
  - Built complete SAM template with DynamoDB tables, Lambda functions, and API Gateway routing
  - Created automated infrastructure deployment script for all AWS resources
  - Implemented IELTS assessment rubrics data population with Nova AI system prompts
  - Added production configuration script for environment setup and endpoint testing
  - Created detailed AWS deployment guide with step-by-step instructions
  - Configured WebSocket API for Nova Sonic bi-directional speech streaming
  - Set up IAM roles and policies for Bedrock, DynamoDB, and ElastiCache access
  - Built mobile app configuration with iOS/Android in-app purchase integration
  - Created website production endpoint configuration with automatic environment detection
  - Developed Nova AI testing script for validating real Bedrock integration before full deployment
  - Added comprehensive mobile purchase flow with Apple App Store and Google Play verification
  - Implemented automatic endpoint configuration script that updates all mobile and web configs
  - Created complete production deployment guide with 5-command deployment process

- June 16, 2025: Implemented mobile-first authentication architecture replacing QR code system
  - Created secure mobile-first authentication flow where users register and purchase through mobile app
  - Users can login to website using same mobile app credentials for cross-platform access
  - Removed QR code complexity in favor of standard username/password authentication with bcrypt
  - Built comprehensive login page guiding new users to download mobile app first
  - Created dashboard page showing purchased assessments with secure session management
  - Updated "How It Works" section to reflect simplified 3-step process: Download → Purchase → Login Anywhere
  - Enhanced security by eliminating temporary QR tokens and potential interception risks
  - Maintained dual-platform access while simplifying authentication architecture
  - Added comprehensive legal compliance with privacy policy and terms of service pages
  - Implemented mandatory terms acceptance modal before mobile app purchases
  - Enhanced purchase flow with clear non-refundable policy communication
  - Added dual checkbox system requiring separate agreement to Terms of Service AND Privacy Policy
  - Implemented "By creating an account, you agree to our Terms of Service and Privacy Policy" text in all registration forms

- June 14, 2025: Successfully enhanced mobile app home screen with comprehensive GenAI assessment information
  - Implemented prominent gradient banner in top half explaining desktop/laptop access
  - Added comprehensive TrueScore® GenAI Writing Assessment section with detailed features
  - Added comprehensive ClearScore® GenAI Speaking Assessment section with detailed features
  - Created "Learn More Details" modals with full product information including technology explanations
  - Updated all branding to consistently highlight "GenAI" technology throughout the app
  - Fixed missing in-app purchase verification routes for Apple and Google platforms
  - Integrated complete purchase flow: mobile purchase → verification → QR generation → web access
  - Added purchase record storage in DynamoDB for transaction tracking
  - Provided consistent information matching website to help users understand products before purchase

## Changelog

- June 14, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.