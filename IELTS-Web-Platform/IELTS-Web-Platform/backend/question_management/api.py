#!/usr/bin/env python3
"""
Question Management API for IELTS GenAI Prep
Provides optimized question selection with no-repeat functionality
"""

from flask import Flask, request, jsonify
import json
import os
from question_filter import QuestionFilter
from user_question_tracking import QuestionTracker
from purchase_tracking import PurchaseTracker

app = Flask(__name__)

# Initialize services
question_filter = QuestionFilter('optimized-questions')
question_tracker = QuestionTracker()
purchase_tracker = PurchaseTracker()

@app.route('/api/questions/<assessment_type>', methods=['GET'])
def get_questions(assessment_type):
    """Get optimized questions for assessment type"""
    try:
        user_id = request.args.get('user_id')
        count = int(request.args.get('count', 4))
        user_level = request.args.get('level', 'intermediate')
        preferred_topics = request.args.getlist('topics')
        
        if not user_id:
            return jsonify({'error': 'user_id required'}), 400
        
        # Check if user has available assessments
        available = purchase_tracker.get_available_assessments(user_id, assessment_type)
        if available <= 0:
            return jsonify({'error': 'No assessments available. Please purchase more.'}), 403
        
        # Get questions user hasn't seen
        seen_questions = question_tracker.get_user_seen_questions(user_id, assessment_type)
        
        # Get optimized question set
        questions = question_filter.get_optimized_questions(
            assessment_type, count, user_level, preferred_topics, list(seen_questions)
        )
        
        if not questions:
            return jsonify({'error': 'No questions available'}), 404
        
        return jsonify({
            'status': 'success',
            'assessment_type': assessment_type,
            'questions': questions,
            'count': len(questions),
            'user_level': user_level,
            'available_assessments': available
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/questions/submit', methods=['POST'])
def submit_assessment():
    """Submit completed assessment and mark questions as used"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        purchase_id = data.get('purchase_id')
        question_ids = data.get('question_ids', [])
        assessment_type = data.get('assessment_type')
        
        if not all([user_id, purchase_id, question_ids, assessment_type]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Use assessment from purchase
        success = purchase_tracker.use_assessment(user_id, purchase_id, question_ids)
        if not success:
            return jsonify({'error': 'Failed to use assessment'}), 400
        
        # Mark questions as seen
        question_tracker.mark_questions_seen(user_id, assessment_type, question_ids)
        
        return jsonify({
            'status': 'success',
            'message': 'Assessment submitted successfully',
            'questions_marked': len(question_ids)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/<user_id>/stats', methods=['GET'])
def get_user_stats(user_id):
    """Get user question and purchase statistics"""
    try:
        purchases = purchase_tracker.get_user_purchases(user_id)
        
        stats = {
            'total_purchases': len(purchases),
            'assessments_by_type': {},
            'questions_seen_by_type': {}
        }
        
        assessment_types = ['academic_writing', 'general_writing', 'academic_speaking', 'general_speaking']
        
        for assessment_type in assessment_types:
            available = purchase_tracker.get_available_assessments(user_id, assessment_type)
            seen_questions = len(question_tracker.get_user_seen_questions(user_id, assessment_type))
            
            stats['assessments_by_type'][assessment_type] = {
                'available': available,
                'total_purchased': sum(p['assessments_total'] for p in purchases if p['assessment_type'] == assessment_type),
                'used': sum(p['assessments_used'] for p in purchases if p['assessment_type'] == assessment_type)
            }
            
            stats['questions_seen_by_type'][assessment_type] = seen_questions
        
        return jsonify({
            'status': 'success',
            'user_id': user_id,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
