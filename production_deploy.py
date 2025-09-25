#!/usr/bin/env python3
"""
Deploy production-ready IELTS GenAI Prep code to GitHub production repository
https://github.com/WWPCA/IELTS-Web-Platform
"""

import os
import subprocess
import shutil
import json
from datetime import datetime

def run_command(cmd, cwd=None):
    """Run shell command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Command failed: {cmd}")
            print(f"Error: {result.stderr}")
            return False, result.stderr
        return True, result.stdout
    except Exception as e:
        print(f"Command exception: {e}")
        return False, str(e)

def clone_production_repo():
    """Clone the production repository"""
    repo_url = "https://github.com/WWPCA/IELTS-Web-Platform.git"
    
    # Remove existing clone if present
    if os.path.exists("IELTS-Web-Platform"):
        shutil.rmtree("IELTS-Web-Platform")
    
    success, output = run_command(f"git clone {repo_url}")
    if not success:
        print(f"Failed to clone repository: {output}")
        return False
    
    return True

def update_production_files():
    """Update production repository with current preview code"""
    try:
        # Create updated app.py for production
        production_dir = "IELTS-Web-Platform/IELTS-Web-Platform/lambda_functions"
        
        # Copy production app.py
        shutil.copy2("production_code/app.py", f"{production_dir}/main_handler.py")
        
        # Copy HTML templates to src/pages
        pages_dir = "IELTS-Web-Platform/IELTS-Web-Platform/src/pages"
        os.makedirs(pages_dir, exist_ok=True)
        
        # Copy all the active templates
        template_files = [
            "working_template_backup_20250714_192410.html",
            "mobile_registration_flow.html", 
            "test_mobile_home_screen.html",
            "test_maya_voice.html",
            "database_schema_demo.html",
            "nova_assessment_demo.html"
        ]
        
        for template in template_files:
            if os.path.exists(f"production_code/{template}"):
                shutil.copy2(f"production_code/{template}", f"{pages_dir}/{template}")
        
        # Update requirements.txt
        shutil.copy2("production_code/requirements.txt", "IELTS-Web-Platform/IELTS-Web-Platform/requirements.txt")
        
        # Copy robots.txt if it exists
        if os.path.exists("production_code/robots.txt"):
            shutil.copy2("production_code/robots.txt", "IELTS-Web-Platform/IELTS-Web-Platform/robots.txt")
        
        return True
        
    except Exception as e:
        print(f"Failed to update production files: {e}")
        return False

def commit_and_push():
    """Commit and push changes to production repository"""
    repo_dir = "IELTS-Web-Platform"
    
    # Configure git
    run_command("git config user.name 'IELTS AI Prep CI'", cwd=repo_dir)
    run_command("git config user.email 'ci@ieltsaiprep.com'", cwd=repo_dir)
    
    # Add all changes
    success, output = run_command("git add .", cwd=repo_dir)
    if not success:
        print(f"Failed to add files: {output}")
        return False
    
    # Check if there are changes to commit
    success, output = run_command("git status --porcelain", cwd=repo_dir)
    if not success or not output.strip():
        print("No changes to commit")
        return True
    
    # Commit changes
    commit_message = f"Update production code with current preview templates - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC"
    success, output = run_command(f'git commit -m "{commit_message}"', cwd=repo_dir)
    if not success:
        print(f"Failed to commit: {output}")
        return False
    
    # Push changes
    success, output = run_command("git push origin main", cwd=repo_dir)
    if not success:
        print(f"Failed to push: {output}")
        return False
    
    print("Successfully pushed production code to GitHub")
    return True

def main():
    """Main deployment function"""
    print("Starting production deployment...")
    
    if not clone_production_repo():
        return False
    
    if not update_production_files():
        return False
    
    if not commit_and_push():
        return False
    
    print("Production deployment completed successfully!")
    return True

if __name__ == "__main__":
    main()