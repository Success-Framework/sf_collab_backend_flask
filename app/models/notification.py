"""
SF Collab Notification Model
Updated to support all notification types from documentation (4.1 - 4.12)
"""

from datetime import datetime
from app.extensions import db
from sqlalchemy import JSON


class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    actor_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    
    # Notification content
    notification_type = db.Column(db.String(50), default='info')  # success, info, warning, error
    category = db.Column(db.String(50), default='system')  # account, social, idea, startup, task, etc.
    priority = db.Column(db.String(20), default='medium')  # critical, high, medium, low
    
    title = db.Column(db.String(255))
    message = db.Column(db.Text)
    
    # Entity reference (what this notification is about)
    entity_type = db.Column(db.String(50), nullable=True)  # idea, task, startup, post, message, etc.
    entity_id = db.Column(db.Integer, nullable=True)
    
    # Additional metadata
    data = db.Column(JSON, default=dict)
    
    # Read status
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime, nullable=True)
    
    # Email/Push tracking
    email_sent = db.Column(db.Boolean, default=False)
    email_sent_at = db.Column(db.DateTime, nullable=True)
    push_sent = db.Column(db.Boolean, default=False)
    push_sent_at = db.Column(db.DateTime, nullable=True)
    link_url = db.Column(db.String(500), nullable=True)
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    notification_owner = db.relationship(
        'User', 
        back_populates='notifications', 
        foreign_keys=[user_id]
    )
    actor = db.relationship(
        'User', 
        foreign_keys=[actor_id],
        backref='triggered_notifications'
    )
    
    # ===== HELPER METHODS =====
    
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
            return self.data.get(key) if self.data else None
        return self.data or {}
    
    def get_priority_level(self):
        """Get numeric priority level for sorting"""
        priority_map = {
            'critical': 4,
            'high': 3,
            'medium': 2,
            'low': 1
        }
        return priority_map.get(self.priority, 2)
    
    def to_dict(self):
        """Convert notification to dictionary"""
        actor_info = None
        if self.actor:
            actor_info = {
                'id': self.actor.id,
                'firstName': self.actor.first_name,
                'lastName': self.actor.last_name,
                'profilePicture': self.actor.profile_picture
            }
        
        return {
            'id': self.id,
            'userId': self.user_id,
            'actorId': self.actor_id,
            'actor': actor_info,
            'type': self.notification_type,
            'category': self.category,
            'priority': self.priority,
            'title': self.title,
            'message': self.message,
            'entityType': self.entity_type,
            'entityId': self.entity_id,
            'data': self.data or {},
            'isRead': self.is_read,
            'readAt': self.read_at.isoformat() if self.read_at else None,
            'emailSent': self.email_sent,
            'pushSent': self.push_sent,
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat(),
            'linkUrl': self.link_url,
            'isRecent': self.is_recent(),
            'priorityLevel': self.get_priority_level(),
            'user': {
                'id': self.notification_owner.id,
                'firstName': self.notification_owner.first_name,
                'lastName': self.notification_owner.last_name,
                'profilePicture': self.notification_owner.profile_picture
            } if self.notification_owner else None
        }
    
    def __repr__(self):
        return f'<Notification {self.id}: {self.title}>'