from app_secure import db
from flask_login import UserMixin
from datetime import datetime, timedelta
import secrets
import json
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    """Unified User model combining session-based and JWT authentication support"""
    __tablename__ = 'ielts_genai_user'  # Use the existing table name
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Enhanced user profile fields
    full_name = db.Column(db.String(120), nullable=True)
    profile_picture = db.Column(db.String(256), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    
    # Timestamps (mapping created_at -> join_date for compatibility)
    join_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Keep for backward compatibility
    
    # Password reset fields (added from original User model)
    reset_token = db.Column(db.String(100), unique=True, nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)
    
    # User status and preferences
    is_active = db.Column(db.Boolean, default=True)
    assessment_package_status = db.Column(db.String(20), default="none")
    assessment_package_expiry = db.Column(db.DateTime, nullable=True)
    
    # Legacy fields for backward compatibility
    subscription_status = db.Column(db.String(20), default="none")
    subscription_expiry = db.Column(db.DateTime, nullable=True)
    preferred_language = db.Column(db.String(10), default="en")
    _preferences = db.Column(db.Text, default='{}')  # JSON string of user preferences
    
    def set_password(self, password):
        """Set the user's password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the password is correct"""
        return check_password_hash(self.password_hash, password)
    
    @property
    def preferences(self):
        """Get user preferences"""
        try:
            return json.loads(self._preferences) if self._preferences else {}
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @preferences.setter
    def preferences(self, value):
        """Set user preferences"""
        self._preferences = json.dumps(value) if value else '{}'
    
    def has_active_assessment_package(self):
        """Check if the user has an active assessment package"""
        if not self.assessment_package_expiry:
            return False
        return self.assessment_package_status == "active" and self.assessment_package_expiry > datetime.utcnow()
    
    def __repr__(self):
        return f'<User {self.email}>'


class QRSession(db.Model):
    """Secure QR authentication sessions"""
    id = db.Column(db.Integer, primary_key=True)
    browser_session_id = db.Column(db.String(128), nullable=False)
    code = db.Column(db.String(64), unique=True, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, claimed, expired
    expires_at = db.Column(db.DateTime, nullable=False)
    claimed_user_id = db.Column(db.Integer, db.ForeignKey('ielts_genai_user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @staticmethod
    def generate_secure_code():
        """Generate cryptographically secure 128-bit random code"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def create_session(browser_session_id, ttl_seconds=120):
        """Create new QR session with secure code and expiration"""
        qr_session = QRSession(
            browser_session_id=browser_session_id,
            code=QRSession.generate_secure_code(),
            expires_at=datetime.utcnow() + timedelta(seconds=ttl_seconds)
        )
        db.session.add(qr_session)
        db.session.commit()
        return qr_session


class AssessmentEntitlement(db.Model):
    """Track user's purchased assessment entitlements"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('ielts_genai_user.id'), nullable=False)
    product_id = db.Column(db.String(100), nullable=False)  # e.g., 'academic_writing', 'general_speaking'
    remaining_uses = db.Column(db.Integer, nullable=False, default=0)
    expires_at = db.Column(db.DateTime, nullable=True)
    transaction_id = db.Column(db.String(200), unique=True, nullable=True)  # App Store/Play transaction
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'product_id', name='unique_user_product'),
        db.CheckConstraint('remaining_uses >= 0', name='check_remaining_uses_positive')
    )


class AssessmentAttempt(db.Model):
    """Track individual assessment attempts"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('ielts_genai_user.id'), nullable=False)
    product_id = db.Column(db.String(100), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='active')  # active, completed, abandoned
    device_session_id = db.Column(db.String(128), nullable=False)
    score_data = db.Column(db.Text, nullable=True)  # JSON assessment results