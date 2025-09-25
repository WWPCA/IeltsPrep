# IELTS GenAI Prep - Website UI Package

This package contains all the UI components and assets needed to replicate the beautiful IELTS GenAI Prep website interface.

## Features

- **Modern Design**: Professional UI with Bootstrap 5.2.3 and custom CSS
- **Responsive Layout**: Mobile-first design that works on all devices  
- **Purple Gradient Theme**: Beautiful color scheme with CSS variables
- **Professional Components**: Hero sections, pricing cards, testimonials, navigation
- **Interactive Elements**: Mobile menu, connection monitoring, device capability checking
- **TrueScore® & ClearScore® Branding**: Professional assessment technology branding

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python app.py
   ```

3. **View in browser:**
   Open http://localhost:5000 to see the website

## File Structure

```
website_ui_package/
├── app.py                  # Flask application with UI routes
├── requirements.txt        # Python dependencies
├── static/                # Static assets
│   ├── css/
│   │   ├── style.css      # Main stylesheet with purple theme
│   │   └── cookie-consent.css
│   ├── js/
│   │   ├── main.js        # Mobile menu and interactions
│   │   ├── connection.js   # Connection monitoring
│   │   └── cookie-consent.js
│   └── images/            # Icons and graphics
│       ├── checklist_icon.svg
│       ├── globe_icon.svg
│       ├── graduate_icon.svg
│       ├── ielts-logo.svg
│       └── writing_graphs/
└── templates/             # HTML templates
    ├── layout.html        # Base template with navigation
    ├── index.html         # Homepage with hero and pricing
    └── login.html         # Login page
```

## Key UI Components

### 1. Hero Section
- Purple gradient background
- Professional headline and tagline
- Call-to-action buttons
- Responsive design

### 2. Navigation
- Professional header with logo
- Mobile-responsive hamburger menu
- Footer with multiple sections

### 3. Pricing Cards
- TrueScore® Writing Assessment section
- ClearScore® Speaking Assessment section
- Professional card design with hover effects

### 4. Features Section
- Icon-based feature highlights
- Professional card layout
- SVG icons included

### 5. Testimonials
- User success stories
- Star ratings
- Professional card design

## Customization

### Colors
Main colors are defined in CSS variables in `static/css/style.css`:
- `--primary-color: #2c3e50`
- `--secondary-color: #3498db` 
- `--accent-color: #e74c3c`

### Branding
- Update logo and branding text in `templates/layout.html`
- Modify hero section content in `templates/index.html`
- Customize pricing cards and feature descriptions

### Assets
- Replace icons in `static/images/` with your own
- Update writing graphs in `static/images/writing_graphs/`
- Modify CSS in `static/css/style.css`

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Dependencies

- **Bootstrap 5.2.3**: UI framework
- **Font Awesome 6.2.1**: Icons
- **Google Fonts**: Roboto font family
- **Flask**: Python web framework (for running locally)

## Features Included

✅ Responsive mobile navigation  
✅ Professional hero section  
✅ Pricing cards with hover effects  
✅ Feature sections with icons  
✅ Testimonial cards  
✅ Professional footer  
✅ Login page design  
✅ Purple gradient theme  
✅ Mobile-first responsive design  
✅ Connection monitoring  
✅ Device capability checking  

## Notes

- This is a UI-focused package for replicating the visual design
- Backend functionality would need to be implemented separately
- All branding reflects the original IELTS GenAI Prep platform
- Includes mock routes for demonstration purposes