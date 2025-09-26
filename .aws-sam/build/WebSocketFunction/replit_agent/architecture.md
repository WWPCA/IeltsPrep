# Architecture Overview

## Overview

This repository contains an IELTS preparation application built with Flask. The application provides practice tests for all four IELTS components (Reading, Writing, Speaking, and Listening) for both Academic and General Training test types. It features AI-powered assessment, user subscription management, and adaptive test recommendations.

## System Architecture

The application follows a monolithic architecture pattern built on Flask. It consists of:

1. **Web Application Layer**: Flask-based web server handling HTTP requests, rendering templates, and managing user sessions.
2. **Business Logic Layer**: Python modules for test management, user authentication, assessment processing, and subscription handling.
3. **Data Access Layer**: SQLAlchemy ORM for database interactions.
4. **External Services Layer**: Integrations with AWS (Bedrock, Polly, Transcribe, S3) and OpenAI for AI assessment capabilities.

### Tech Stack

- **Backend**: Python with Flask framework
- **Database**: PostgreSQL (via SQLAlchemy)
- **Authentication**: Flask-Login
- **Frontend**: Flask templates with likely JavaScript/CSS (not fully visible in the repository)
- **AI Services**: AWS Bedrock, AWS Polly, AWS Transcribe, OpenAI GPT, AssemblyAI
- **Deployment**: Replit-based deployment with Gunicorn

## Key Components

### Core Application

- **`app.py`**: Flask application initialization, database setup, and extension configuration
- **`main.py`**: Main application entry point with route definitions
- **`models.py`**: Database models for users, practice tests, results, and subscriptions

### Test Management

The application supports various IELTS test types:

1. **Reading Tests**: 
   - Academic and General Training formats
   - Multiple question types (multiple choice, true/false/not given, matching features, etc.)

2. **Writing Tests**:
   - Academic (Task 1: graph/chart description, Task 2: essay)
   - General Training (Task 1: letter writing, Task 2: essay)

3. **Speaking Tests**:
   - Three-part interviews with AI assessment

4. **Listening Tests**:
   - Four sections with increasing difficulty
   - Audio playback and comprehension questions

### AI Assessment Services

The application leverages several AI services for assessment:

1. **AWS Bedrock Services** (`aws_bedrock_services.py`):
   - Uses Amazon's Nova Micro models for evaluating IELTS writing and speaking responses
   - Structured assessment based on IELTS band descriptors

2. **AssemblyAI Integration** (`assemblyai_services.py`):
   - Transcribes speech for speaking assessments
   - Works with OpenAI for evaluation against IELTS criteria

3. **AWS Services** (`aws_services.py`):
   - Transcribe for speech-to-text
   - Polly for text-to-speech
   - S3 for audio file storage

### User Management

- User registration and authentication via Flask-Login
- Subscription management with tiered access (free, premium)
- Country-specific pricing (`create_country_pricing.py`)
- Test result tracking and progress analytics

## Data Models

Key database models include:

1. **User**: Stores user information, authentication details, and subscription status
2. **PracticeTest**: Individual test components (reading, writing, listening, speaking sections)
3. **CompletePracticeTest**: Groups related test sections into complete IELTS tests
4. **TestResult**: Records user test attempts and scores
5. **CountryPricing**: Supports region-specific subscription pricing

## Data Flow

1. **User Registration/Login Flow**:
   - User registers/logs in → authentication → dashboard access
   - Subscription status determines available content

2. **Practice Test Flow**:
   - User selects test type → system presents appropriate test
   - User completes test → submission → AI assessment → results display

3. **Assessment Flow**:
   - Writing: User submits text → AWS Bedrock or other AI service evaluates → structured feedback
   - Speaking: User records audio → AssemblyAI transcribes → AI evaluates → feedback
   - Reading/Listening: User submits answers → automated checking against answer key → score calculation

## External Dependencies

The application relies on several external services:

1. **AWS Services**:
   - **Bedrock**: For AI assessment using foundation models
   - **Transcribe**: For speech-to-text conversion
   - **Polly**: For text-to-speech generation
   - **S3**: For file storage

2. **AssemblyAI**:
   - For advanced speech recognition and transcription

3. **OpenAI**:
   - For assessment and feedback generation

## Deployment Strategy

The application is configured for deployment on Replit with the following characteristics:

1. **Runtime Environment**:
   - Python 3.11
   - PostgreSQL 16

2. **Web Server**:
   - Gunicorn as the WSGI HTTP server
   - Binding to 0.0.0.0:5000
   - Port forwarding: 5000 → 80 (external)

3. **Dependencies**:
   - FFmpeg for audio processing
   - Python packages managed through a package manager

4. **Scaling**:
   - Configured for autoscaling (`deploymentTarget = "autoscale"`)
   - Reuse-port and reload capabilities for development

5. **Workflows**:
   - Defined project startup workflows in the Replit configuration

## Security Considerations

1. **Authentication**: Flask-Login for session management
2. **CSRF Protection**: Flask-WTF CSRF protection
3. **API Keys**: Environment variables for service credentials
4. **Proxy Support**: ProxyFix middleware for working behind proxies

## Development and Testing

The repository contains numerous utility scripts for:
- Adding test data
- Checking model integrity
- Testing AWS service connectivity
- Validating AI model access

These appear to be development tools rather than part of the production application.

## Future Considerations

1. **Service Isolation**: The monolithic architecture could be refactored toward microservices, particularly for the AI assessment components.
2. **Scalability**: While the current deployment targets Replit autoscaling, a more robust cloud deployment might be needed for growth.
3. **Testing Automation**: Additional automated testing would benefit the reliability of the AI assessment components.