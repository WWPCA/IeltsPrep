"""
Mobile Purchase Validation API
Handles in-app purchase validation and user access synchronization
"""

import os
import json
import logging
from datetime import datetime, timedelta
from flask import request, jsonify
from models import db, User, UserAssessmentAssignment
from assessment_assignment_service import assign_assessment_package

logger = logging.getLogger(__name__)

# Product ID mapping for validation - aligned with actual 4 assessment products
VALID_PRODUCT_IDS = {
    # iOS Product IDs
    'com.ieltsaiprep.academic.writing': {
        'assessment_type': 'academic_writing',
        'package_type': 'individual',
        'assessment_count': 1
    },
    'com.ieltsaiprep.academic.speaking': {
        'assessment_type': 'academic_speaking',
        'package_type': 'individual',
        'assessment_count': 1
    },
    'com.ieltsaiprep.general.writing': {
        'assessment_type': 'general_writing',
        'package_type': 'individual', 
        'assessment_count': 1
    },
    'com.ieltsaiprep.general.speaking': {
        'assessment_type': 'general_speaking',
        'package_type': 'individual',
        'assessment_count': 1
    },
    
    # Android Product IDs
    'academic_writing_assessment': {
        'assessment_type': 'academic_writing',
        'package_type': 'individual',
        'assessment_count': 1
    },
    'academic_speaking_assessment': {
        'assessment_type': 'academic_speaking',
        'package_type': 'individual', 
        'assessment_count': 1
    },
    'general_writing_assessment': {
        'assessment_type': 'general_writing',
        'package_type': 'individual',
        'assessment_count': 1
    },
    'general_speaking_assessment': {
        'assessment_type': 'general_speaking',
        'package_type': 'individual',
        'assessment_count': 1
    }
}

def validate_apple_receipt(receipt_data, product_id):
    """
    Validate Apple App Store receipt
    In production, this would call Apple's receipt validation API
    """
    try:
        # Production validation would use:
        # https://buy.itunes.apple.com/verifyReceipt (production)
        # https://sandbox.itunes.apple.com/verifyReceipt (sandbox)
        
        # For now, return validation structure
        return {
            'valid': True,
            'product_id': product_id,
            'transaction_id': f"apple_txn_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'purchase_date': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Apple receipt validation error: {e}")
        return {'valid': False, 'error': str(e)}

def validate_google_purchase(purchase_token, product_id, package_name):
    """
    Validate Google Play purchase
    In production, this would call Google Play Developer API
    """
    try:
        # Production validation would use:
        # Google Play Developer API v3
        # https://developers.google.com/android-publisher/api-ref/rest/v3/purchases/products/get
        
        return {
            'valid': True,
            'product_id': product_id,
            'transaction_id': f"google_txn_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'purchase_date': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Google purchase validation error: {e}")
        return {'valid': False, 'error': str(e)}

def validate_mobile_purchase():
    """
    API endpoint to validate mobile in-app purchases
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_id', 'platform', 'product_id']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        user_id = data['user_id']
        platform = data['platform'].lower()
        product_id = data['product_id']
        
        # Validate user exists
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Validate product ID
        if product_id not in VALID_PRODUCT_IDS:
            return jsonify({
                'success': False,
                'error': 'Invalid product ID'
            }), 400
        
        # Platform-specific validation
        validation_result = None
        
        if platform == 'ios':
            receipt_data = data.get('receipt_data')
            if not receipt_data:
                return jsonify({
                    'success': False,
                    'error': 'Missing receipt_data for iOS purchase'
                }), 400
            
            validation_result = validate_apple_receipt(receipt_data, product_id)
            
        elif platform == 'android':
            purchase_token = data.get('purchase_token')
            package_name = data.get('package_name', 'com.ieltsaiprep.app')
            
            if not purchase_token:
                return jsonify({
                    'success': False,
                    'error': 'Missing purchase_token for Android purchase'
                }), 400
            
            validation_result = validate_google_purchase(purchase_token, product_id, package_name)
            
        else:
            return jsonify({
                'success': False,
                'error': 'Unsupported platform'
            }), 400
        
        # Check validation result
        if not validation_result.get('valid'):
            return jsonify({
                'success': False,
                'error': f"Purchase validation failed: {validation_result.get('error', 'Unknown error')}"
            }), 400
        
        # Get product configuration
        product_config = VALID_PRODUCT_IDS[product_id]
        assessment_type = product_config['assessment_type']
        assessment_count = product_config['assessment_count']
        
        # Assign assessment package to user
        try:
            assign_assessment_package(
                user_id=user_id,
                package_type=assessment_type,
                assessment_count=assessment_count
            )
            
            logger.info(f"Successfully assigned {assessment_type} package to user {user_id}")
            
            return jsonify({
                'success': True,
                'message': 'Purchase validated and access granted',
                'details': {
                    'assessment_type': assessment_type,
                    'assessment_count': assessment_count,
                    'transaction_id': validation_result.get('transaction_id'),
                    'access_granted_at': datetime.now().isoformat()
                }
            })
            
        except Exception as e:
            logger.error(f"Error assigning assessment package: {e}")
            return jsonify({
                'success': False,
                'error': 'Failed to grant access after purchase validation'
            }), 500
            
    except Exception as e:
        logger.error(f"Mobile purchase validation error: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

def get_user_purchase_status():
    """
    API endpoint to check user's current purchase status
    """
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'Missing user_id parameter'
            }), 400
        
        # Get user's active assignments
        assignments = UserAssessmentAssignment.query.filter(
            UserAssessmentAssignment.user_id == user_id,
            UserAssessmentAssignment.expires_at > datetime.utcnow()
        ).all()
        
        purchase_status = []
        for assignment in assignments:
            purchase_status.append({
                'assessment_type': assignment.assessment_type,
                'assigned_at': assignment.assigned_at.isoformat(),
                'expires_at': assignment.expires_at.isoformat(),
                'is_active': assignment.expires_at > datetime.utcnow()
            })
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'active_purchases': purchase_status,
            'total_active': len(purchase_status)
        })
        
    except Exception as e:
        logger.error(f"Error checking purchase status: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500