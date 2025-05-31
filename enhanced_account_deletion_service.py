"""
Enhanced Account Deletion Service

This module provides comprehensive account deletion functionality with:
- 72-hour suspension period for users with active assessments
- Email notifications with reactivation options
- Secure token-based reactivation system
- Complete data removal after suspension period
"""

import os
import secrets
from datetime import datetime, timedelta
from flask import url_for, request, jsonify, flash, redirect
from werkzeug.security import generate_password_hash
from app import db
from models import User, UserTestAttempt, PaymentRecord
from enhanced_email_service import professional_email_service
import logging

logger = logging.getLogger(__name__)

class AccountDeletionService:
    
    @staticmethod
    def request_account_deletion(user_id):
        """
        Request account deletion with appropriate handling based on user status.
        
        Args:
            user_id (int): The ID of the user requesting deletion
            
        Returns:
            dict: Response with success status and message
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return {"success": False, "message": "User not found"}
            
            # Check if user has active assessments
            has_active_assessments = user.has_active_assessment_package()
            
            if has_active_assessments:
                # Schedule for deletion in 72 hours with suspension
                return AccountDeletionService._schedule_deletion_with_suspension(user)
            else:
                # Immediate deletion for users without active assessments
                return AccountDeletionService._immediate_deletion(user)
                
        except Exception as e:
            logger.error(f"Error in account deletion request: {str(e)}")
            return {"success": False, "message": "An error occurred processing your request"}
    
    @staticmethod
    def _schedule_deletion_with_suspension(user):
        """Schedule account deletion with 72-hour suspension period."""
        try:
            # Generate reactivation token
            reactivation_token = secrets.token_urlsafe(32)
            
            # Set deletion schedule
            deletion_time = datetime.utcnow() + timedelta(hours=72)
            
            # Update user record
            user.deletion_requested = True
            user.deletion_requested_at = datetime.utcnow()
            user.deletion_scheduled_for = deletion_time
            user.reactivation_token = reactivation_token
            user.account_activated = False  # Suspend account
            
            db.session.commit()
            
            # Send suspension notification email
            AccountDeletionService._send_suspension_email(user, reactivation_token)
            
            return {
                "success": True, 
                "message": "Your account has been suspended and scheduled for deletion in 72 hours. Check your email for reactivation instructions."
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error scheduling deletion with suspension: {str(e)}")
            return {"success": False, "message": "Failed to process suspension request"}
    
    @staticmethod
    def _immediate_deletion(user):
        """Perform immediate account deletion."""
        try:
            # Send deletion confirmation email before deletion
            AccountDeletionService._send_deletion_confirmation_email(user.email, user.email)
            
            # Delete all user data
            AccountDeletionService._delete_all_user_data(user.id)
            
            return {
                "success": True,
                "message": "Your account has been permanently deleted. A confirmation email has been sent."
            }
            
        except Exception as e:
            logger.error(f"Error in immediate deletion: {str(e)}")
            return {"success": False, "message": "Failed to delete account"}
    
    @staticmethod
    def _send_suspension_email(user, reactivation_token):
        """Send account suspension email with reactivation link."""
        try:
            # Determine the domain for the reactivation link
            domain = os.environ.get('REPLIT_DEV_DOMAIN')
            if not domain:
                domains = os.environ.get('REPLIT_DOMAINS', '').split(',')
                domain = domains[0] if domains else 'localhost:5000'
            
            reactivation_url = f"https://{domain}/reactivate-account/{reactivation_token}"
            
            subject = "Account Deletion Scheduled - Reactivation Available"
            
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background-color: #dc3545; color: white; padding: 20px; text-align: center;">
                    <h1 style="margin: 0;">Account Deletion Scheduled</h1>
                </div>
                
                <div style="padding: 30px; background-color: #f8f9fa;">
                    <p>Hello,</p>
                    
                    <p>You have requested to delete your IELTS AI Prep account. Since you have active assessment packages, we've scheduled your account for deletion in <strong>72 hours</strong>.</p>
                    
                    <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; margin: 20px 0; border-radius: 4px;">
                        <h3 style="color: #856404; margin-top: 0;">⚠️ Important Information</h3>
                        <ul style="color: #856404;">
                            <li>Your account is now suspended</li>
                            <li>Final deletion will occur on: <strong>{user.deletion_scheduled_for.strftime('%B %d, %Y at %I:%M %p UTC')}</strong></li>
                            <li>You can reactivate your account anytime before this date</li>
                        </ul>
                    </div>
                    
                    <h3>Want to Keep Your Account?</h3>
                    <p>If you change your mind, you can reactivate your account by clicking the button below:</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{reactivation_url}" style="background-color: #28a745; color: white; padding: 12px 30px; text-decoration: none; border-radius: 4px; display: inline-block; font-weight: bold;">
                            Reactivate My Account
                        </a>
                    </div>
                    
                    <p style="font-size: 14px; color: #666;">
                        <strong>Note:</strong> This reactivation link will expire when your account is permanently deleted.
                    </p>
                    
                    <hr style="margin: 30px 0;">
                    
                    <h3>What Happens After 72 Hours?</h3>
                    <p>If you don't reactivate your account, the following will be permanently deleted:</p>
                    <ul>
                        <li>Your profile and account information</li>
                        <li>All test results and assessment history</li>
                        <li>Your unused assessment packages</li>
                        <li>All personal data associated with your account</li>
                    </ul>
                    
                    <p>Best regards,<br>
                    The IELTS AI Prep Team</p>
                </div>
                
                <div style="background-color: #343a40; color: white; padding: 15px; text-align: center; font-size: 12px;">
                    <p style="margin: 0;">This is an automated message from IELTS AI Prep. Please do not reply to this email.</p>
                </div>
            </div>
            """
            
            professional_email_service._send_email(
                to_email=user.email,
                subject=subject,
                html_body=html_content,
                text_body="Your account has been suspended and scheduled for deletion in 72 hours. Check your email for reactivation instructions."
            )
            
            logger.info(f"Suspension email sent to user {user.id}")
            
        except Exception as e:
            logger.error(f"Failed to send suspension email: {str(e)}")
    
    @staticmethod
    def _send_deletion_confirmation_email(email, username):
        """Send account deletion confirmation email."""
        try:
            subject = "Account Successfully Deleted - IELTS AI Prep"
            
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background-color: #28a745; color: white; padding: 20px; text-align: center;">
                    <h1 style="margin: 0;">Account Deleted Successfully</h1>
                </div>
                
                <div style="padding: 30px; background-color: #f8f9fa;">
                    <p>Hello,</p>
                    
                    <p>Your IELTS AI Prep account has been permanently deleted as requested.</p>
                    
                    <div style="background-color: #d4edda; border: 1px solid #c3e6cb; padding: 15px; margin: 20px 0; border-radius: 4px;">
                        <h3 style="color: #155724; margin-top: 0;">✅ Deletion Complete</h3>
                        <p style="color: #155724; margin-bottom: 0;">All your personal data, test results, and account information have been permanently removed from our systems.</p>
                    </div>
                    
                    <h3>What Was Deleted:</h3>
                    <ul>
                        <li>Your profile and account information</li>
                        <li>All test results and assessment history</li>
                        <li>Any unused assessment packages</li>
                        <li>All personal data associated with your account</li>
                    </ul>
                    
                    <p>Thank you for using IELTS AI Prep. If you decide to use our services again in the future, you're welcome to create a new account.</p>
                    
                    <p>Best regards,<br>
                    The IELTS AI Prep Team</p>
                </div>
                
                <div style="background-color: #343a40; color: white; padding: 15px; text-align: center; font-size: 12px;">
                    <p style="margin: 0;">This is an automated message from IELTS AI Prep. Please do not reply to this email.</p>
                </div>
            </div>
            """
            
            professional_email_service._send_email(
                to_email=email,
                subject=subject,
                html_body=html_content,
                text_body="Your IELTS AI Prep account has been permanently deleted as requested."
            )
            
            logger.info(f"Deletion confirmation email sent to {email}")
            
        except Exception as e:
            logger.error(f"Failed to send deletion confirmation email: {str(e)}")
    
    @staticmethod
    def reactivate_account(token):
        """
        Reactivate a suspended account using the reactivation token.
        
        Args:
            token (str): The reactivation token
            
        Returns:
            dict: Response with success status and message
        """
        try:
            user = User.query.filter_by(reactivation_token=token).first()
            
            if not user:
                return {"success": False, "message": "Invalid reactivation token"}
            
            if not user.deletion_requested:
                return {"success": False, "message": "Account is not scheduled for deletion"}
            
            if datetime.utcnow() > user.deletion_scheduled_for:
                return {"success": False, "message": "Reactivation period has expired"}
            
            # Reactivate the account
            user.deletion_requested = False
            user.deletion_requested_at = None
            user.deletion_scheduled_for = None
            user.reactivation_token = None
            user.account_activated = True
            
            db.session.commit()
            
            # Send reactivation confirmation email
            AccountDeletionService._send_reactivation_confirmation_email(user)
            
            return {
                "success": True,
                "message": "Your account has been successfully reactivated!"
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error in account reactivation: {str(e)}")
            return {"success": False, "message": "Failed to reactivate account"}
    
    @staticmethod
    def _send_reactivation_confirmation_email(user):
        """Send account reactivation confirmation email."""
        try:
            subject = "Account Reactivated Successfully - IELTS AI Prep"
            
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background-color: #28a745; color: white; padding: 20px; text-align: center;">
                    <h1 style="margin: 0;">Welcome Back!</h1>
                </div>
                
                <div style="padding: 30px; background-color: #f8f9fa;">
                    <p>Hello,</p>
                    
                    <p>Great news! Your IELTS AI Prep account has been successfully reactivated.</p>
                    
                    <div style="background-color: #d4edda; border: 1px solid #c3e6cb; padding: 15px; margin: 20px 0; border-radius: 4px;">
                        <h3 style="color: #155724; margin-top: 0;">✅ Account Status</h3>
                        <ul style="color: #155724;">
                            <li>Your account is now fully active</li>
                            <li>All your assessment packages are restored</li>
                            <li>You can access all features immediately</li>
                        </ul>
                    </div>
                    
                    <p>You can now log in and continue your IELTS preparation journey with all your progress intact.</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="https://{os.environ.get('REPLIT_DEV_DOMAIN', 'localhost')}/login" style="background-color: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 4px; display: inline-block; font-weight: bold;">
                            Login to Your Account
                        </a>
                    </div>
                    
                    <p>Thank you for choosing to continue with IELTS AI Prep!</p>
                    
                    <p>Best regards,<br>
                    The IELTS AI Prep Team</p>
                </div>
                
                <div style="background-color: #343a40; color: white; padding: 15px; text-align: center; font-size: 12px;">
                    <p style="margin: 0;">This is an automated message from IELTS AI Prep. Please do not reply to this email.</p>
                </div>
            </div>
            """
            
            professional_email_service._send_email(
                to_email=user.email,
                subject=subject,
                html_body=html_content,
                text_body="Your account has been successfully reactivated! You can now log in."
            )
            
            logger.info(f"Reactivation confirmation email sent to user {user.id}")
            
        except Exception as e:
            logger.error(f"Failed to send reactivation confirmation email: {str(e)}")
    
    @staticmethod
    def _delete_all_user_data(user_id):
        """
        Permanently delete all user data from the database.
        
        Args:
            user_id (int): The ID of the user to delete
        """
        try:
            # Delete user test attempts
            UserTestAttempt.query.filter_by(user_id=user_id).delete()
            
            # Delete payment records (keep for compliance but anonymize)
            payment_records = PaymentRecord.query.filter_by(user_id=user_id).all()
            for record in payment_records:
                record.user_id = None  # Anonymize instead of delete for compliance
            
            # Delete the user account
            user = User.query.get(user_id)
            if user:
                db.session.delete(user)
            
            db.session.commit()
            logger.info(f"All data for user {user_id} has been deleted")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting user data for user {user_id}: {str(e)}")
            raise
    
    @staticmethod
    def process_scheduled_deletions():
        """
        Process all accounts scheduled for deletion (to be run as a scheduled job).
        This should be called periodically to clean up expired accounts.
        """
        try:
            # Find accounts scheduled for deletion that have passed their deadline
            expired_accounts = User.query.filter(
                User.deletion_requested == True,
                User.deletion_scheduled_for <= datetime.utcnow()
            ).all()
            
            for user in expired_accounts:
                logger.info(f"Processing scheduled deletion for user {user.id}")
                
                # Send final deletion confirmation
                AccountDeletionService._send_deletion_confirmation_email(user.email, user.email)
                
                # Delete all user data
                AccountDeletionService._delete_all_user_data(user.id)
            
            logger.info(f"Processed {len(expired_accounts)} scheduled deletions")
            
        except Exception as e:
            logger.error(f"Error processing scheduled deletions: {str(e)}")