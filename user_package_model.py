"""
UserPackage model for handling multiple individual assessment packages per user.
"""
from app import db
from datetime import datetime

class UserPackage(db.Model):
    """Individual assessment package purchased by a user."""
    __tablename__ = 'user_package'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    package_name = db.Column(db.String(50), nullable=False)  # e.g., "Academic Speaking"
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='active')  # active, expired, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure one package type per user
    __table_args__ = (
        db.UniqueConstraint('user_id', 'package_name', name='unique_user_package'),
        db.Index('idx_user_package_user_id', 'user_id'),
        db.Index('idx_user_package_status', 'status'),
        db.Index('idx_user_package_expiry', 'expiry_date'),
    )
    
    # Relationship back to User
    user = db.relationship('User', backref=db.backref('packages', lazy=True, cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<UserPackage {self.package_name} for User {self.user_id}>'
    
    @property
    def is_active(self):
        """Check if this package is currently active."""
        if self.status != 'active':
            return False
        if self.expiry_date and self.expiry_date <= datetime.utcnow():
            return False
        return True
    
    def expire_package(self):
        """Mark this package as expired."""
        self.status = 'expired'
        db.session.commit()