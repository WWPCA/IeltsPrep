from app_secure import db
from flask_login import UserMixin
from datetime import datetime, timedelta
import secrets


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    # ensure password hash field has length of at least 256
    password_hash = db.Column(db.String(256))
    # Password reset fields
    reset_token = db.Column(db.String(100), unique=True, nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<User {self.email}>'


class QRSession(db.Model):
    """Secure QR authentication sessions"""
    id = db.Column(db.Integer, primary_key=True)
    browser_session_id = db.Column(db.String(128), nullable=False)
    code = db.Column(db.String(64), unique=True, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, claimed, expired
    expires_at = db.Column(db.DateTime, nullable=False)
    claimed_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.String(100), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='active')  # active, completed, abandoned
    device_session_id = db.Column(db.String(128), nullable=False)
    score_data = db.Column(db.Text, nullable=True)  # JSON assessment results