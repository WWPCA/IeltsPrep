"""
Ad Services module for the AI Learning Hub API.
Provides ad management for both web and native mobile applications.
"""
import json
import os
# Importing Flask and related modules within the same package structure to avoid import issues
from flask import jsonify

def get_web_ad_config():
    """
    Get Google Ads configuration for web applications.
    
    Returns:
        dict: Google Ads configuration
    """
    return {
        'ad_client_id': os.environ.get('GOOGLE_ADS_CLIENT_ID', 'ca-pub-YOUR-GOOGLE-ADS-CLIENT-ID'),
        'ad_slots': {
            'header': os.environ.get('GOOGLE_ADS_SLOT_HEADER', 'YOUR-AD-SLOT-ID-TOP'),
            'content': os.environ.get('GOOGLE_ADS_SLOT_CONTENT', 'YOUR-AD-SLOT-ID'),
            'footer': os.environ.get('GOOGLE_ADS_SLOT_FOOTER', 'YOUR-AD-SLOT-ID-BOTTOM')
        }
    }

def get_mobiads_config():
    """
    Get MobiAds configuration for native mobile applications.
    
    Returns:
        dict: MobiAds configuration
    """
    return {
        'api_key': os.environ.get('MOBIADS_API_KEY', 'YOUR-MOBIADS-API-KEY'),
        'publisher_id': os.environ.get('MOBIADS_PUBLISHER_ID', 'YOUR-MOBIADS-PUBLISHER-ID'),
        'ad_units': {
            'banner': os.environ.get('MOBIADS_BANNER_ID', 'mobiads-banner-unit-id'),
            'interstitial': os.environ.get('MOBIADS_INTERSTITIAL_ID', 'mobiads-interstitial-unit-id'),
            'rewarded': os.environ.get('MOBIADS_REWARDED_ID', 'mobiads-rewarded-unit-id'),
            'native': os.environ.get('MOBIADS_NATIVE_ID', 'mobiads-native-unit-id')
        },
        'test_mode': os.environ.get('MOBIADS_TEST_MODE', 'true').lower() == 'true'
    }

def get_ad_config_for_platform(platform):
    """
    Get ad configuration for the specified platform.
    
    Args:
        platform (str): 'web', 'ios', or 'android'
        
    Returns:
        dict: Ad configuration for the platform
    """
    if platform == 'web':
        return get_web_ad_config()
    elif platform in ['ios', 'android']:
        return get_mobiads_config()
    else:
        return {'error': 'Invalid platform'}

def should_show_ads(user):
    """
    Determine if ads should be shown to the user.
    Ads are only shown to non-subscribed users.
    
    Args:
        user: User object
        
    Returns:
        bool: True if ads should be shown, False otherwise
    """
    # Check if user is not subscribed
    if not user or not hasattr(user, 'is_subscribed'):
        return True
    return not user.is_subscribed()

def user_ad_preferences(user_id):
    """
    Get user-specific ad preferences.
    
    Args:
        user_id (int): User ID
        
    Returns:
        dict: User ad preferences
    """
    # This could be expanded to include user preferences from a database
    return {
        'personalized_ads': True,
        'ad_categories': {
            'education': True,
            'language_learning': True,
            'test_preparation': True
        }
    }