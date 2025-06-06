"""
Account Cleanup Service
Manages inactive account cleanup and GDPR compliance for non-purchasing users
"""

import os
from datetime import datetime, timedelta
from flask import current_app
from models import db, User
from enhanced_email_service import send_notification_email
import logging

logger = logging.getLogger(__name__)

class AccountCleanupService:
    """Service for managing inactive account cleanup"""
    
    INACTIVE_THRESHOLD_DAYS = 365  # 1 year of inactivity
    WARNING_PERIOD_DAYS = 30      # 30 days notice before deletion
    
    @classmethod
    def identify_inactive_accounts(cls):
        """Identify accounts that haven't purchased anything and are inactive"""
        cutoff_date = datetime.utcnow() - timedelta(days=cls.INACTIVE_THRESHOLD_DAYS)
        
        # Find users with no purchases who haven't logged in recently
        inactive_users = db.session.query(User).filter(
            ~User.id.in_(
                db.session.query(db.distinct(db.text('user_package.user_id')))
                .select_from(db.text('user_package'))
                .filter(db.text('user_package.user_id IS NOT NULL'))
            ),
            User.last_login < cutoff_date
        ).all()
        
        return inactive_users
    
    @classmethod
    def identify_accounts_for_warning(cls):
        """Identify accounts approaching deletion that need warning"""
        warning_date = datetime.utcnow() - timedelta(
            days=cls.INACTIVE_THRESHOLD_DAYS - cls.WARNING_PERIOD_DAYS
        )
        
        inactive_users = db.session.query(User).filter(
            ~User.id.in_(
                db.session.query(db.distinct(db.text('user_package.user_id')))
                .select_from(db.text('user_package'))
                .filter(db.text('user_package.user_id IS NOT NULL'))
            ),
            User.last_login < warning_date,
            User.last_login >= datetime.utcnow() - timedelta(days=cls.INACTIVE_THRESHOLD_DAYS),
            User.deletion_warning_sent != True
        ).all()
        
        return inactive_users
    
    @classmethod
    def send_deletion_warnings(cls):
        """Send deletion warning emails to inactive accounts"""
        try:
            users_to_warn = cls.identify_accounts_for_warning()
            
            for user in users_to_warn:
                cls._send_deletion_warning_email(user)
                user.deletion_warning_sent = True
                user.deletion_warning_date = datetime.utcnow()
            
            db.session.commit()
            logger.info(f"Sent deletion warnings to {len(users_to_warn)} users")
            return len(users_to_warn)
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error sending deletion warnings: {e}")
            return 0
    
    @classmethod
    def cleanup_inactive_accounts(cls):
        """Delete accounts that have been inactive for the threshold period"""
        try:
            inactive_users = cls.identify_inactive_accounts()
            deleted_count = 0
            
            for user in inactive_users:
                # Only delete if warning was sent at least 30 days ago
                if (user.deletion_warning_sent and 
                    user.deletion_warning_date and
                    (datetime.utcnow() - user.deletion_warning_date).days >= cls.WARNING_PERIOD_DAYS):
                    
                    cls._delete_user_data(user)
                    deleted_count += 1
            
            db.session.commit()
            logger.info(f"Deleted {deleted_count} inactive accounts")
            return deleted_count
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error during account cleanup: {e}")
            return 0
    
    @classmethod
    def _send_deletion_warning_email(cls, user):
        """Send deletion warning email to user"""
        subject = "IELTS GenAI Prep - Account Deletion Notice"
        
        content = f"""
        Dear {user.email},
        
        We noticed you haven't used your IELTS GenAI Prep account recently. To comply with data protection regulations and maintain our service quality, we will be deleting inactive accounts.
        
        Your account will be permanently deleted in 30 days unless you:
        - Log in to your account
        - Purchase an assessment package
        - Reply to this email to keep your account active
        
        If you no longer need your account, no action is required.
        
        To keep your account active, simply log in at: https://{os.environ.get('REPLIT_DEV_DOMAIN', 'localhost')}/login
        
        Best regards,
        The IELTS GenAI Prep Team
        """
        
        send_notification_email(user.email, subject, content)
        logger.info(f"Sent deletion warning to {user.email}")
    
    @classmethod
    def _delete_user_data(cls, user):
        """Safely delete user and associated data"""
        try:
            # Delete related records first (foreign key constraints)
            db.session.execute(
                db.text("DELETE FROM user_assessment_attempt WHERE user_id = :user_id"),
                {"user_id": user.id}
            )
            db.session.execute(
                db.text("DELETE FROM assessment_session WHERE user_id = :user_id"),
                {"user_id": user.id}
            )
            db.session.execute(
                db.text("DELETE FROM consent_record WHERE user_id = :user_id"),
                {"user_id": user.id}
            )
            
            # Delete the user
            db.session.delete(user)
            logger.info(f"Deleted user account: {user.email}")
            
        except Exception as e:
            logger.error(f"Error deleting user {user.email}: {e}")
            raise
    
    @classmethod
    def get_cleanup_statistics(cls):
        """Get statistics about account cleanup"""
        total_users = db.session.query(User).count()
        
        users_with_purchases = db.session.query(User).filter(
            User.id.in_(
                db.session.query(db.distinct(db.text('user_package.user_id')))
                .select_from(db.text('user_package'))
                .filter(db.text('user_package.user_id IS NOT NULL'))
            )
        ).count()
        
        inactive_users = len(cls.identify_inactive_accounts())
        warning_candidates = len(cls.identify_accounts_for_warning())
        
        return {
            'total_users': total_users,
            'users_with_purchases': users_with_purchases,
            'users_without_purchases': total_users - users_with_purchases,
            'inactive_accounts': inactive_users,
            'accounts_needing_warning': warning_candidates
        }

def run_daily_cleanup():
    """Daily cleanup job function"""
    logger.info("Starting daily account cleanup process")
    
    warnings_sent = AccountCleanupService.send_deletion_warnings()
    accounts_deleted = AccountCleanupService.cleanup_inactive_accounts()
    
    stats = AccountCleanupService.get_cleanup_statistics()
    
    logger.info(f"Cleanup complete - Warnings sent: {warnings_sent}, Accounts deleted: {accounts_deleted}")
    logger.info(f"Current stats: {stats}")
    
    return {
        'warnings_sent': warnings_sent,
        'accounts_deleted': accounts_deleted,
        'statistics': stats
    }