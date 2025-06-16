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
- **QR Code-Based Authentication**: Mobile app generates QR codes for web platform login
- **Session Management**: 10-minute QR token expiry, 1-hour web session duration
- **Purchase Verification**: Apple App Store and Google Play Store receipt validation

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
1. User purchases assessment in mobile app (iOS/Android)
2. App Store receipt validation via Lambda backend
3. QR code generation with encrypted session token
4. User scans QR code on web platform
5. Session authentication and assessment access granted
6. Assessment completion with AI-powered evaluation

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

- June 16, 2025: Updated public landing page to match original website design with dual-platform access
  - Recreated public homepage using original Bootstrap layout from templates/index.html
  - Fixed header layout issues to prevent content overlap on mobile and desktop
  - Updated "How It Works" section to reflect dual-platform access capabilities
  - Clarified that users can access assessments directly in mobile app OR via desktop through QR code
  - Maintained existing authentication flow while allowing public browsing of assessment information
  - Enhanced mobile responsiveness with proper spacing and navigation
  - Updated architecture documentation to reflect flexible access options
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