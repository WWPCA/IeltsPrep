"""
Create an admin user for accessing the admin dashboard.
This script creates a new admin user or elevates an existing user to admin status.
"""

from flask import Flask
from werkzeug.security import generate_password_hash
from app import db
from models import User
import sys

def create_admin_user(username, email, password):
    """
    Create a new admin user or update an existing user to have admin privileges.
    
    Args:
        username (str): Admin username
        email (str): Admin email
        password (str): Admin password
        
    Returns:
        User: The created or updated admin user
    """
    # Check if the user already exists
    user = User.query.filter(User.username == username).first()
    
    if user:
        print(f"User '{username}' already exists. Updating to admin status.")
        user.is_admin = True
        user.password_hash = generate_password_hash(password)
    else:
        print(f"Creating new admin user '{username}'.")
        # Create a new user with admin privileges
        user = User(
            username=username,
            email=email,
            subscription_status="Value Pack",  # Give admin full subscription access
            is_admin=True
        )
        user.set_password(password)
        db.session.add(user)
    
    # Save changes
    db.session.commit()
    
    print(f"Admin user '{username}' created/updated successfully!")
    return user

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python create_admin_user.py <username> <email> <password>")
        sys.exit(1)
    
    username = sys.argv[1]
    email = sys.argv[2]
    password = sys.argv[3]
    
    # Create Flask app context
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///instance/app.db"
    
    with app.app_context():
        create_admin_user(username, email, password)