from datetime import datetime
from app.extensions import db

class PostLike(db.Model):
    __tablename__ = 'post_likes'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    liked_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    liked_post = db.relationship('Post', back_populates='post_likes', foreign_keys=[post_id])
    like_owner = db.relationship('User', back_populates='post_likes', foreign_keys=[user_id])
    
    # HELPER FUNCTIONS
    
    def get_time_since_like(self):
        """Get time since like was created"""
        return datetime.utcnow() - self.liked_at
    
    def is_recent(self, minutes=30):
        """Check if like is recent"""
        time_diff = datetime.utcnow() - self.liked_at
        return time_diff.total_seconds() <= minutes * 60
    
    def to_dict(self):
        return {
            'id': self.id,
            'postId': self.post_id,
            'userId': self.user_id,
            'likedAt': self.liked_at.isoformat(),
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat(),
            'timeSinceLike': str(self.get_time_since_like()),
            'isRecent': self.is_recent(),
            'user': {
                'id': self.like_owner.id,
                'firstName': self.like_owner.first_name,
                'lastName': self.like_owner.last_name,
                'profilePicture': self.like_owner.profile_picture
            } if self.like_owner else None,
            'post': {
                'id': self.liked_post.id,
                'content': self.liked_post.content[:100] + '...' if len(self.liked_post.content) > 100 else self.liked_post.content
            } if self.liked_post else None
        }