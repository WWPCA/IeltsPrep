# API Endpoints Documentation

## Production API Base URL
https://www.ieltsaiprep.com

## Public Endpoints

### Home Page
- **GET** `/` - Main landing page with SEO optimization, FAQ, and pricing

### Legal Pages  
- **GET** `/privacy-policy` - GDPR-compliant privacy policy
- **GET** `/terms-of-service` - Terms of service with current pricing

### Authentication
- **GET** `/login` - Login page with reCAPTCHA v2
- **POST** `/api/login` - Login authentication endpoint
- **GET** `/register` - Registration page

### Utility
- **GET** `/robots.txt` - SEO-optimized robots.txt for AI bots

## Protected Endpoints (Require Authentication)

### Dashboard
- **GET** `/dashboard` - Main user dashboard with assessment options

### Assessments
- **GET** `/assessment/academic-writing` - Academic writing assessment
- **GET** `/assessment/general-writing` - General training writing assessment  
- **GET** `/assessment/academic-speaking` - Academic speaking assessment
- **GET** `/assessment/general-speaking` - General training speaking assessment

### User Management
- **GET** `/my-profile` - User profile page with account management
- **POST** `/api/delete-account` - Account deletion endpoint
- **POST** `/api/export-data` - Data export for GDPR compliance

## API Response Format

### Success Response
```json
{
  "success": true,
  "data": {...},
  "message": "Operation completed successfully"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message",
  "code": "ERROR_CODE"
}
```

## Authentication Method
- Session-based authentication
- QR code integration for mobile-to-web access
- Google reCAPTCHA v2 verification

## Rate Limiting
- Standard CloudFront rate limiting applied
- Assessment attempts limited by purchase validation

## Security Headers
- Content-Type: text/html (for pages)
- Cache-Control: Varies by endpoint
- Custom security headers via CloudFront