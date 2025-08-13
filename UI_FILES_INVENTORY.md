# Verified UI Files Inventory (Production Only)

## CSS Stylesheets (Production Verified)
- `static/css/style.css` - Main application styles
- `static/css/qr-purchase-modal.css` - QR code purchase modal styling
- `static/css/cookie-consent.css` - Cookie consent banner styles

## JavaScript Files (Production Verified)
- `static/js/main.js` - Core application functionality
- `static/js/speaking.js` - Speaking assessment interface
- `static/js/practice.js` - Practice mode functionality
- `static/js/mobile-purchase-config.js` - Mobile purchase configuration
- `static/js/mobile_api_client.js` - Mobile API client
- `static/js/mobile_purchase_integration.js` - Purchase flow integration
- `static/js/qr-purchase-redirect.js` - QR code purchase redirects
- `static/js/test-structure.js` - Test structure management
- `static/js/test_purchase_flow.js` - Purchase flow handling
- `static/js/assessment_recovery.js` - Assessment recovery features
- `static/js/connection.js` - Connection management
- `static/js/cookie-consent.js` - Cookie consent handling
- `static/js/error_suppressor.js` - Error suppression utilities
- `static/js/offline.js` - Offline functionality

## Images and Icons (Production Assets)
- `static/images/ielts-logo.svg` - Main IELTS logo
- `static/images/ielts_chart.svg` - IELTS scoring chart
- `static/images/checklist_icon.svg` - Checklist icon
- `static/images/globe_icon.svg` - Globe icon
- `static/images/graduate_icon.svg` - Graduate icon
- `static/images/graduation_cap_icon.svg` - Graduation cap icon
- `static/images/ai_coach.jpeg` - AI coach image
- `static/images/brain_ai.jpeg` - Brain AI image
- `static/images/comprehensive_test_prep.jpeg` - Test prep image
- `static/images/global_icon.jpeg` - Global icon image
- Plus additional writing graphs and UI assets

## Audio Files (Production Samples)
- `static/audio/accommodation_inquiry.mp3` - Sample accommodation inquiry
- `static/audio/community_center.mp3` - Community center audio
- `static/audio/customer_agent_conversation.mp3` - Customer service conversation
- `static/audio/urban_planning_lecture.mp3` - Urban planning lecture

## HTML Templates (Production Verified Only)

### Core Pages (Verified on www.ieltsaiprep.com)
- `templates/index.html` - Home page template
- `templates/login.html` - Login page (/login)
- `templates/profile.html` - User profile page (/my-profile)
- `templates/layout.html` - Base layout template
- `templates/assessment_details.html` - Assessment interface (/assessment/*)

### Error Pages (Production Verified)
- `templates/404.html` - Page not found
- `templates/500.html` - Server error page

### Legal Pages (Production Verified)
- `templates/privacy_policy.html` - Privacy policy
- `templates/terms_of_service.html` - Terms of service

## Content Embedded in Lambda Function

Most production content is embedded directly in `lambda_function.py` rather than separate templates:

### Embedded Templates
- **Home page content** - Full HTML with FAQ, pricing, and schema markup
- **Dashboard content** - Assessment selection interface
- **QR authentication** - QR code generation and verification pages
- **Privacy policy text** - Complete GDPR-compliant privacy content
- **Terms of service text** - Full terms with pricing and refund policy

### Why Content is Embedded
The production architecture uses embedded content for:
1. **Faster loading** - No file system access required
2. **Better caching** - CloudFront can cache full responses
3. **Simpler deployment** - Single Lambda package deployment
4. **Security** - No template injection vulnerabilities

## Templates Removed (Not in Production)
These templates were removed as they don't exist on the live www.ieltsaiprep.com:

- ❌ `register.html` - Registration is mobile-app only
- ❌ `qr_login.html` - QR functionality is embedded
- ❌ `contact.html` - No contact page in production
- ❌ `forgot_password.html` - No password recovery page
- ❌ All `assessments/` subdirectory templates
- ❌ All `practice/` subdirectory templates  
- ❌ All `admin/` subdirectory templates
- ❌ All `account/` subdirectory templates
- ❌ All test/demo templates

## Production Architecture Notes

The live www.ieltsaiprep.com uses:
- **Mobile-first registration** (no web registration form)
- **QR code authentication** for cross-platform access
- **Embedded content** in Lambda function for performance
- **Purchase redirects** to mobile app (no web purchase forms)
- **Minimal template files** - most content is programmatically generated

This inventory reflects only the authentic production templates and assets that actually exist on the live platform.