"""
Assessment Type Converters
Provides conversion functions between different assessment type formats
"""

def convert_route_to_db_type(route_type):
    """Convert route assessment type to database format"""
    conversions = {
        'academic_speaking': 'Academic Speaking',
        'general_speaking': 'General Speaking', 
        'academic_writing': 'Academic Writing',
        'general_writing': 'General Writing'
    }
    return conversions.get(route_type, route_type)

def convert_db_to_route_type(db_type):
    """Convert database assessment type to route format"""
    conversions = {
        'Academic Speaking': 'academic_speaking',
        'General Speaking': 'general_speaking',
        'Academic Writing': 'academic_writing', 
        'General Writing': 'general_writing'
    }
    return conversions.get(db_type, db_type.lower().replace(' ', '_'))

def get_assessment_category(assessment_type):
    """Get the category (academic/general) from assessment type"""
    if 'academic' in assessment_type.lower():
        return 'academic'
    elif 'general' in assessment_type.lower():
        return 'general'
    return 'unknown'

def get_skill_type(assessment_type):
    """Get the skill type (speaking/writing) from assessment type"""
    if 'speaking' in assessment_type.lower():
        return 'speaking'
    elif 'writing' in assessment_type.lower():
        return 'writing'
    return 'unknown'

def is_valid_assessment_type(assessment_type):
    """Check if assessment type is valid"""
    valid_types = [
        'academic_speaking', 'general_speaking',
        'academic_writing', 'general_writing',
        'Academic Speaking', 'General Speaking',
        'Academic Writing', 'General Writing'
    ]
    return assessment_type in valid_types