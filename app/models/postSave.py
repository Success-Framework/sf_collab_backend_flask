from datetime import datetime
from app.extensions import db

class PostSave(db.Model):
    __tablename__ = 'post_saves'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    saved_post = db.relationship('Post', back_populates='post_saves', foreign_keys=[post_id])
    save_owner = db.relationship('User', back_populates='post_saves', foreign_keys=[user_id])
    
    # HELPER FUNCTIONS
    
    def get_time_since_save(self):
        """Get time since save was created"""
        return datetime.utcnow() - self.saved_at
    
    def is_recent(self, minutes=30):
        """Check if save is recent"""
        time_diff = datetime.utcnow() - self.saved_at
        return time_diff.total_seconds() <= minutes * 60
    
    def save(self):
        """Save the post save to the database"""
        db.session.add(self)
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'postId': self.post_id,
            'userId': self.user_id,
            'savedAt': self.saved_at.isoformat(),
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat(),
            'timeSinceSave': str(self.get_time_since_save()),
            'isRecent': self.is_recent(),
            'user': {
                'id': self.save_owner.id,
                'firstName': self.save_owner.first_name,
                'lastName': self.save_owner.last_name,
                'profilePicture': self.save_owner.profile_picture
            } if self.save_owner else None,
            'post': {
                'id': self.saved_post.id,
                'content': self.saved_post.content[:100] + '...' if len(self.saved_post.content) > 100 else self.saved_post.content
            } if self.saved_post else None
        }