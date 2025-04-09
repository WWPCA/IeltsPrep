import os
import logging
from pydub import AudioSegment
from flask import request, session
from flask_login import current_user
from models import Translation

def get_user_region():
    """
    Determine user's region based on their IP address.
    This is a simplified version. In production, you would use a GeoIP service.
    For now, we'll use a dummy implementation that checks the Accept-Language header.
    """
    # For simplicity, we're using the Accept-Language header as a proxy for region
    accept_language = request.headers.get('Accept-Language', '')
    
    # Map language codes to regions
    language_region_map = {
        'en-GB': 'UK',
        'en-US': 'US',
        'hi': 'India',
        'ur': 'Pakistan',
        'ar': 'Saudi Arabia',
        'ja': 'Japan',
        'ko': 'South Korea',
        'de': 'Germany',
        'fr': 'France',
        'nl': 'Netherlands',
        'pl': 'Poland'
    }
    
    # Extract the language code
    if accept_language:
        lang_code = accept_language.split(',')[0].strip()
        for code, region in language_region_map.items():
            if code in lang_code:
                return region
    
    # Default to US if we can't determine the region
    return 'US'

def get_translation(page, element, language=None):
    """
    Get a translation for a specific page element.
    If no translation is available, returns None.
    """
    if not language:
        # Use the user's preferred language if available
        if current_user.is_authenticated:
            language = current_user.preferred_language
        else:
            language = session.get('language', 'en')
    
    # If language is English or not specified, return None (use default text)
    if language == 'en':
        return None
    
    # Try to find the translation
    translation = Translation.query.filter_by(
        page=page, 
        element=element,
        language=language
    ).first()
    
    return translation.text if translation else None

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
