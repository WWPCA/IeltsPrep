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

- June 18, 2025: Enhanced security and legal compliance
  - Added Google reCAPTCHA v2 verification to website login for enhanced security
  - Updated all pricing displays to show "$36 for 4 attempts" with clear attempt counting
  - Implemented comprehensive 4-attempt assessment system with unique question rotation
  - Enhanced Terms of Service with "Prices are subject to change without notice" and "We may modify these terms at any time and without notice"
  - Fixed login page layout issues and mobile app guidance display
  - Completed backend assessment counter system ensuring each purchase provides exactly 4 unique assessment attempts

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