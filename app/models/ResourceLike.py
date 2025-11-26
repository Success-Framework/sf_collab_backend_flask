from datetime import datetime
from app.extensions import db

class ResourceLike(db.Model):
    __tablename__ = 'resource_likes'
    
    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('knowledge.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    liked_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - ALL CORRECTED
    # resource relationship defined in Knowledge model as 'knowledge_resource'
    knowledge_resource = db.relationship('Knowledge', back_populates='resource_likes', foreign_keys=[resource_id])
    
    # user relationship defined in User model as 'like_owner'
    like_owner = db.relationship('User', back_populates='resource_likes', foreign_keys=[user_id])
    
    # HELPER FUNCTIONS
    def get_time_since_like(self):
        """Get time since like was created"""
        return datetime.utcnow() - self.liked_at
    
    def is_recent(self, minutes=30):
        """Check if like is recent"""
        time_diff = datetime.utcnow() - self.liked_at
        return time_diff.total_seconds() <= minutes * 60
    
    def get_resource_details(self):
        """Get resource details"""
        if self.knowledge_resource:
            return {
                'title': self.knowledge_resource.title,
                'category': self.knowledge_resource.category,
                'author': f"{self.knowledge_resource.author_first_name} {self.knowledge_resource.author_last_name}",
                'likes_count': self.knowledge_resource.likes
            }
        return None
    
    def to_dict(self):
        return {
            'id': self.id,
            'resource_id': self.resource_id,
            'user_id': self.user_id,
            'liked_at': self.liked_at.isoformat(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'time_since_like': str(self.get_time_since_like()),
            'is_recent': self.is_recent(),
            'resource': self.get_resource_details(),
            'user': {
                'id': self.like_owner.id,
                'firstName': self.like_owner.first_name,
                'lastName': self.like_owner.last_name
            } if self.like_owner else None
        }