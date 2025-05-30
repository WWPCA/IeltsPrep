"""
Database Performance Optimizations
Adds missing indexes and implements query optimizations identified in the code review.
"""

import os
from sqlalchemy import text
from app import app, db

def add_database_indexes():
    """Add missing database indexes for performance optimization"""
    
    with app.app_context():
        try:
            # Add index on email field for faster user lookups
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_user_email ON "user"(email);
            """))
            
            # Add index on assessment type for faster assessment queries
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_assessment_type ON assessment(assessment_type);
            """))
            
            # Add index on user_id for faster user assessment lookups
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_user_assessment_user_id ON user_assessment_assignment(user_id);
            """))
            
            # Add index on payment records for faster payment lookups
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_payment_user_id ON payment_record(user_id);
            """))
            
            # Add index on join_date for user analytics
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_user_join_date ON user(join_date);
            """))
            
            # Add index on account_activated for quick filtering
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_user_account_activated ON user(account_activated);
            """))
            
            db.session.commit()
            print("Database indexes added successfully")
            
        except Exception as e:
            print(f"Error adding database indexes: {e}")
            db.session.rollback()

def optimize_query_patterns():
    """Implement query optimization patterns"""
    
    # This function contains optimization examples for common queries
    # These would be implemented in the actual route functions
    
    optimization_examples = {
        'user_with_assessments': """
            # Instead of N+1 queries, use joinedload
            from sqlalchemy.orm import joinedload
            
            user = User.query.options(
                joinedload(User.assessment_assignments)
            ).filter_by(email=email).first()
        """,
        
        'assessment_with_attempts': """
            # Eager load related data
            assessments = Assessment.query.options(
                joinedload(Assessment.user_attempts)
            ).filter_by(assessment_type='academic_speaking').all()
        """,
        
        'paginated_results': """
            # Use pagination for large result sets
            from flask import request
            
            page = request.args.get('page', 1, type=int)
            assessments = Assessment.query.paginate(
                page=page, per_page=20, error_out=False
            )
        """
    }
    
    print("Query optimization patterns documented")
    return optimization_examples

if __name__ == "__main__":
    add_database_indexes()
    optimize_query_patterns()