"""
Add is_admin column to User table and set admin user.
This script adds the is_admin column to support admin access to all assessment types.
"""

import sys
from app import app, db
from models import User
from sqlalchemy import text

def add_admin_column():
    """Add is_admin column to User table and set the admin user."""
    with app.app_context():
        try:
            # Check if the column already exists
            db.session.execute(text("SELECT is_admin FROM \"user\" LIMIT 1"))
            print("is_admin column already exists in the User table.")
        except Exception:
            print("Adding is_admin column to User table...")
            db.session.execute(text('ALTER TABLE "user" ADD COLUMN is_admin BOOLEAN DEFAULT FALSE'))
            db.session.commit()
            print("is_admin column added successfully.")
        
        # Set the admin user
        admin = User.query.filter_by(email='admin@ieltsaiprep.com').first()
        if admin:
            admin.is_admin = True
            db.session.commit()
            print(f"User {admin.username} (ID: {admin.id}) is now marked as admin.")
        else:
            print("Admin user not found.")

if __name__ == "__main__":
    add_admin_column()
    print("Admin column setup completed.")