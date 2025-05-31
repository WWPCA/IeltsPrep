"""
Enhanced Assessment Assignment Service with Unique Question Tracking

This service ensures users get unique assessments every time they purchase,
preventing duplicate questions across multiple purchases of the same type.
"""

import json
import random
import logging
from datetime import datetime, timedelta
from sqlalchemy import text
from models import db, User, Assessment

# Configure logging
logger = logging.getLogger(__name__)

def get_user_used_assessments(user_id, assessment_type):
    """
    Get all assessment IDs that have been used by this user for this assessment type.
    
    Args:
        user_id (int): The user's ID
        assessment_type (str): Specific type like 'academic_writing', 'academic_speaking', etc.
    
    Returns:
        set: Set of assessment IDs already used by this user
    """
    try:
        # Query all user test attempts to see which assessments were already used
        used_assessments = db.session.execute(text("""
            SELECT DISTINCT uta.assessment_id
            FROM user_test_attempt uta
            JOIN assessment a ON uta.assessment_id = a.id
            WHERE uta.user_id = :user_id 
            AND a.assessment_type = :assessment_type
        """), {
            "user_id": user_id,
            "assessment_type": assessment_type
        }).fetchall()
        
        return {row[0] for row in used_assessments}
    except Exception as e:
        logger.error(f"Error getting used assessments for user {user_id}: {e}")
        return set()

def get_available_unique_assessments(user_id, assessment_type, quantity_needed=1):
    """
    Get unique assessments that haven't been used by this user.
    
    Args:
        user_id (int): The user's ID
        assessment_type (str): Specific assessment type
        quantity_needed (int): Number of unique assessments needed
    
    Returns:
        list: List of assessment IDs that are unique for this user
    """
    try:
        # Get all available assessments of this type
        all_assessments = db.session.execute(text("""
            SELECT id FROM assessment 
            WHERE assessment_type = :assessment_type 
            AND status = 'active'
            ORDER BY id
        """), {"assessment_type": assessment_type}).fetchall()
        
        all_assessment_ids = [row[0] for row in all_assessments]
        
        # Get assessments already used by this user
        used_assessment_ids = get_user_used_assessments(user_id, assessment_type)
        
        # Calculate available unique assessments
        available_assessments = [aid for aid in all_assessment_ids if aid not in used_assessment_ids]
        
        # Randomize to ensure variety
        random.shuffle(available_assessments)
        
        # Return the requested quantity
        return available_assessments[:quantity_needed]
        
    except Exception as e:
        logger.error(f"Error getting available assessments for user {user_id}: {e}")
        return []

def assign_unique_assessments_to_user(user_id, package_name, quantity):
    """
    Assign unique assessments to a user based on their package purchase.
    
    Args:
        user_id (int): The user's ID
        package_name (str): Package name like "Academic Writing", "General Speaking", etc.
        quantity (int): Number of assessments to assign
    
    Returns:
        dict: Result with assigned assessment IDs and success status
    """
    try:
        # Map package names to assessment types (database format)
        package_to_type = {
            "Academic Writing": "Academic Writing",
            "General Writing": "General Writing", 
            "Academic Speaking": "Academic Speaking",
            "General Speaking": "General Speaking"
        }
        
        assessment_type = package_to_type.get(package_name)
        if not assessment_type:
            return {"success": False, "error": f"Unknown package type: {package_name}"}
        
        # Get unique assessments for this user
        assigned_assessment_ids = get_available_unique_assessments(
            user_id, assessment_type, quantity
        )
        
        if len(assigned_assessment_ids) < quantity:
            # Check if user has used all available assessments
            total_available = db.session.execute(text("""
                SELECT COUNT(*) FROM assessment 
                WHERE assessment_type = :assessment_type AND status = 'active'
            """), {"assessment_type": assessment_type}).scalar()
            
            used_count = len(get_user_used_assessments(user_id, assessment_type))
            
            if used_count >= total_available:
                # User has exhausted all unique assessments - start cycling through them again
                logger.info(f"User {user_id} has completed all {total_available} {assessment_type} assessments. Cycling through again.")
                
                all_assessments = db.session.execute(text("""
                    SELECT id FROM assessment 
                    WHERE assessment_type = :assessment_type AND status = 'active'
                    ORDER BY RANDOM()
                    LIMIT :quantity
                """), {
                    "assessment_type": assessment_type,
                    "quantity": quantity
                }).fetchall()
                
                assigned_assessment_ids = [row[0] for row in all_assessments]
            else:
                return {
                    "success": False, 
                    "error": f"Not enough unique assessments available. Requested: {quantity}, Available: {len(assigned_assessment_ids)}"
                }
        
        # Record the assignment in user_package table
        db.session.execute(text("""
            INSERT INTO user_package (user_id, package_name, purchase_date, quantity_purchased, quantity_remaining, status, created_at)
            VALUES (:user_id, :package_name, NOW(), :quantity, :quantity, 'active', NOW())
        """), {
            "user_id": user_id,
            "package_name": package_name,
            "quantity": quantity
        })
        
        db.session.commit()
        
        logger.info(f"Successfully assigned {len(assigned_assessment_ids)} unique {assessment_type} assessments to user {user_id}")
        
        return {
            "success": True,
            "assigned_assessment_ids": assigned_assessment_ids,
            "assessment_type": assessment_type,
            "package_name": package_name
        }
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error assigning assessments to user {user_id}: {e}")
        return {"success": False, "error": str(e)}

def get_user_assessment_summary(user_id):
    """
    Get a summary of assessments used and available for a user.
    
    Args:
        user_id (int): The user's ID
    
    Returns:
        dict: Summary of assessment usage by type
    """
    summary = {}
    
    assessment_types = ["academic_writing", "academic_speaking", "general_writing", "general_speaking"]
    
    for assessment_type in assessment_types:
        try:
            # Total available
            total = db.session.execute(text("""
                SELECT COUNT(*) FROM assessment 
                WHERE assessment_type = :assessment_type AND status = 'active'
            """), {"assessment_type": assessment_type}).scalar()
            
            # Used by user
            used = len(get_user_used_assessments(user_id, assessment_type))
            
            # Remaining unique
            remaining = max(0, total - used)
            
            summary[assessment_type] = {
                "total_available": total,
                "used_by_user": used,
                "remaining_unique": remaining,
                "completion_percentage": round((used / total * 100) if total > 0 else 0, 1)
            }
            
        except Exception as e:
            logger.error(f"Error getting summary for {assessment_type}: {e}")
            summary[assessment_type] = {"error": str(e)}
    
    return summary

def validate_assessment_assignment_integrity():
    """
    Validate that the assessment assignment system is working correctly.
    
    Returns:
        dict: Validation results
    """
    try:
        # Check total assessments by type
        assessment_counts = db.session.execute(text("""
            SELECT assessment_type, COUNT(*) as count
            FROM assessment 
            WHERE status = 'active'
            GROUP BY assessment_type
            ORDER BY assessment_type
        """)).fetchall()
        
        results = {
            "assessment_counts": {row[0]: row[1] for row in assessment_counts},
            "total_assessments": sum(row[1] for row in assessment_counts),
            "validation_passed": True
        }
        
        # Check for naming consistency
        naming_issues = db.session.execute(text("""
            SELECT assessment_type, title FROM assessment 
            WHERE (assessment_type = 'academic_writing' AND title NOT LIKE '%Academic Writing%') 
            OR (assessment_type = 'general_writing' AND title NOT LIKE '%General Training Writing%')
            OR (assessment_type = 'academic_speaking' AND title NOT LIKE '%Academic Speaking%')
            OR (assessment_type = 'general_speaking' AND title NOT LIKE '%General Training Speaking%')
        """)).fetchall()
        
        if naming_issues:
            results["naming_issues"] = [{"type": row[0], "title": row[1]} for row in naming_issues]
            results["validation_passed"] = False
        
        return results
        
    except Exception as e:
        logger.error(f"Error validating assessment assignment integrity: {e}")
        return {"error": str(e), "validation_passed": False}