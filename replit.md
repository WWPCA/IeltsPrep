### Overview

IELTS GenAI Prep is an AI-powered platform for IELTS test preparation. It offers assessment services for Academic and General Training IELTS, leveraging a serverless AWS Lambda architecture. The system supports QR code authentication for a seamless mobile-to-web user experience and utilizes AI for comprehensive evaluation across all IELTS criteria. The platform aims to provide high-quality, AI-driven assessment and feedback to help users prepare for the IELTS exam, with a focus on ease of access and consistent user experience across devices.

### User Preferences

Preferred communication style: Simple, everyday language.

### System Architecture

**Backend Infrastructure:**
- Pure AWS Lambda Serverless architecture.
- Multi-region deployment across `us-east-1`, `eu-west-1`, and `ap-southeast-1`.
- API Gateway for regional endpoints and automatic routing.
- WebSocket API for real-time bi-directional communication, especially for Nova Sonic streaming.

**Frontend Architecture:**
- Progressive Web App (PWA) optimized for mobile and desktop.
- Capacitor-based native iOS/Android mobile applications.
- QR Code Authentication for seamless transitions between mobile and web.

**AI Services Integration:**
- Amazon Nova Sonic for bi-directional speech-to-speech conversations with AI examiner Maya (primarily `us-east-1`).
- Amazon Nova Micro for text processing and assessment evaluation.
- Real-time streaming via WebSockets for speaking assessments.

**Key Components:**
- **Authentication System:** Mobile-first registration and purchase, cross-platform login, 1-hour web session management, and App Store/Google Play receipt validation.
- **Assessment Engine:** Supports four assessment types (Academic/General Speaking and Writing) with AI-powered, multi-modal evaluation.
- **Content Moderation System:** Real-time content filtering during speaking assessments with seamless conversation flow, maintaining authentic IELTS examination experience while ensuring appropriate content standards.
- **Mobile App Integration:** In-app purchases ($36 per assessment product), regional API routing, native platform features via Capacitor, and flexible dual-platform access.

**Data Flow:**
- **Purchase-to-Assessment:** User purchases in mobile app, receipt is validated, and assessment can be completed on mobile or web.
- **Speech Assessment:** Web-based initiation, WebSocket connection to `us-east-1`, bi-directional audio streaming with Nova Sonic, real-time conversation, transcript generation, and detailed feedback.

**Deployment Strategy:**
- Multi-Region Serverless Deployment with `us-east-1` as primary and `eu-west-1`, `ap-southeast-1` as secondary regions.
- DynamoDB Global Tables for cross-region data replication.
- Mobile App Distribution via Apple App Store and Google Play Store, with automated Capacitor build pipeline.
- Development environment integrates Replit with AWS mock services and Flask compatibility.

**UI/UX Decisions:**
- Professional, clean interface with simplified user messages (e.g., "Maya" as examiner, no technical AWS references).
- Responsive design with professional Bootstrap styling, purple gradient backgrounds, and modern card layouts.
- Authentic IELTS examination format with two-column layouts for writing assessments, timers, and word counters.
- Clear call-to-action buttons, glassmorphism-styled benefit icons, and smooth sequential animations.

**Security Guidelines:**
- Environment variables for all sensitive configuration values.
- CloudFront-based blocking with custom header validation to prevent direct API Gateway access.
- Google reCAPTCHA v2 integration for secure authentication.
- AWS SES email confirmation system for registration and account deletion.
- Real-time content moderation for speaking assessments with graduated response system (mild guidance, redirection, or assessment termination for severe violations).

**Payment Integration:**
- **Mobile-Only Purchase Model:** All payments processed exclusively through Apple App Store and Google Play Store ($36 per assessment package).
- **QR Code Bridge:** Seamless transition from mobile purchase to web platform access via QR code authentication.
- **No Web Payments:** Zero integration with web-based payment processors - maintaining strict mobile app store compliance.

### External Dependencies

**AWS Services:**
- **Lambda:** Serverless compute.
- **DynamoDB Global Tables:** Data storage and replication.
- **ElastiCache Redis:** Session storage and real-time data.
- **Bedrock:** Access to Nova Sonic and Nova Micro models.
- **API Gateway:** REST and WebSocket API management.
- **SES:** Email services.
- **Comprehend:** Content safety integration.
- **CloudFront:** Content Delivery Network.
- **Route 53:** DNS management.
- **Certificate Manager:** SSL/TLS certificates.

**Third-Party Integrations:**
- **Apple App Store:** In-app purchase processing and receipt validation.
- **Google Play Store:** Android purchase verification.
- **Capacitor:** Mobile app framework for native device access.
- **Google reCAPTCHA:** Bot detection and security.

**Development Tools:**
- **Serverless Framework:** Infrastructure as Code.
- **SAM CLI:** Local Lambda development and testing.
- **AWS CLI:** Resource management.