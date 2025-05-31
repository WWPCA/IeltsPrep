"""
Assessment Type Converters
Handles conversion between different assessment type formats used throughout the application.
"""

def convert_route_to_db_type(assessment_type):
    """
    Convert route parameter format to database format.
    
    Route URLs use underscore format (academic_speaking) while database
    uses space format (Academic Speaking).
    
    Args:
        assessment_type (str): Route parameter like 'academic_speaking'
        
    Returns:
        str: Database format like 'Academic Speaking'
    """
    conversion_map = {
        'academic_speaking': 'Academic Speaking',
        'general_speaking': 'General Speaking',
        'academic_writing': 'Academic Writing', 
        'general_writing': 'General Writing'
    }
    return conversion_map.get(assessment_type, assessment_type)

def convert_db_to_package_name(assessment_type):
    """
    Convert database format to package name format.
    
    After the database fix, both formats are the same.
    
    Args:
        assessment_type (str): Database format like 'Academic Speaking'
        
    Returns:
        str: Package name format (same as database format)
    """
    return assessment_type

def convert_route_to_package_name(assessment_type):
    """
    Convert route parameter directly to package name format.
    
    Args:
        assessment_type (str): Route parameter like 'academic_speaking'
        
    Returns:
        str: Package name like 'Academic Speaking'
    """
    return convert_route_to_db_type(assessment_type)

def get_all_assessment_types():
    """
    Get all valid assessment types in database format.
    
    Returns:
        list: All 4 assessment type names as stored in database
    """
    return [
        'Academic Speaking',
        'Academic Writing',
        'General Speaking', 
        'General Writing'
    ]

def get_all_route_types():
    """
    Get all valid assessment types in route format.
    
    Returns:
        list: All 4 assessment type names as used in URLs
    """
    return [
        'academic_speaking',
        'academic_writing',
        'general_speaking',
        'general_writing'
    ]

def is_valid_assessment_type(assessment_type, format_type='route'):
    """
    Check if an assessment type is valid.
    
    Args:
        assessment_type (str): The assessment type to validate
        format_type (str): Either 'route' or 'db' to specify expected format
        
    Returns:
        bool: True if the assessment type is valid
    """
    if format_type == 'route':
        return assessment_type in get_all_route_types()
    elif format_type == 'db':
        return assessment_type in get_all_assessment_types()
    else:
        return False