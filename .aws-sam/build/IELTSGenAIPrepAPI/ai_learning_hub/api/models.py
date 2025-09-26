"""
Models for the AI Learning Hub mobile API
These models are specific to the mobile app functionality
"""
from ai_learning_hub.app import db
from datetime import datetime
import json

class MobileDevice(db.Model):
    """Model for tracking mobile devices"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('ielts_genai_user.id'), nullable=False)
    platform = db.Column(db.String(20), nullable=False)  # 'ios' or 'android'
    device_uuid = db.Column(db.String(64), nullable=False, unique=True)
    device_name = db.Column(db.String(128), nullable=True)
    app_version = db.Column(db.String(20), nullable=True)
    os_version = db.Column(db.String(20), nullable=True)
    push_token = db.Column(db.String(256), nullable=True)
    last_sync = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<MobileDevice {self.platform} {self.device_name}>'
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'platform': self.platform,
            'device_name': self.device_name,
            'app_version': self.app_version,
            'os_version': self.os_version,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None
        }

class LocalSync(db.Model):
    """Model for tracking local data synchronization with the server"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('ielts_genai_user.id'), nullable=False)
    device_id = db.Column(db.Integer, db.ForeignKey('mobile_device.id'), nullable=False)
    sync_type = db.Column(db.String(20), nullable=False)  # 'full', 'partial', 'content'
    content_type = db.Column(db.String(20), nullable=True)  # 'course', 'lesson', 'note'
    _sync_data = db.Column(db.Text, nullable=True)  # JSON data
    sync_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_success = db.Column(db.Boolean, default=True)
    
    @property
    def sync_data(self):
        """Get the sync data"""
        if self._sync_data:
            return json.loads(self._sync_data)
        return {}
    
    @sync_data.setter
    def sync_data(self, value):
        """Set the sync data"""
        self._sync_data = json.dumps(value)
    
    def __repr__(self):
        return f'<LocalSync {self.sync_type} {self.sync_date}>'

class ApiAccessToken(db.Model):
    """Model for API access tokens"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('ielts_genai_user.id'), nullable=False)
    device_id = db.Column(db.Integer, db.ForeignKey('mobile_device.id'), nullable=False)
    token = db.Column(db.String(256), nullable=False, unique=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    last_used = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<ApiAccessToken {self.id} expires: {self.expires_at}>'
    
    def is_valid(self):
        """Check if the token is valid"""
        return self.is_active and datetime.utcnow() < self.expires_at

class PushNotification(db.Model):
    """Model for push notifications"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('ielts_genai_user.id'), nullable=False)
    title = db.Column(db.String(128), nullable=False)
    message = db.Column(db.Text, nullable=False)
    _data = db.Column(db.Text, nullable=True)  # JSON data for deep linking
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime, nullable=True)
    notification_type = db.Column(db.String(20), nullable=False)  # 'course', 'reminder', 'system'
    
    @property
    def data(self):
        """Get the notification data"""
        if self._data:
            return json.loads(self._data)
        return {}
    
    @data.setter
    def data(self, value):
        """Set the notification data"""
        self._data = json.dumps(value)
    
    def __repr__(self):
        return f'<PushNotification {self.title}>'
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'data': self.data,
            'sent_at': self.sent_at.isoformat(),
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'notification_type': self.notification_type,
            'is_read': self.read_at is not None
        }