"""
Create UserPackage table to handle multiple individual assessment packages per user.
This replaces the single assessment_package_status field with a proper relational approach.
"""
from app import app, db
from models import User
from datetime import datetime

def create_user_packages_table():
    """Create UserPackage table for tracking individual package purchases."""
    
    # Create the UserPackage table
    db.engine.execute("""
        CREATE TABLE IF NOT EXISTS user_package (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
            package_name VARCHAR(50) NOT NULL,
            purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expiry_date TIMESTAMP,
            status VARCHAR(20) DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, package_name)
        );
    """)
    
    # Create indexes for performance
    db.engine.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_package_user_id ON user_package(user_id);
        CREATE INDEX IF NOT EXISTS idx_user_package_status ON user_package(status);
        CREATE INDEX IF NOT EXISTS idx_user_package_expiry ON user_package(expiry_date);
    """)
    
    print("UserPackage table created successfully")

def migrate_existing_users():
    """Migrate existing users with assessment packages to the new table."""
    
    with app.app_context():
        users = User.query.filter(
            User.assessment_package_status.notin_(['none', 'expired'])
        ).all()
        
        for user in users:
            # Skip if user already has packages in new table
            existing_count = db.engine.execute(
                "SELECT COUNT(*) FROM user_package WHERE user_id = %s", 
                (user.id,)
            ).scalar()
            
            if existing_count > 0:
                continue
                
            package_status = user.assessment_package_status
            
            if package_status == "All Products":
                # Convert "All Products" to individual packages
                packages = [
                    "Academic Writing",
                    "Academic Speaking", 
                    "General Writing",
                    "General Speaking"
                ]
            else:
                # Single package
                packages = [package_status]
            
            # Insert packages for this user
            for package in packages:
                db.engine.execute("""
                    INSERT INTO user_package (user_id, package_name, expiry_date)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (user_id, package_name) DO NOTHING
                """, (user.id, package, user.assessment_package_expiry))
            
            print(f"Migrated user {user.id} with packages: {packages}")

if __name__ == "__main__":
    with app.app_context():
        create_user_packages_table()
        migrate_existing_users()
        print("Migration completed successfully")