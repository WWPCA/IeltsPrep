# Components Directory

## Purpose
This directory is reserved for future frontend components when the IELTS AI Prep platform evolves to a component-based architecture (React, Vue, or similar framework).

## Current Status
**Empty** - The current implementation uses server-side rendered HTML templates located in `/templates/`.

## Future Component Structure
When implementing a component-based frontend, this directory will contain:

```
src/components/
├── assessment/
│   ├── SpeakingAssessment.js     # Maya AI speaking interface
│   ├── WritingAssessment.js      # TrueScore writing evaluation
│   └── AssessmentTimer.js        # Timer component
├── auth/
│   ├── LoginForm.js              # Authentication form
│   ├── QRCodeAuth.js             # Mobile QR authentication
│   └── RegistrationFlow.js       # User registration
├── ui/
│   ├── Modal.js                  # Reusable modal component
│   ├── Button.js                 # Styled button component
│   └── Card.js                   # Content card component
└── shared/
    ├── Header.js                 # Site navigation
    ├── Footer.js                 # Site footer
    └── Layout.js                 # Page layout wrapper
```

## Current Architecture
The platform currently uses:
- **Flask backend** with Jinja2 templates
- **Server-side rendering** for all pages
- **JavaScript modules** in `/src/js/` for client-side functionality
- **HTML templates** in `/templates/` for page structure

## Migration Path
To implement components:
1. Choose frontend framework (React, Vue, Angular)
2. Set up build pipeline (Webpack, Vite, etc.)
3. Migrate templates to components
4. Implement client-side routing
5. Connect to existing Lambda API endpoints

## Note
Keep this directory for future development. The current Flask-based architecture is production-ready and handles all IELTS assessment functionality effectively.