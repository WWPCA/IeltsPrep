"""
Add Writing Assessments to Database

This script adds writing assessments to match the speaking assessment structure.
Creates both Academic Writing and General Training Writing assessments.
"""

from app import app, db
from models import Assessment
from datetime import datetime

def add_writing_assessments():
    """Add writing assessments to the database."""
    
    with app.app_context():
        print("Adding writing assessments to the database...")
        
        # Academic Writing Assessments
        academic_writing_assessments = [
            {
                'title': 'Academic Writing Assessment 1',
                'description': 'Complete IELTS Academic Writing assessment with Task 1 (graph/chart description) and Task 2 (essay). Assessed with revolutionary TrueScore® GenAI technology.',
                'assessment_type': 'academic_writing'
            },
            {
                'title': 'Academic Writing Assessment 2', 
                'description': 'Complete IELTS Academic Writing assessment with Task 1 (graph/chart description) and Task 2 (essay). Assessed with revolutionary TrueScore® GenAI technology.',
                'assessment_type': 'academic_writing'
            },
            {
                'title': 'Academic Writing Assessment 3',
                'description': 'Complete IELTS Academic Writing assessment with Task 1 (graph/chart description) and Task 2 (essay). Assessed with revolutionary TrueScore® GenAI technology.',
                'assessment_type': 'academic_writing'
            },
            {
                'title': 'Academic Writing Assessment 4',
                'description': 'Complete IELTS Academic Writing assessment with Task 1 (graph/chart description) and Task 2 (essay). Assessed with revolutionary TrueScore® GenAI technology.',
                'assessment_type': 'academic_writing'
            }
        ]
        
        # General Training Writing Assessments
        general_writing_assessments = [
            {
                'title': 'General Training Writing Assessment 1',
                'description': 'Complete IELTS General Training Writing assessment with Task 1 (formal/informal letters) and Task 2 (essay). Assessed with revolutionary TrueScore® GenAI technology.',
                'assessment_type': 'general_writing'
            },
            {
                'title': 'General Training Writing Assessment 2',
                'description': 'Complete IELTS General Training Writing assessment with Task 1 (formal/informal letters) and Task 2 (essay). Assessed with revolutionary TrueScore® GenAI technology.',
                'assessment_type': 'general_writing'
            },
            {
                'title': 'General Training Writing Assessment 3',
                'description': 'Complete IELTS General Training Writing assessment with Task 1 (formal/informal letters) and Task 2 (essay). Assessed with revolutionary TrueScore® GenAI technology.',
                'assessment_type': 'general_writing'
            },
            {
                'title': 'General Training Writing Assessment 4',
                'description': 'Complete IELTS General Training Writing assessment with Task 1 (formal/informal letters) and Task 2 (essay). Assessed with revolutionary TrueScore® GenAI technology.',
                'assessment_type': 'general_writing'
            }
        ]
        
        # Combine all assessments
        all_assessments = academic_writing_assessments + general_writing_assessments
        
        # Add assessments to database
        for assessment_data in all_assessments:
            # Check if assessment already exists
            existing = Assessment.query.filter_by(
                title=assessment_data['title'],
                assessment_type=assessment_data['assessment_type']
            ).first()
            
            if not existing:
                assessment = Assessment(
                    title=assessment_data['title'],
                    description=assessment_data['description'],
                    assessment_type=assessment_data['assessment_type'],
                    status='active',
                    created_at=datetime.utcnow()
                )
                db.session.add(assessment)
                print(f"✓ Added: {assessment_data['title']}")
            else:
                print(f"- Already exists: {assessment_data['title']}")
        
        try:
            db.session.commit()
            print("\n" + "="*60)
            print("WRITING ASSESSMENTS ADDED SUCCESSFULLY")
            print("="*60)
            
            # Verify what we have now
            academic_count = Assessment.query.filter_by(assessment_type='academic_writing').count()
            general_count = Assessment.query.filter_by(assessment_type='general_writing').count()
            
            print(f"Academic Writing assessments: {academic_count}")
            print(f"General Training Writing assessments: {general_count}")
            
            print("\nUsers can now purchase and access:")
            print("- Academic Writing packages (4 assessments available)")
            print("- General Writing packages (4 assessments available)")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error adding assessments: {e}")

if __name__ == "__main__":
    add_writing_assessments()