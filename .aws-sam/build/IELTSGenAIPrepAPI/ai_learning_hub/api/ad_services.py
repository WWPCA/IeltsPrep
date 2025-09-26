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
        'ad_client_id': os.environ.get('GOOGLE_ADS_CLIENT_ID', 'ca-pub-1234567890123456'),
        'ad_slots': {
            'header': os.environ.get('GOOGLE_ADS_SLOT_HEADER', '2345678901'),
            'content': os.environ.get('GOOGLE_ADS_SLOT_CONTENT', '1234567890'),
            'footer': os.environ.get('GOOGLE_ADS_SLOT_FOOTER', '3456789012')
        },
        'page_level_ads': True,
        'auto_ads': {
            'enabled': True,
            'format_filter': ['banner', 'in-article', 'in-feed']
        },
        'ad_frequency': {
            'article_body': 3,  # Insert ad after every 3 paragraphs
            'content_listing': 5  # Insert ad after every 5 list items
        },
        'responsive_sizing': True
    }

def get_mobiads_config():
    """
    Get MobiAds configuration for native mobile applications.
    
    Returns:
        dict: MobiAds configuration
    """
    return {
        'api_key': os.environ.get('MOBIADS_API_KEY', 'mobiads-api-key-12345'),
        'publisher_id': os.environ.get('MOBIADS_PUBLISHER_ID', 'pub-5678901234'),
        'ad_units': {
            'banner': os.environ.get('MOBIADS_BANNER_ID', 'mobiads-banner-9876543210'),
            'interstitial': os.environ.get('MOBIADS_INTERSTITIAL_ID', 'mobiads-interstitial-8765432109'),
            'rewarded': os.environ.get('MOBIADS_REWARDED_ID', 'mobiads-rewarded-7654321098'),
            'native': os.environ.get('MOBIADS_NATIVE_ID', 'mobiads-native-6543210987')
        },
        'mediation_config': {
            'enabled': True,
            'networks': ['mobiads', 'admob', 'facebook', 'unity'],
            'refresh_rate': 60,  # seconds
            'timeout': 30,  # seconds
            'priority_order': ['admob', 'facebook', 'unity', 'mobiads']
        },
        'placements': {
            'app_launch': {
                'type': 'interstitial',
                'frequency': 3,  # Show every 3 launches
                'cooldown': 60   # Minimum 60 seconds between interstitials
            },
            'main_screen': {
                'type': 'banner',
                'position': 'bottom'
            },
            'course_listing': {
                'type': 'native',
                'position': 'inline',
                'frequency': 4    # Show after every 4 courses
            },
            'content_completion': {
                'type': 'rewarded',
                'reward': {'type': 'points', 'amount': 10}
            }
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
    Ads are only shown to users without active assessment packages.
    
    Args:
        user: User object
        
    Returns:
        bool: True if ads should be shown, False otherwise
    """
    # Check if user has an active assessment package
    if not user or not hasattr(user, 'has_active_assessment_package'):
        return True
    return not user.has_active_assessment_package()

def user_ad_preferences(user_id):
    """
    Get user-specific ad preferences.
    
    Args:
        user_id (int): User ID
        
    Returns:
        dict: User ad preferences
    """
    # This would normally be retrieved from the database for each user
    # For now, we're providing a comprehensive default configuration
    return {
        'personalized_ads': True,
        'ad_categories': {
            'education': True,
            'language_learning': True,
            'test_preparation': True,
            'productivity': True,
            'technology': True,
            'travel': False,
            'gaming': False,
            'finance': False
        },
        'ad_formats': {
            'banner': True,
            'interstitial': True,
            'rewarded': True,
            'native': True,
            'video': True
        },
        'frequency_settings': {
            'max_ads_per_session': 10,
            'min_time_between_interstitials': 120,  # seconds
            'session_start_delay': 30  # seconds before showing first ad
        },
        'ad_networks': {
            'mobiads': True,
            'admob': True,
            'facebook': True,
            'unity': True
        },
        'privacy_settings': {
            'location_based': False,
            'interest_based': True,
            'demographic_based': True,
            'behavior_based': True
        },
        'rewarded_incentives': {
            'enabled': True,
            'preferred_rewards': ['premium_content', 'points', 'badges']
        }
    }