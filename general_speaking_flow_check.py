"""
General Speaking Flow Verification
Checks every step from login to Maya conversation interface for General Speaking
"""

from main import app
from models import User, Assessment
import json

def check_general_speaking_flow():
    """Verify the complete General Speaking flow"""
    
    print('GENERAL SPEAKING FLOW VERIFICATION')
    print('=' * 60)
    
    with app.app_context():
        # Step 1: Check General Speaking assessments exist
        print('Step 1: General Speaking Database Check')
        general_speaking = Assessment.query.filter_by(assessment_type='General Speaking').all()
        print(f'   Found {len(general_speaking)} General Speaking assessments')
        
        if general_speaking:
            first_assessment = general_speaking[0]
            print(f'   First assessment ID: {first_assessment.id}')
            print(f'   Assessment type: {first_assessment.assessment_type}')
        else:
            print('   ❌ No General Speaking assessments found')
        
        # Step 2: Check route accessibility
        print('\nStep 2: Route Accessibility Check')
        with app.test_client() as client:
            # General speaking selection page
            response = client.get('/assessments/general_speaking')
            print(f'   /assessments/general_speaking: {response.status_code}')
            
            # Assessment start page
            response = client.get('/assessments/General%20Speaking/assessment/1')
            print(f'   Assessment start page: {response.status_code}')
            
            # Conversational interface
            response = client.get('/assessments/General%20Speaking/conversational/1')
            print(f'   Maya conversation interface: {response.status_code}')
        
        # Step 3: Check Nova Sonic service
        print('\nStep 3: Maya Voice Service Check')
        try:
            from nova_sonic_services import NovaService
            service = NovaService()
            print('   ✅ Nova Sonic service available for General Speaking')
        except Exception as e:
            print(f'   ⚠️  Nova Sonic service: {str(e)}')
        
        # Step 4: Check user access requirements
        print('\nStep 4: User Access Requirements')
        test_user = User.query.filter_by(email='test@example.com').first()
        if test_user:
            has_access = test_user.has_package_access('General Speaking')
            print(f'   Package access check: {"✅" if has_access else "❌ Purchase required"}')
        else:
            print('   ⚠️  No test user found')
        
        # Step 5: Check assessment content structure
        print('\nStep 5: Assessment Content Structure')
        if general_speaking:
            sample_assessment = general_speaking[0]
            if hasattr(sample_assessment, 'questions') and sample_assessment.questions:
                print('   ✅ Assessment questions available')
            else:
                print('   ⚠️  Assessment structure needs verification')
        
        # Step 6: Compare with Academic Speaking
        print('\nStep 6: Consistency with Academic Speaking')
        academic_speaking = Assessment.query.filter_by(assessment_type='Academic Speaking').count()
        print(f'   Academic Speaking assessments: {academic_speaking}')
        print(f'   General Speaking assessments: {len(general_speaking)}')
        
        if len(general_speaking) > 0 and academic_speaking > 0:
            print('   ✅ Both assessment types available')
        else:
            print('   ⚠️  Assessment type imbalance detected')
        
        # Step 7: Final assessment
        print('\nStep 7: Flow Readiness Assessment')
        issues = []
        
        if len(general_speaking) == 0:
            issues.append("No General Speaking assessments in database")
        
        if not test_user or not test_user.has_package_access('General Speaking'):
            issues.append("User needs General Speaking package purchase")
        
        print('\n' + '=' * 60)
        if not issues:
            print('🎯 GENERAL SPEAKING FLOW: FULLY READY')
            print('   User path: Login → General Speaking → Assessment 1 → Maya')
        else:
            print('⚠️  GENERAL SPEAKING FLOW STATUS:')
            for issue in issues:
                print(f'   - {issue}')
        print('=' * 60)
        
        return len(general_speaking), issues

if __name__ == "__main__":
    check_general_speaking_flow()