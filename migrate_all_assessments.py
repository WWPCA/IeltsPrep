"""
Migrate All Assessments from practice_test to assessment table

This script migrates all available writing and speaking assessments 
to ensure users get unique content for multiple purchases.
"""

from app import app, db
from sqlalchemy import text
from datetime import datetime

def migrate_all_assessments():
    """Migrate all writing and speaking assessments from practice_test table."""
    
    with app.app_context():
        print("Starting comprehensive assessment migration...")
        
        # Get all Academic Writing tests
        academic_writing_tests = db.session.execute(text("""
            SELECT DISTINCT id, title, description 
            FROM practice_test 
            WHERE test_type = 'writing' 
            AND ielts_test_type = 'academic'
            ORDER BY id
        """)).fetchall()
        
        # Get all General Training Writing tests  
        general_writing_tests = db.session.execute(text("""
            SELECT DISTINCT id, title, description 
            FROM practice_test 
            WHERE test_type = 'writing' 
            AND ielts_test_type = 'general'
            ORDER BY id
        """)).fetchall()
        
        # Get all Academic Speaking tests
        academic_speaking_tests = db.session.execute(text("""
            SELECT DISTINCT id, title, description 
            FROM practice_test 
            WHERE test_type = 'speaking' 
            AND ielts_test_type = 'academic'
            ORDER BY id
        """)).fetchall()
        
        # Get all General Training Speaking tests
        general_speaking_tests = db.session.execute(text("""
            SELECT DISTINCT id, title, description 
            FROM practice_test 
            WHERE test_type = 'speaking' 
            AND ielts_test_type = 'general'
            ORDER BY id
        """)).fetchall()
        
        # Check what we already have
        existing_assessments = db.session.execute(text("""
            SELECT assessment_type, COUNT(*) as count
            FROM assessment 
            GROUP BY assessment_type
        """)).fetchall()
        
        print(f"\nCurrent assessment counts:")
        for assessment in existing_assessments:
            print(f"  {assessment[0]}: {assessment[1]}")
        
        print(f"\nAvailable to migrate:")
        print(f"  Academic Writing: {len(academic_writing_tests)} tests")
        print(f"  General Writing: {len(general_writing_tests)} tests")
        print(f"  Academic Speaking: {len(academic_speaking_tests)} tests")
        print(f"  General Speaking: {len(general_speaking_tests)} tests")
        
        # Migrate Academic Writing assessments
        print(f"\nMigrating {len(academic_writing_tests)} Academic Writing assessments...")
        for i, test in enumerate(academic_writing_tests, 1):
            # Check if already exists
            existing = db.session.execute(text("""
                SELECT COUNT(*) FROM assessment 
                WHERE assessment_type = 'academic_writing' 
                AND title = :title
            """), {"title": f"Academic Writing Assessment {i}"}).scalar()
            
            if existing == 0:
                db.session.execute(text("""
                    INSERT INTO assessment (title, description, assessment_type, status, creation_date)
                    VALUES (:title, :description, 'academic_writing', 'active', NOW())
                """), {
                    "title": f"Academic Writing Assessment {i}",
                    "description": f"Complete IELTS Academic Writing assessment. {test[2]} Assessed with revolutionary TrueScore® GenAI technology by Maya."
                })
                print(f"✓ Added Academic Writing Assessment {i}")
        
        # Migrate General Training Writing assessments
        print(f"\nMigrating {len(general_writing_tests)} General Training Writing assessments...")
        for i, test in enumerate(general_writing_tests, 1):
            existing = db.session.execute(text("""
                SELECT COUNT(*) FROM assessment 
                WHERE assessment_type = 'general_writing' 
                AND title = :title
            """), {"title": f"General Training Writing Assessment {i}"}).scalar()
            
            if existing == 0:
                db.session.execute(text("""
                    INSERT INTO assessment (title, description, assessment_type, status, creation_date)
                    VALUES (:title, :description, 'general_writing', 'active', NOW())
                """), {
                    "title": f"General Training Writing Assessment {i}",
                    "description": f"Complete IELTS General Training Writing assessment. {test[2]} Assessed with revolutionary TrueScore® GenAI technology by Maya."
                })
                print(f"✓ Added General Training Writing Assessment {i}")
        
        # Migrate Academic Speaking assessments
        print(f"\nMigrating {len(academic_speaking_tests)} Academic Speaking assessments...")
        for i, test in enumerate(academic_speaking_tests, 1):
            existing = db.session.execute(text("""
                SELECT COUNT(*) FROM assessment 
                WHERE assessment_type = 'academic_speaking' 
                AND title = :title
            """), {"title": f"Academic Speaking Assessment {i}"}).scalar()
            
            if existing == 0:
                db.session.execute(text("""
                    INSERT INTO assessment (title, description, assessment_type, status, creation_date)
                    VALUES (:title, :description, 'academic_speaking', 'active', NOW())
                """), {
                    "title": f"Academic Speaking Assessment {i}",
                    "description": f"Complete IELTS Academic Speaking assessment. {test[2]} Assessed with revolutionary ClearScore® conversational AI technology by Maya."
                })
                print(f"✓ Added Academic Speaking Assessment {i}")
        
        # Migrate General Training Speaking assessments
        print(f"\nMigrating {len(general_speaking_tests)} General Training Speaking assessments...")
        for i, test in enumerate(general_speaking_tests, 1):
            existing = db.session.execute(text("""
                SELECT COUNT(*) FROM assessment 
                WHERE assessment_type = 'general_speaking' 
                AND title = :title
            """), {"title": f"General Training Speaking Assessment {i}"}).scalar()
            
            if existing == 0:
                db.session.execute(text("""
                    INSERT INTO assessment (title, description, assessment_type, status, creation_date)
                    VALUES (:title, :description, 'general_speaking', 'active', NOW())
                """), {
                    "title": f"General Training Speaking Assessment {i}",
                    "description": f"Complete IELTS General Training Speaking assessment. {test[2]} Assessed with revolutionary ClearScore® conversational AI technology by Maya."
                })
                print(f"✓ Added General Training Speaking Assessment {i}")
        
        try:
            db.session.commit()
            print("\n" + "="*70)
            print("COMPREHENSIVE ASSESSMENT MIGRATION COMPLETED")
            print("="*70)
            
            # Show final counts
            final_counts = db.session.execute(text("""
                SELECT assessment_type, COUNT(*) as count
                FROM assessment 
                GROUP BY assessment_type
                ORDER BY assessment_type
            """)).fetchall()
            
            print(f"\nFinal assessment library:")
            total_assessments = 0
            for assessment in final_counts:
                count = assessment[1]
                total_assessments += count
                assessment_type = assessment[0].replace('_', ' ').title()
                print(f"  {assessment_type}: {count} assessments")
            
            print(f"\nTotal assessments available: {total_assessments}")
            print("\nUsers now get unique content with every purchase!")
            print("Multiple purchases of the same type = different questions every time")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error during migration: {e}")

if __name__ == "__main__":
    migrate_all_assessments()