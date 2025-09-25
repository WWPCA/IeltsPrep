# IELTS GenAI Prep - Complete Website UI Package

This is a comprehensive UI package containing all pages and components from the IELTS GenAI Prep website, including the home page, all subpages, and robots.txt.

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the application  
python app.py

# 3. Open in browser
http://localhost:5000
```

## 📁 Complete Page Structure

### Main Pages
- **Home Page** (`/`) - Hero section, pricing, testimonials
- **Login** (`/login`) - User authentication page
- **Register** (`/register`) - User registration
- **Profile** (`/profile`) - User dashboard and assessments

### Assessment Pages
- **Assessment Products** (`/assessment-products`) - Package selection
- **Academic Speaking** (`/academic-speaking-selection`) - Academic speaking tests
- **General Speaking** (`/general-speaking-selection`) - General speaking tests  
- **Academic Writing** (`/academic-writing-selection`) - Academic writing tests
- **General Writing** (`/general-writing-selection`) - General writing tests

### Assessment Structure
- **Overview** (`/assessment-structure`) - Test structure information
- **Academic** (`/assessment-structure/academic`) - Academic test details
- **General Training** (`/assessment-structure/general-training`) - General test details

### Practice Tests
- **Practice Home** (`/practice`) - Practice test overview
- **Reading Practice** (`/practice/reading`) - Reading test practice
- **Writing Practice** (`/practice/writing`) - Writing test practice
- **Listening Practice** (`/practice/listening`) - Listening test practice
- **Speaking Practice** (`/practice/speaking`) - Speaking test practice

### Assessment Tools
- **Speaking Assessment** (`/speaking-assessment`) - Live speaking test
- **Writing Assessment** (`/writing-assessment`) - Live writing test
- **Conversational Speaking** (`/conversational-speaking`) - Maya AI conversation

### Legal & Support
- **Privacy Policy** (`/privacy-policy`) - GDPR compliant privacy policy
- **Terms of Service** (`/terms-of-service`) - Terms and conditions
- **Cookie Policy** (`/cookie-policy`) - Cookie usage policy
- **Contact** (`/contact`) - Contact information
- **Documentation** (`/documentation`) - User guides

### Account Management
- **Change Password** (`/change-password`) - Password management
- **Forgot Password** (`/forgot-password`) - Password recovery
- **Delete Account** (`/delete-account`) - Account deletion
- **My Data** (`/my-data`) - GDPR data access

### Technical Pages
- **Device Specs** (`/device-specs`) - System requirements
- **QR Login** (`/qr-login`) - Mobile QR authentication
- **Test Dashboard** (`/test-dashboard`) - Assessment dashboard

### SEO & Crawlers
- **robots.txt** (`/robots.txt`) - Search engine crawler instructions
- **sitemap.xml** (`/sitemap.xml`) - Site structure for search engines

## 🎨 UI Components Included

✅ **Professional Navigation** - Responsive header with mobile menu  
✅ **Hero Section** - Purple gradient with call-to-action  
✅ **Pricing Cards** - TrueScore® and ClearScore® assessment packages  
✅ **Feature Sections** - Icon-based highlights with professional styling  
✅ **Testimonials** - User success stories with ratings  
✅ **Footer** - Multi-section professional footer  
✅ **Forms** - Login, register, contact forms  
✅ **Error Pages** - Custom 404 and 500 error pages  
✅ **Admin Interface** - Administrative dashboard pages  

## 🔧 Customization

### Update Branding
- Edit `templates/layout.html` for site-wide branding
- Modify `static/css/style.css` for colors and styling
- Replace images in `static/images/` directory

### Add New Pages
- Create template in `templates/` directory
- Add route in `app.py`
- Update navigation in `templates/layout.html`

### Modify Styling
- Colors: Edit CSS variables in `static/css/style.css`
- Layout: Modify Bootstrap classes in templates
- Fonts: Update Google Fonts links in `templates/layout.html`

## 📱 Mobile Responsive

All pages are fully responsive with:
- Mobile-first design approach
- Hamburger navigation menu
- Touch-friendly buttons and forms
- Optimized images and loading

## 🔍 SEO Optimized

- **robots.txt** - AI crawler and search engine optimization
- **sitemap.xml** - Complete site structure mapping  
- **Meta tags** - Title and description optimization
- **Structured data** - Professional markup

## 🛡️ Security Features

- CSRF protection (demo tokens)
- Content Security Policy headers
- GDPR compliance pages
- Secure form handling

## 📊 Analytics Ready

Template structure supports:
- Google Analytics integration
- Cookie consent management
- User behavior tracking
- Performance monitoring

## 🔗 API Endpoints

Demo API endpoints included:
- `/api/health` - System health check
- `/api/demo-data` - Sample data for testing

## 📋 Template Structure

```
templates/
├── layout.html              # Base template
├── index.html               # Home page
├── login.html               # Login form
├── register.html            # Registration form
├── profile.html             # User profile
├── assessment_products.html # Assessment packages
├── assessments/            # Assessment pages
├── practice/               # Practice test pages
├── gdpr/                   # Legal compliance pages
├── admin/                  # Administrative interface
├── errors/                 # Error pages (404, 500)
└── ...                     # Additional subpages
```

## 🎯 Technologies Used

- **Flask** - Python web framework
- **Bootstrap 5.2.3** - UI framework
- **Font Awesome 6.2.1** - Icon library
- **Google Fonts** - Typography (Roboto)
- **Custom CSS** - Professional styling with purple theme
- **JavaScript** - Interactive functionality

## 📈 Performance Optimized

- Minified CSS and JavaScript
- Optimized image assets
- Lazy loading support
- Connection monitoring
- Low-bandwidth mode support

This package provides a complete, production-ready website structure that can be customized for any IELTS preparation platform or educational website.