"""
Browser-Based Speech Recognition Routes
Routes for handling conversational speaking assessments using local browser speech recognition
"""

from flask import request, jsonify
from flask_login import login_required, current_user
from app import app, db
from nova_sonic_services import NovaSonicService
from enhanced_nova_assessment import EnhancedNovaAssessment
import json
import logging

logger = logging.getLogger(__name__)

@app.route('/api/continue_conversation', methods=['POST'])
@login_required
def continue_conversation():
    """Continue conversation using browser-generated transcript"""
    try:
        data = request.get_json()
        user_message = data.get('user_message', '')
        conversation_history = data.get('conversation_history', [])
        current_part = data.get('current_part', 1)
        
        if not user_message:
            return jsonify({'success': False, 'error': 'No user message provided'})
        
        # Use Nova Sonic for browser-transcript assessment
        nova_sonic = NovaSonicService()
        
        # Assess the browser-generated transcript
        result = nova_sonic.assess_browser_transcript(
            transcript=user_message,
            conversation_history=conversation_history,
            part_number=current_part
        )
        
        if result.get('success'):
            # Determine if we should move to next part based on conversation length
            next_part = current_part
            if len(conversation_history) > 8 and current_part == 1:
                next_part = 2
            elif len(conversation_history) > 15 and current_part == 2:
                next_part = 3
                
            return jsonify({
                'success': True,
                'response': result.get('response', 'Please continue.'),
                'next_part': next_part,
                'assessment_notes': result.get('assessment_notes', '')
            })
        else:
            return jsonify({'success': False, 'error': result.get('error', 'Assessment failed')})
            
    except Exception as e:
        logger.error(f"Continue conversation error: {e}")
        return jsonify({'success': False, 'error': 'Conversation service unavailable'})

@app.route('/api/start_conversation', methods=['POST'])
@login_required
def start_conversation():
    """Start a conversation session with Maya"""
    try:
        data = request.get_json()
        assessment_type = data.get('assessment_type', 'academic_speaking')
        part = data.get('part', 1)
        
        nova_sonic = NovaSonicService()
        
        # Create conversation session
        result = nova_sonic.create_speaking_conversation(
            user_level='intermediate',
            part_number=part,
            topic='general_introduction'
        )
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'opening_message': result.get('examiner_response', 'Hello! I\'m Maya, ready to begin your assessment.'),
                'conversation_id': result.get('conversation_id')
            })
        else:
            return jsonify({'success': False, 'error': result.get('error', 'Conversation start failed')})
            
    except Exception as e:
        logger.error(f"Conversation start error: {e}")
        return jsonify({'success': False, 'error': 'Conversation service unavailable'})

@app.route('/api/finalize_conversation', methods=['POST'])
@login_required
def finalize_conversation():
    """Generate final assessment for the complete conversation"""
    try:
        data = request.get_json()
        conversation_history = data.get('conversation_history', [])
        part_number = data.get('part_number', 1)
        assessment_type = data.get('assessment_type', 'academic')
        
        if not conversation_history:
            return jsonify({'success': False, 'error': 'No conversation history provided'})
        
        # Use Enhanced Nova Assessment for final scoring
        enhanced_assessment = EnhancedNovaAssessment()
        
        # Create transcript from conversation history
        transcript = "\n".join([
            f"{msg.get('speaker', 'User')}: {msg.get('message', '')}"
            for msg in conversation_history
        ])
        
        # Generate final assessment
        result = enhanced_assessment.assess_speaking_conversation_transcript(
            transcript=transcript,
            part_number=part_number,
            assessment_type=assessment_type,
            user_id=current_user.id
        )
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'final_assessment': result.get('assessment', {}),
                'transcript': transcript
            })
        else:
            return jsonify({'success': False, 'error': result.get('error', 'Final assessment failed')})
            
    except Exception as e:
        logger.error(f"Finalize conversation error: {e}")
        return jsonify({'success': False, 'error': 'Assessment generation failed'})

print("Browser-based speech recognition routes loaded successfully")