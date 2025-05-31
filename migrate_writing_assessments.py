"""
Migrate Writing Assessments from practice_test to assessment table

This script converts existing writing tests from the practice_test table 
to proper assessments in the assessment table with correct naming conventions.
"""

from app import app, db
from models import Assessment
from datetime import datetime

def migrate_writing_assessments():
    """Migrate writing assessments from practice_test to assessment table."""
    
    with app.app_context():
        print("Migrating writing assessments from practice_test table...")
        
        # Get Academic Writing tests
        print("\nProcessing Academic Writing tests...")
        academic_tests = db.session.execute("""
            SELECT id, title, description 
            FROM practice_test 
            WHERE test_type = 'writing' 
            AND ielts_test_type = 'academic'
            AND title LIKE '%Academic Writing Test%'
            ORDER BY id 
            LIMIT 4
        """).fetchall()
        
        # Get General Training Writing tests  
        print("Processing General Training Writing tests...")
        general_tests = db.session.execute("""
            SELECT id, title, description 
            FROM practice_test 
            WHERE test_type = 'writing' 
            AND ielts_test_type = 'general'
            AND title LIKE '%General Training Writing Test%'
            ORDER BY id 
            LIMIT 4
        """).fetchall()
        
        # Convert Academic tests
        for i, test in enumerate(academic_tests, 1):
            assessment_title = f"Academic Writing Assessment {i}"
            assessment_description = f"Complete IELTS Academic Writing assessment with Task 1 (graph/chart description) and Task 2 (essay). Assessed with revolutionary TrueScore® GenAI technology. {test[2]}"
            
            # Check if already exists
            existing = Assessment.query.filter_by(
                title=assessment_title,
                assessment_type='academic_writing'
            ).first()
            
            if not existing:
                assessment = Assessment(
                    title=assessment_title,
                    description=assessment_description,
                    assessment_type='academic_writing',
                    status='active',
                    created_at=datetime.utcnow()
                )
                db.session.add(assessment)
                print(f"✓ Added: {assessment_title}")
            else:
                print(f"- Already exists: {assessment_title}")
        
        # Convert General Training tests
        for i, test in enumerate(general_tests, 1):
            assessment_title = f"General Training Writing Assessment {i}"
            assessment_description = f"Complete IELTS General Training Writing assessment with Task 1 (formal/informal letters) and Task 2 (essay). Assessed with revolutionary TrueScore® GenAI technology. {test[2]}"
            
            # Check if already exists
            existing = Assessment.query.filter_by(
                title=assessment_title,
                assessment_type='general_writing'
            ).first()
            
            if not existing:
                assessment = Assessment(
                    title=assessment_title,
                    description=assessment_description,
                    assessment_type='general_writing',
                    status='active',
                    created_at=datetime.utcnow()
                )
                db.session.add(assessment)
                print(f"✓ Added: {assessment_title}")
            else:
                print(f"- Already exists: {assessment_title}")
        
        try:
            db.session.commit()
            print("\n" + "="*60)
            print("WRITING ASSESSMENT MIGRATION COMPLETED")
            print("="*60)
            
            # Verify final state
            all_assessments = Assessment.query.all()
            academic_speaking = len([a for a in all_assessments if a.assessment_type == 'academic_speaking'])
            general_speaking = len([a for a in all_assessments if a.assessment_type == 'general_speaking'])
            academic_writing = len([a for a in all_assessments if a.assessment_type == 'academic_writing'])
            general_writing = len([a for a in all_assessments if a.assessment_type == 'general_writing'])
            
            print(f"Final assessment counts:")
            print(f"  Academic Speaking: {academic_speaking}")
            print(f"  General Speaking: {general_speaking}")  
            print(f"  Academic Writing: {academic_writing}")
            print(f"  General Writing: {general_writing}")
            
            print("\nUsers can now purchase and access:")
            print("- Academic Speaking packages (4 assessments)")
            print("- General Speaking packages (2 assessments)")
            print("- Academic Writing packages (4 assessments)")
            print("- General Writing packages (4 assessments)")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error during migration: {e}")

if __name__ == "__main__":
    migrate_writing_assessments()