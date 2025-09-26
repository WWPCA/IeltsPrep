"""
Simple Flask Application for IELTS GenAI Prep
Serves the correct templates with TrueScore® and ClearScore® branding
"""

from flask import Flask, render_template

# Mock functions for template compatibility  
def csrf_token():
    return "mock-csrf-token"

class MockConfig:
    RECAPTCHA_SITE_KEY = "mock-recaptcha-key"

app = Flask(__name__)
app.jinja_env.globals['csrf_token'] = csrf_token
app.jinja_env.globals['config'] = MockConfig()
app.secret_key = 'dev-secret-key-for-testing'

# Add cache buster for template compatibility
app.jinja_env.globals['cache_buster'] = '1.0'

@app.route('/')
def home():
    """Serve main homepage with TrueScore® and ClearScore® branding"""
    return render_template('index.html')

@app.route('/index')
def index():
    """Index route for template compatibility"""
    return render_template('index.html')

@app.route('/login')
def login():
    """Login page"""
    return render_template('login.html')

@app.route('/register')
def register():
    """Register page"""
    return render_template('register.html')

@app.route('/assessment-products')
def assessment_products_page():
    """Assessment products page"""
    return render_template('assessment_products.html')

@app.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html')

@app.route('/privacy')
def privacy():
    """Privacy page"""
    return render_template('privacy.html')

@app.route('/qr-auth')
def qr_auth():
    """QR authentication page"""
    return render_template('qr_auth_page.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'service': 'IELTS GenAI Prep',
        'templates': 'working'
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)