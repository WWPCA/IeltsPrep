
def convert_route_to_db_type(assessment_type):
    """Convert route parameter format to database format"""
    conversion_map = {
        'academic_speaking': 'Academic Speaking',
        'general_speaking': 'General Speaking',
        'academic_writing': 'Academic Writing', 
        'general_writing': 'General Writing'
    }
    return conversion_map.get(assessment_type, assessment_type)

def convert_db_to_package_name(assessment_type):
    """Convert database format to package name format"""
    conversion_map = {
        'Academic Speaking': 'Academic Speaking',
        'General Speaking': 'General Speaking',
        'Academic Writing': 'Academic Writing',
        'General Writing': 'General Writing'
    }
    return conversion_map.get(assessment_type, assessment_type)

def convert_route_to_package_name(assessment_type):
    """Convert route parameter directly to package name"""
    # First convert to DB format, then to package format
    db_format = convert_route_to_db_type(assessment_type)
    return convert_db_to_package_name(db_format)
