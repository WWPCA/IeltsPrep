import os
import logging
from pydub import AudioSegment
from flask import request, session
from flask_login import current_user
from models import Translation

def get_user_region(request_obj=None):
    """
    Determine user's region based on their IP address.
    This is a simplified version. In production, you would use a GeoIP service.
    For now, we'll use a dummy implementation that checks the Accept-Language header.
    
    Args:
        request_obj: Flask request object (optional, uses global request if not provided)
    """
    if request_obj is None:
        request_obj = request
    # If user is authenticated and has a region set, use that
    if current_user.is_authenticated and current_user.region:
        return current_user.region
    
    # For simplicity, we're using the Accept-Language header as a proxy for region
    accept_language = request_obj.headers.get('Accept-Language', '')
    
    # Map language codes to regions for payment methods
    language_region_map = {
        # South Asia
        'hi': 'India',
        'ur': 'Pakistan',
        'bn': 'Bangladesh',
        'si': 'Sri Lanka',
        'ne': 'Nepal',
        
        # East Asia & Middle East
        'ja': 'Japan',
        'ko': 'South Korea',
        'ar-SA': 'Saudi Arabia',
        'ar-AE': 'UAE',
        'ar': 'UAE',  # Default Arabic to UAE
        
        # Europe
        'pl': 'Poland',
        'nl': 'Netherlands',
        'de': 'Germany',
        'fr': 'France',
        'ru': 'Eastern Europe',
        'uk': 'Eastern Europe',
        'cs': 'Eastern Europe',
        'sk': 'Eastern Europe',
        'hu': 'Eastern Europe',
        'ro': 'Eastern Europe',
        'bg': 'Eastern Europe',
        
        # English-speaking countries (default)
        'en-GB': 'UK',
        'en-US': 'US',
        'en-CA': 'Canada',
        'en-AU': 'Australia',
        'en-NZ': 'New Zealand'
    }
    
    # Extract the language code
    if accept_language:
        lang_code = accept_language.split(',')[0].strip()
        # Try exact match first
        if lang_code in language_region_map:
            return language_region_map[lang_code]
        
        # Try prefix match
        for code, region in language_region_map.items():
            if lang_code.startswith(code) or code in lang_code:
                return region
    
    # Get region from geolocation using IP (in a real app)
    # This is a placeholder for a real IP-based geolocation service
    # In a production app, you would integrate with a service like MaxMind GeoIP or similar
    
    # Default to US if we can't determine the region
    return 'US'

def get_translation(page, element, language=None):
    """
    Get a translation for a specific page element.
    If no translation is available, returns None.
    
    Note: App is only available in English, so this always returns None.
    """
    # App is only available in English
    return None

def compress_audio(audio_path, target_bitrate="64k"):
    """
    Compress an audio file to reduce its size for low-bandwidth environments.
    
    Args:
        audio_path (str): Path to the audio file
        target_bitrate (str): Target bitrate for compression (e.g., "64k")
    
    Returns:
        str: Path to the compressed audio file
    """
    try:
        # Load the audio file
        audio = AudioSegment.from_file(audio_path)
        
        # Create a new filename for the compressed version
        filename, ext = os.path.splitext(audio_path)
        compressed_path = f"{filename}_compressed{ext}"
        
        # Export with reduced bitrate
        audio.export(compressed_path, format="mp3", bitrate=target_bitrate)
        
        logging.info(f"Compressed audio file: {audio_path} -> {compressed_path}")
        return compressed_path
    
    except Exception as e:
        logging.error(f"Error compressing audio: {str(e)}")
        # Return the original path if compression fails
        return audio_path
