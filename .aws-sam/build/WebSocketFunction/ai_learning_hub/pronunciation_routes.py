"""
Routes for the pronunciation coach feature of the AI Learning Hub
"""
import os
import json
import uuid
import logging
from flask import Blueprint, render_template, request, jsonify, current_app
from werkzeug.utils import secure_filename
import aws_services

# Create a blueprint for the pronunciation coach
pronunciation_bp = Blueprint('pronunciation', __name__, url_prefix='/ai-learning-hub')

# Ensure upload directories exist
def ensure_dirs_exist():
    """Ensure the necessary directories exist"""
    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'audio')
    tts_dir = os.path.join(current_app.root_path, 'static', 'audio', 'tts')
    
    os.makedirs(upload_dir, exist_ok=True)
    os.makedirs(tts_dir, exist_ok=True)
    
    return upload_dir, tts_dir

@pronunciation_bp.route('/pronunciation-coach')
def pronunciation_coach():
    """
    Display the pronunciation coach interface
    """
    return render_template('pronunciation_coach.html')

@pronunciation_bp.route('/pronunciation-exercises')
def get_pronunciation_exercises():
    """
    Get pronunciation exercises based on difficulty and category
    """
    try:
        # Get parameters
        difficulty = request.args.get('difficulty', 'medium')
        category = request.args.get('category', 'general')
        
        # Get exercises from the AWS services module
        exercises = aws_services.generate_pronunciation_exercises(difficulty, category)
        
        # Return JSON response
        return jsonify({
            'success': True,
            'exercises': exercises
        })
    except Exception as e:
        logging.error(f"Error getting pronunciation exercises: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to load pronunciation exercises'
        }), 500

@pronunciation_bp.route('/generate-speech', methods=['POST'])
def generate_speech():
    """
    Generate speech from text using AWS Polly
    """
    try:
        # Get parameters
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing text parameter'
            }), 400
        
        text = data['text']
        
        # Create a unique filename
        _, tts_dir = ensure_dirs_exist()
        filename = f"tts_{uuid.uuid4()}.mp3"
        output_path = os.path.join(tts_dir, filename)
        
        # Generate speech using AWS Polly
        success = aws_services.generate_polly_speech(text, output_path)
        
        if success:
            # Return the URL to the generated audio
            audio_url = f"/static/audio/tts/{filename}"
            return jsonify({
                'success': True,
                'audio_url': audio_url
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to generate speech'
            }), 500
    except Exception as e:
        logging.error(f"Error generating speech: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate speech'
        }), 500

@pronunciation_bp.route('/analyze-pronunciation', methods=['POST'])
def analyze_pronunciation():
    """
    Analyze pronunciation from uploaded audio
    """
    try:
        # Check if audio file was uploaded
        if 'audio' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No audio file provided'
            }), 400
        
        audio_file = request.files['audio']
        reference_text = request.form.get('reference_text', '')
        
        if not reference_text:
            return jsonify({
                'success': False,
                'error': 'No reference text provided'
            }), 400
        
        # Save the uploaded audio file
        upload_dir, _ = ensure_dirs_exist()
        filename = f"recording_{uuid.uuid4()}.webm"
        file_path = os.path.join(upload_dir, filename)
        audio_file.save(file_path)
        
        # Transcribe the audio using AWS Transcribe
        transcription = aws_services.transcribe_audio(file_path)
        
        if not transcription:
            return jsonify({
                'success': False,
                'error': 'Failed to transcribe audio'
            }), 500
        
        # Analyze pronunciation by comparing transcription to reference text
        analysis_results = aws_services.analyze_pronunciation(transcription, reference_text)
        
        # Return the results
        return jsonify({
            'success': True,
            'results': analysis_results,
            'transcription': transcription
        })
    except Exception as e:
        logging.error(f"Error analyzing pronunciation: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to analyze pronunciation'
        }), 500

# Additional utility routes can be added here