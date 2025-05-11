"""
Integrate GDPR Routes into Application

This script updates the main application file to integrate the GDPR routes
and apply necessary middleware for cookie and consent management.
"""

import os
import re
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_main_app():
    """Update the main app.py file to integrate GDPR routes"""
    try:
        # Determine the main app file (app.py or main.py)
        app_file = 'app.py'
        if not os.path.exists(app_file):
            app_file = 'main.py'
            if not os.path.exists(app_file):
                logger.error("Could not find app.py or main.py")
                return False
        
        logger.info(f"Updating {app_file} with GDPR integration")
        
        # Read the current file
        with open(app_file, 'r') as f:
            content = f.read()
        
        # Create a backup
        with open(f'{app_file}.bak', 'w') as f:
            f.write(content)
        
        # Check if GDPR routes are already registered
        if 'from gdpr_routes import gdpr_bp' in content:
            logger.info("GDPR routes already integrated. No changes needed.")
            return True
        
        # Find import section
        import_pattern = r'(import .*?\n\n)'
        import_section = re.search(import_pattern, content, re.DOTALL)
        
        if not import_section:
            logger.error("Could not find import section in app file")
            return False
        
        # Add GDPR imports after existing imports
        imports_end = import_section.end()
        updated_content = content[:imports_end] + "from gdpr_routes import gdpr_bp\n" + content[imports_end:]
        
        # Find app initialization
        app_init_pattern = r'app = Flask\(__name__\)'
        app_init_match = re.search(app_init_pattern, updated_content)
        
        if not app_init_match:
            logger.error("Could not find Flask app initialization")
            return False
        
        # Find where blueprints/routes are registered
        # Look for app.register_blueprint or @app.route
        bp_pattern = r'(app\.register_blueprint.*?\))|(^@app\.route)'
        bp_match = re.search(bp_pattern, updated_content, re.MULTILINE)
        
        if not bp_match:
            # Try to find a good insertion point before the app.run() or if __name__ == "__main__"
            insertion_point = updated_content.find('if __name__ == "__main__"')
            if insertion_point == -1:
                insertion_point = updated_content.find('app.run(')
            
            if insertion_point == -1:
                # As a last resort, add at the end of the file
                insertion_point = len(updated_content)
            
            # Add blueprint registration
            bp_registration = "\n\n# Register GDPR blueprint\napp.register_blueprint(gdpr_bp, url_prefix='/privacy')\n"
            updated_content = updated_content[:insertion_point] + bp_registration + updated_content[insertion_point:]
        else:
            # Add after the last blueprint registration
            bp_end = bp_match.end()
            next_line_end = updated_content.find('\n', bp_end) + 1
            
            # Add blueprint registration
            bp_registration = "\n# Register GDPR blueprint\napp.register_blueprint(gdpr_bp, url_prefix='/privacy')\n"
            updated_content = updated_content[:next_line_end] + bp_registration + updated_content[next_line_end:]
        
        # Find a good spot to add GDPR middleware
        # Look for app.before_request or similar
        middleware_pattern = r'(@app\.before_request)|(app\.before_request)'
        middleware_match = re.search(middleware_pattern, updated_content)
        
        if not middleware_match:
            # Find a good insertion point after app creation but before routes
            # Try to find app configuration section
            config_pattern = r'(app\.config\[.*?\].*?\n)'
            config_match = re.search(config_pattern, updated_content, re.DOTALL)
            
            if config_match:
                insertion_point = config_match.end()
            else:
                # Otherwise, insert after app initialization
                insertion_point = updated_content.find('\n', app_init_match.end()) + 1
            
            # Add GDPR middleware
            gdpr_middleware = """
# GDPR Cookie Consent Middleware
@app.before_request
def check_gdpr_consent():
    # Import inside function to avoid circular imports
    import gdpr_framework as gdpr
    from flask import request, session
    
    # Skip for static files and certain endpoints
    if request.path.startswith('/static') or request.path.startswith('/privacy') or request.endpoint in ['login', 'logout', 'register']:
        return
        
    # Check if user has made cookie choices
    if 'cookie_preferences' not in session:
        # Set defaults (essential only)
        session['cookie_preferences'] = {
            'essential': True,
            'functional': False,
            'analytics': False,
            'marketing': False
        }

"""
            updated_content = updated_content[:insertion_point] + gdpr_middleware + updated_content[insertion_point:]
        
        # Write the updated file
        with open(app_file, 'w') as f:
            f.write(updated_content)
        
        logger.info(f"Successfully updated {app_file} with GDPR integration")
        return True
        
    except Exception as e:
        logger.error(f"Error updating app file: {str(e)}")
        return False

def update_layout_template():
    """Update the layout template to include GDPR consent banner"""
    try:
        # Check if layout.html exists
        layout_file = 'templates/layout.html'
        if not os.path.exists(layout_file):
            logger.error("Could not find templates/layout.html")
            return False
        
        logger.info("Updating layout.html with cookie consent banner")
        
        # Read the current file
        with open(layout_file, 'r') as f:
            content = f.read()
        
        # Create a backup
        with open(f'{layout_file}.bak', 'w') as f:
            f.write(content)
        
        # Check if consent banner is already added
        if 'cookie-consent-banner' in content:
            logger.info("Cookie consent banner already exists in layout. No changes needed.")
            return True
        
        # Find end of body tag
        body_end = content.rfind('</body>')
        
        if body_end == -1:
            logger.error("Could not find </body> tag in layout.html")
            return False
        
        # Add cookie consent banner before end of body
        cookie_banner = """
    <!-- GDPR Cookie Consent Banner -->
    <div id="cookie-consent-banner" class="cookie-banner" style="display: none;">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-lg-8">
                    <p class="mb-2 mb-lg-0">
                        We use cookies to enhance your experience. By continuing to visit this site you agree to our use of cookies.
                        <a href="{{ url_for('gdpr.cookie_policy') }}" class="text-decoration-underline">Learn more</a>
                    </p>
                </div>
                <div class="col-lg-4 text-lg-end">
                    <button id="accept-all-cookies-btn" class="btn btn-primary btn-sm me-2">Accept All</button>
                    <button id="cookie-settings-btn" class="btn btn-outline-secondary btn-sm">Cookie Settings</button>
                </div>
            </div>
        </div>
    </div>

    <!-- GDPR Cookie Banner Script -->
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Check if user has already set cookie preferences
            if (!localStorage.getItem('cookie_consent_set')) {
                // Show the consent banner
                document.getElementById('cookie-consent-banner').style.display = 'block';
            }
            
            // Accept all cookies button
            document.getElementById('accept-all-cookies-btn').addEventListener('click', function() {
                // Set all cookie types to true
                fetch('/privacy/api/cookie-preferences', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        'essential': true,
                        'functional': true,
                        'analytics': true,
                        'marketing': true
                    }),
                })
                .then(response => response.json())
                .then(data => {
                    // Hide the banner
                    document.getElementById('cookie-consent-banner').style.display = 'none';
                    
                    // Set local storage to remember consent
                    localStorage.setItem('cookie_consent_set', 'true');
                });
            });
            
            // Cookie settings button
            document.getElementById('cookie-settings-btn').addEventListener('click', function() {
                // Redirect to cookie preferences page
                window.location.href = '{{ url_for("gdpr.cookie_preferences") }}';
            });
        });
    </script>
        """
        
        updated_content = content[:body_end] + cookie_banner + content[body_end:]
        
        # Add cookie banner styles to head section
        head_end = content.find('</head>')
        
        if head_end == -1:
            logger.error("Could not find </head> tag in layout.html")
        else:
            # Add cookie banner CSS
            cookie_css = """
    <!-- Cookie Consent Banner Styles -->
    <style>
        .cookie-banner {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background-color: #f8f9fa;
            padding: 15px 0;
            box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
            z-index: 1000;
            border-top: 1px solid #dee2e6;
        }
    </style>
    """
            updated_content = updated_content[:head_end] + cookie_css + updated_content[head_end:]
        
        # Write the updated file
        with open(layout_file, 'w') as f:
            f.write(updated_content)
        
        logger.info("Successfully updated layout.html with cookie consent banner")
        return True
        
    except Exception as e:
        logger.error(f"Error updating layout template: {str(e)}")
        return False

def update_user_menu():
    """Update the user menu to include GDPR options"""
    try:
        # Check if layout.html exists
        layout_file = 'templates/layout.html'
        if not os.path.exists(layout_file):
            logger.error("Could not find templates/layout.html")
            return False
        
        # Read the current file
        with open(layout_file, 'r') as f:
            content = f.read()
        
        # Look for user dropdown menu
        dropdown_pattern = r'(dropdown-menu\s*"[^>]*>)(.*?)(</div>\s*<!--\s*end\s*dropdown-menu|\s*</ul>\s*</div>)'
        dropdown_match = re.search(dropdown_pattern, content, re.DOTALL)
        
        if not dropdown_match:
            logger.warning("Could not find user dropdown menu in layout.html")
            return False
        
        # Check if GDPR options are already added
        if 'my-data' in dropdown_match.group(2):
            logger.info("GDPR options already in user menu. No changes needed.")
            return True
        
        # Add GDPR options to dropdown menu
        dropdown_start = dropdown_match.group(1)
        dropdown_content = dropdown_match.group(2)
        dropdown_end = dropdown_match.group(3)
        
        # Find a good insertion point in the dropdown (before logout)
        logout_pos = dropdown_content.rfind('logout')
        if logout_pos == -1:
            # If logout not found, insert at the end
            insertion_point = len(dropdown_content)
        else:
            # Find the start of the line containing logout
            line_start = dropdown_content.rfind('\n', 0, logout_pos) + 1
            insertion_point = line_start
        
        # Add GDPR menu items
        gdpr_menu_items = """
                            <div class="dropdown-divider"></div>
                            <h6 class="dropdown-header">Privacy & Data</h6>
                            <a class="dropdown-item" href="{{ url_for('gdpr.my_data') }}">
                                <i class="fas fa-user-shield me-2"></i> My Data
                            </a>
                            <a class="dropdown-item" href="{{ url_for('gdpr.consent_settings') }}">
                                <i class="fas fa-sliders-h me-2"></i> Privacy Settings
                            </a>
                            """
        
        updated_dropdown = dropdown_start + dropdown_content[:insertion_point] + gdpr_menu_items + dropdown_content[insertion_point:] + dropdown_end
        
        # Replace the dropdown in the content
        updated_content = content.replace(dropdown_match.group(0), updated_dropdown)
        
        # Write the updated file
        with open(layout_file, 'w') as f:
            f.write(updated_content)
        
        logger.info("Successfully updated user menu with GDPR options")
        return True
        
    except Exception as e:
        logger.error(f"Error updating user menu: {str(e)}")
        return False

def add_footer_privacy_links():
    """Add privacy links to footer if it exists"""
    try:
        # Check if layout.html exists
        layout_file = 'templates/layout.html'
        if not os.path.exists(layout_file):
            logger.error("Could not find templates/layout.html")
            return False
        
        # Read the current file
        with open(layout_file, 'r') as f:
            content = f.read()
        
        # Look for footer section
        footer_pattern = r'<footer\s*.*?>(.*?)</footer>'
        footer_match = re.search(footer_pattern, content, re.DOTALL)
        
        if not footer_match:
            logger.warning("Could not find footer in layout.html")
            return False
        
        # Check if privacy links already exist
        if 'privacy-policy' in footer_match.group(1):
            logger.info("Privacy links already in footer. No changes needed.")
            return True
        
        # Find a good insertion point in the footer
        footer_content = footer_match.group(1)
        
        # Look for a container or row in the footer
        container_match = re.search(r'<div\s+class=".*?container.*?">', footer_content)
        if container_match:
            # Insert before the closing div of the container
            container_end = footer_content.rfind('</div>')
            if container_end != -1:
                insertion_point = container_end
            else:
                insertion_point = len(footer_content)
        else:
            # Insert at the end of the footer
            insertion_point = len(footer_content)
        
        # Add privacy links
        privacy_links = """
        <div class="row mt-3">
            <div class="col-12 text-center">
                <ul class="list-inline mb-0">
                    <li class="list-inline-item">
                        <a href="{{ url_for('gdpr.privacy_policy') }}" class="text-muted small">Privacy Policy</a>
                    </li>
                    <li class="list-inline-item">•</li>
                    <li class="list-inline-item">
                        <a href="{{ url_for('gdpr.terms_of_service') }}" class="text-muted small">Terms of Service</a>
                    </li>
                    <li class="list-inline-item">•</li>
                    <li class="list-inline-item">
                        <a href="{{ url_for('gdpr.cookie_policy') }}" class="text-muted small">Cookie Policy</a>
                    </li>
                </ul>
            </div>
        </div>
        """
        
        updated_footer = footer_content[:insertion_point] + privacy_links + footer_content[insertion_point:]
        
        # Replace the footer in the content
        updated_content = content.replace(footer_match.group(1), updated_footer)
        
        # Write the updated file
        with open(layout_file, 'w') as f:
            f.write(updated_content)
        
        logger.info("Successfully added privacy links to footer")
        return True
        
    except Exception as e:
        logger.error(f"Error adding footer privacy links: {str(e)}")
        return False

if __name__ == "__main__":
    print("Integrating GDPR routes and features into the application...")
    
    # Update main app
    if update_main_app():
        print("✓ Successfully integrated GDPR routes into main application")
    else:
        print("✗ Failed to integrate GDPR routes")
    
    # Update layout template
    if update_layout_template():
        print("✓ Successfully added cookie consent banner to layout")
    else:
        print("✗ Failed to add cookie consent banner")
    
    # Update user menu
    if update_user_menu():
        print("✓ Successfully added GDPR options to user menu")
    else:
        print("✗ Failed to add GDPR options to user menu")
    
    # Add footer privacy links
    if add_footer_privacy_links():
        print("✓ Successfully added privacy links to footer")
    else:
        print("✗ Failed to add privacy links to footer")
    
    print("\nGDPR integration complete.")
    print("Next steps:")
    print("1. Run the database migration: python run_gdpr_migration.py")
    print("2. Restart the application")
    print("3. Test the GDPR features")