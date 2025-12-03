from datetime import datetime
from app.extensions import db
from sqlalchemy import Enum, JSON
# from .Enums import SuggestionStatus

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    type = db.Column(db.String(50), default='system')
    title = db.Column(db.String(255))
    message = db.Column(db.Text)
    data = db.Column(JSON, default={})
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    notification_owner = db.relationship('User', back_populates='notifications', foreign_keys=[user_id])
    
    # HELPER FUNCTIONS
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.read_at = datetime.utcnow()
        db.session.commit()
    
    def mark_as_unread(self):
        """Mark notification as unread"""
        self.is_read = False
        self.read_at = None
        db.session.commit()
    
    def is_recent(self, hours=24):
        """Check if notification is recent"""
        time_diff = datetime.utcnow() - self.created_at
        return time_diff.total_seconds() <= hours * 3600
    
    def get_related_data(self, key=None):
        """Get related data from notification"""
        if key:
            return self.data.get(key)
        return self.data
    
    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'type': self.type,
            'title': self.title,
            'message': self.message,
            'data': self.data or {},
            'isRead': self.is_read,
            'readAt': self.read_at.isoformat() if self.read_at else None,
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat(),
            'isRecent': self.is_recent(),
            'user': {
                'id': self.notification_owner.id,
                'firstName': self.notification_owner.first_name,
                'lastName': self.notification_owner.last_name
            } if self.notification_owner else None
        }