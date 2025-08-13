# Verified Production Templates

## Templates That Actually Exist on www.ieltsaiprep.com

Based on verification of the live production website, these are the ONLY templates that exist:

### Core Pages (Verified URLs)
- **index.html** - Home page (/)
- **login.html** - Login page (/login)  
- **dashboard.html** - User dashboard (/dashboard)
- **profile.html** - User profile (/my-profile)
- **assessment_details.html** - Assessment pages (/assessment/*)

### Error Pages (Verified)
- **404.html** - Not found page
- **500.html** - Server error page

### GDPR/Legal Pages
- **privacy_policy.html** - Privacy policy (embedded in lambda)
- **terms_of_service.html** - Terms of service (embedded in lambda)

## URLs That Return 404 (Removed from Package)
- /qr-login → 404 (removed qr_login.html)
- /register → 404 (removed register.html)
- /contact → 404 (removed contact.html)
- /privacy → 404 (privacy content is embedded)
- /terms → 404 (terms content is embedded)
- /cookie-policy → 404 (removed cookie_policy.html)
- /delete-account → 404 (functionality exists but no dedicated page)

## Templates Embedded in Lambda Function
The production system has most content embedded directly in the lambda_function.py file rather than as separate templates. This includes:

- Home page content
- Login form
- Dashboard content  
- Privacy policy text
- Terms of service text
- Assessment interfaces

## Mobile-First Architecture
The production system is designed for:
1. **Mobile app registration** (users cannot register on website)
2. **QR code authentication** for web access
3. **Cross-platform usage** (purchase on mobile, use on web)

## Verified Production Features
- ✅ Home page with FAQ and pricing
- ✅ Login (for mobile app users only)
- ✅ Dashboard with 4 assessment types
- ✅ Assessment interfaces for writing/speaking
- ✅ Profile page with account management
- ✅ Purchase flow redirects to mobile app
- ✅ QR authentication system
- ✅ GDPR compliance features

This verification ensures the package contains only authentic production templates and functionality.