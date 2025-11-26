from datetime import datetime
from app.extensions import db

class StoryView(db.Model):
    __tablename__ = 'story_views'
    
    id = db.Column(db.Integer, primary_key=True)
    story_id = db.Column(db.Integer, db.ForeignKey('stories.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    viewed_story = db.relationship('Story', back_populates='views_list', foreign_keys=[story_id])
    view_owner = db.relationship('User', back_populates='story_views', foreign_keys=[user_id])
    
    # HELPER FUNCTIONS
    
    def get_time_since_view(self):
        """Get time since view was created"""
        return datetime.utcnow() - self.viewed_at
    
    def is_recent(self, minutes=30):
        """Check if view is recent"""
        time_diff = datetime.utcnow() - self.viewed_at
        return time_diff.total_seconds() <= minutes * 60
    
    def get_story_details(self):
        """Get story details"""
        if self.story:
            return {
                'media_url': self.story.media_url,
                'caption': self.story.caption,
                'type': self.story.type.value,
                'author': f"{self.story.author_first_name} {self.story.author_last_name}"
            }
        return None
    
    def to_dict(self):
        return {
            'id': self.id,
            'story_id': self.story_id,
            'user_id': self.user_id,
            'viewed_at': self.viewed_at.isoformat(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'time_since_view': str(self.get_time_since_view()),
            'is_recent': self.is_recent(),
            'story': self.get_story_details(),
            'user': {
                'id': self.user.id,
                'firstName': self.user.first_name,
                'lastName': self.user.last_name,
                'profilePicture': self.user.profile_picture
            } if self.user else None
        }