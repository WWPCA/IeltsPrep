#!/usr/bin/env python3
"""
Fix Route Accessibility

This script addresses issues with route accessibility by ensuring that the necessary
routes are properly defined and registered, particularly the assessment_products_page route.
"""

import logging
import os
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("fix_routes")

def fix_assessment_structure_routes():
    """Fix assessment structure routes by ensuring they're properly included in main.py"""
    logger.info("Checking assessment structure routes...")
    
    main_py_path = "main.py"
    
    # Check if assessment_structure_routes is properly imported
    with open(main_py_path, 'r') as f:
        content = f.read()
    
    if "import assessment_structure_routes" in content:
        logger.info("Assessment structure routes are properly imported")
        return
    
    logger.warning("Assessment structure routes not properly imported, fixing...")
    lines = content.splitlines()
    
    insert_index = -1
    for i, line in enumerate(lines):
        if "import " in line and "routes" in line:
            insert_index = i + 1
    
    if insert_index >= 0:
        lines.insert(insert_index, "import assessment_structure_routes  # noqa: F401")
        
        with open(main_py_path, 'w') as f:
            f.write('\n'.join(lines))
        logger.info("Fixed assessment structure routes import")
    else:
        logger.error("Could not locate appropriate position to insert import")

def fix_assessment_route_import():
    """Fix circular imports between main, assessment_routes and add_assessment_routes"""
    logger.info("Checking for assessment route imports...")
    
    # Check if the assessment routes have circular imports
    assessment_routes_path = "assessment_routes.py"
    if os.path.exists(assessment_routes_path):
        with open(assessment_routes_path, 'r') as f:
            content = f.read()
        
        if "from main import app" in content:
            logger.warning("Circular import detected in assessment_routes.py, fixing...")
            content = content.replace("from main import app", "from app import app")
            
            with open(assessment_routes_path, 'w') as f:
                f.write(content)
            logger.info("Fixed circular import in assessment_routes.py")
    
    # Check add_assessment_routes.py for proper imports
    add_assessment_routes_path = "add_assessment_routes.py"
    if os.path.exists(add_assessment_routes_path):
        with open(add_assessment_routes_path, 'r') as f:
            content = f.read()
        
        # Make sure the correct imports are present
        if "from flask import Flask" not in content:
            logger.warning("Missing proper imports in add_assessment_routes.py, fixing...")
            
            # Find the imports section
            import_lines = []
            other_lines = []
            in_imports = True
            
            for line in content.splitlines():
                if line.strip() == '' and in_imports and import_lines:
                    in_imports = False
                
                if in_imports and (line.startswith('import ') or line.startswith('from ')):
                    import_lines.append(line)
                else:
                    other_lines.append(line)
            
            # Add the necessary imports
            needed_imports = [
                "from flask import Flask, render_template, request, redirect, url_for, flash, session, current_app, jsonify"
            ]
            
            for imp in needed_imports:
                if imp not in import_lines:
                    import_lines.append(imp)
            
            # Reconstruct the file
            updated_content = '\n'.join(import_lines + [''] + other_lines)
            
            with open(add_assessment_routes_path, 'w') as f:
                f.write(updated_content)
            logger.info("Fixed imports in add_assessment_routes.py")

def fix_assessment_routes_module():
    """Ensure assessment routes module is properly setup"""
    logger.info("Checking assessment routes module...")
    
    # Make sure assessment_routes.py exists and has the basic structure
    assessment_routes_path = "assessment_routes.py"
    if not os.path.exists(assessment_routes_path):
        logger.warning("assessment_routes.py not found, creating it...")
        
        with open(assessment_routes_path, 'w') as f:
            f.write('''"""
Assessment Routes Module

This module provides the main routes for handling IELTS GenAI Assessments.
It defines the index, listings, and common functionality for all assessment types.
"""

from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, request, flash, session, abort, jsonify
from flask_login import login_required, current_user
import json
import logging

from app import app
from models import db, Assessment, UserAssessmentAttempt
from account_activation import authenticated_user_required


@app.route('/assessments')
@login_required
def assessment_index():
    """Display the main assessment landing page."""
    # Check if user has an active assessment package
    has_package = current_user.has_active_assessment_package()
    
    # Get user's assessment preference (academic or general)
    assessment_type = current_user.assessment_preference
    
    return render_template('assessments/index.html',
                         title='IELTS GenAI Assessments',
                         has_package=has_package,
                         assessment_type=assessment_type)
''')
        logger.info("Created basic assessment_routes.py file")

def ensure_assessment_products_route():
    """Make sure the assessment products route is properly defined in add_assessment_routes.py"""
    logger.info("Ensuring assessment products route is accessible...")
    
    add_assessment_routes_path = "add_assessment_routes.py"
    if os.path.exists(add_assessment_routes_path):
        with open(add_assessment_routes_path, 'r') as f:
            content = f.read()
        
        if "@app.route('/assessment-products')" in content:
            logger.info("Assessment products route is properly defined")
        else:
            logger.warning("Assessment products route not found or not properly defined")
            
            # Check if the function is defined correctly
            if "def assessment_products_page():" in content and "@app.route" not in content:
                logger.warning("Function exists but route decorator is missing, fixing...")
                
                # Add the decorator
                content = content.replace(
                    "def assessment_products_page():", 
                    "@app.route('/assessment-products')\ndef assessment_products_page():"
                )
                
                with open(add_assessment_routes_path, 'w') as f:
                    f.write(content)
                logger.info("Added route decorator to assessment_products_page")

def main():
    """Main function to fix route accessibility issues"""
    logger.info("Starting route accessibility fixes...")
    
    # Fix assessment structure routes
    fix_assessment_structure_routes()
    
    # Fix assessment route import issues
    fix_assessment_route_import()
    
    # Ensure assessment routes module is properly setup
    fix_assessment_routes_module()
    
    # Make sure assessment products route is properly defined
    ensure_assessment_products_route()
    
    logger.info("Completed route accessibility fixes")

if __name__ == "__main__":
    main()