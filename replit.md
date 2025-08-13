# IELTS GenAI Prep - Compressed replit.md

## Overview
IELTS GenAI Prep is an AI-powered IELTS test preparation platform that evolved into a serverless AWS Lambda architecture. It offers assessment services for both Academic and General Training IELTS, leveraging QR code authentication for a seamless mobile-to-web user experience. The platform aims to provide comprehensive AI-powered evaluation, detailed feedback, and multi-modal assessment capabilities to help users prepare for the IELTS exam.

## User Preferences
Preferred communication style: Simple, everyday language.

## Recent Critical Fixes
- **August 13, 2025:** Created GitHub-ready project structure with professional organization
  - Reorganized into proper GitHub structure: src/, templates/, config/, docs/
  - Created professional README.md with project overview and getting started guide
  - Added package.json with NPM scripts for development and deployment
  - Professional .gitignore with comprehensive exclusions
  - Package: ielts-ai-prep-github-ready.zip (3.3MB, properly organized)
  - Ready for professional GitHub upload to https://github.com/WWPCA/ReplitRepo.git

- **August 13, 2025:** Created complete production package with authentic template verification
  - Verified all templates against live www.ieltsaiprep.com (removed non-production templates)
  - Fixed all template references across documentation and code
  - Complete authentication workflow with Google reCAPTCHA v2
  - SEO optimization, GDPR compliance, Maya AI integration included

- **August 10, 2025:** Fixed production robots.txt endpoint internal server error at https://www.ieltsaiprep.com/robots.txt
  - Added comprehensive error handling to handle_robots_txt() function
  - Implemented fallback robots.txt content to prevent future failures
  - Maintained AI SEO optimization for GPTBot, ClaudeBot, Google-Extended
  - Zero impact on other website functionality - only robots.txt endpoint modified

## System Architecture

### Backend Infrastructure
- **Pure AWS Lambda Serverless**: All backend operations are handled by AWS Lambda functions.
- **Multi-Region Deployment**: Global presence across us-east-1, eu-west-1, and ap-southeast-1.
- **API Gateway**: Regional REST and WebSocket endpoints for efficient routing and real-time communication.
- **WebSocket API**: Enables real-time bi-directional communication for streaming services like Nova Sonic.

### Frontend Architecture
- **Progressive Web App (PWA)**: Responsive design optimized for mobile and desktop browsers.
- **Capacitor Mobile App**: Native iOS/Android applications leveraging Capacitor for platform-specific features and App Store integration.
- **QR Code Authentication**: Facilitates seamless authentication between mobile and web platforms.

### AI Services Integration
- **Amazon Nova Sonic**: Provides bi-directional speech-to-speech conversations with AI examiner Maya for speaking assessments (us-east-1 only).
- **Amazon Nova Micro**: Utilized for text processing and assessment evaluation.
- **Real-time Streaming**: WebSocket-based audio streaming for interactive speaking assessments.

### Key Components
- **Authentication System**: Mobile-first registration and purchase via the mobile app, with cross-platform login and standard web session management. Purchase verification is handled via Apple App Store and Google Play Store receipt validation.
- **Assessment Engine**: Supports four assessment types (Academic Speaking, Academic Writing, General Speaking, General Writing) with AI-powered evaluation based on IELTS criteria and multi-modal support.
- **Mobile App Integration**: Manages in-app purchases, regional API routing, and leverages native platform features for a dual-platform user experience (mobile app or web via QR code).

### Data Flow
- **Purchase-to-Assessment Flow**: User purchases an assessment in the mobile app, which is validated server-side, enabling access on either mobile or web platforms.
- **Speech Assessment Flow**: Initiated on the web, establishes a WebSocket connection for bi-directional audio streaming with Nova Sonic, enabling real-time conversation with the AI examiner Maya, followed by transcript generation and scoring.

### UI/UX Decisions
- Responsive design with a mobile-first approach.
- Professional branding including "TrueScore®" and "ClearScore®".
- Consistent use of purple gradient themes and modern card layouts.
- Clean and professional interface without technical backend details exposed to the user.
- Implementation of professional error pages for 404 and 500 errors.
- Enhanced typography and visual formatting for readability.

### Security Guidelines
- Use environment variables for all sensitive configuration values.
- Redact sensitive information from project documentation and communication.
- CloudFront-based blocking using custom header validation to restrict direct API Gateway access.
- Comprehensive content safety measures for GenAI policy compliance, including content validation, red team testing, and safety monitoring.
- Implementation of robust connectivity safeguards with auto-save, retries, and local storage backup to prevent data loss.
- Standardized feedback format across all AI modules (Nova Micro and Nova Sonic).
- Secure password authentication (PBKDF2-HMAC-SHA256).

## External Dependencies

### AWS Services
- **Lambda**: Serverless compute.
- **DynamoDB Global Tables**: Cross-region data replication for assessment questions, user data, and authentication tokens.
- **ElastiCache Redis**: Used for session storage and real-time data.
- **Bedrock**: Provides access to Nova Sonic and Nova Micro models.
- **API Gateway**: Manages REST and WebSocket APIs.
- **SES**: Email sending service for welcome and account deletion notifications.
- **CloudFront**: Content Delivery Network for global content delivery and security.
- **Route 53**: DNS management.

### Third-Party Integrations
- **Apple App Store**: In-app purchase processing and receipt validation.
- **Google Play Store**: Android purchase verification.
- **Capacitor**: Mobile app framework.
- **Google reCAPTCHA v2**: For secure authentication.
- **Stripe**: Legacy fallback payment processing.

### Development Tools
- **Serverless Framework**: Infrastructure as Code.
- **SAM CLI**: Local Lambda development and testing.
- **AWS CLI**: Resource management and deployment automation.