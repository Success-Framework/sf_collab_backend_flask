from datetime import datetime
from app.extensions import db
from sqlalchemy import Enum
from .Enums import StoryType
from .storyView import StoryView

class Story(db.Model):
    __tablename__ = 'stories'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    author_first_name = db.Column(db.String(100))
    author_last_name = db.Column(db.String(100))
    
    media_url = db.Column(db.String(500), nullable=False)
    caption = db.Column(db.Text)
    type = db.Column(Enum(StoryType), default=StoryType.image)
    
    views = db.Column(db.Integer, default=0)
    expires_at = db.Column(db.DateTime, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - ALL CORRECTED
    # user and author relationships defined in User model
    story_author = db.relationship('User', back_populates='stories', foreign_keys=[user_id])
    
    views_list = db.relationship('StoryView', 
        back_populates='viewed_story', 
        lazy='dynamic', 
        cascade='all, delete-orphan',
        foreign_keys='StoryView.story_id')
    
    # HELPER FUNCTIONS
    def increment_views(self):
        """Increment view count"""
        self.views += 1
        db.session.commit()
    
    def is_expired(self):
        """Check if story has expired"""
        return datetime.utcnow() > self.expires_at
    
    def get_time_until_expiry(self):
        """Get time until story expires"""
        return self.expires_at - datetime.utcnow()
    
    def is_active(self):
        """Check if story is still active (not expired)"""
        return not self.is_expired()
    
    def get_viewers_count(self):
        """Get number of unique viewers"""
        return self.story_views.count()
    
    def get_recent_viewers(self, limit=10):
        """Get recent viewers"""
        return self.story_views.order_by(StoryView.viewed_at.desc()).limit(limit).all()
    
    def has_user_viewed(self, user_id):
        """Check if user has viewed this story"""
        return self.story_views.filter_by(user_id=user_id).first() is not None
    
    def to_dict(self, include_viewers=False, user_id=None):
        data = {
            'id': self.id,
            'userId': self.user_id,
            'author': {
                'id': self.author_id,
                'firstName': self.author_first_name,
                'lastName': self.author_last_name,
                'profilePicture': self.story_author.profile_picture if self.story_author else None
            },
            'mediaUrl': self.media_url,
            'caption': self.caption,
            'type': self.type.value,
            'views': self.views,
            'expiresAt': self.expires_at.isoformat(),
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat(),
            'isExpired': self.is_expired(),
            'isActive': self.is_active(),
            'timeUntilExpiry': str(self.get_time_until_expiry()) if not self.is_expired() else None,
            'uniqueViewers': self.get_viewers_count()
        }
        
        if user_id:
            data['hasViewed'] = self.has_user_viewed(user_id)
        
        if include_viewers:
            data['recentViewers'] = [view.to_dict() for view in self.get_recent_viewers()]
        
        return data