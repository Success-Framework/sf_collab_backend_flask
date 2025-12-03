from datetime import datetime
from app.extensions import db
# from sqlalchemy import Enum
# from .Enums import SuggestionStatus

class PostComment(db.Model):
    __tablename__ = 'post_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    author_first_name = db.Column(db.String(100))
    author_last_name = db.Column(db.String(100))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parent_post = db.relationship('Post', back_populates='post_comments', foreign_keys=[post_id])
    comment_author = db.relationship('User', back_populates='post_comments_list', foreign_keys=[author_id])
    
    # HELPER FUNCTIONS
    
    def update_content(self, new_content):
        """Update comment content"""
        self.content = new_content
        db.session.commit()
    
    def get_author_name(self):
        """Get author's full name"""
        return f"{self.author_first_name} {self.author_last_name}"
    
    def get_post_content_preview(self):
        """Get post content preview"""
        if self.post:
            return self.post.content[:100] + '...' if len(self.post.content) > 100 else self.post.content
        return None
    
    def is_recent(self, hours=24):
        """Check if comment is recent"""
        time_diff = datetime.utcnow() - self.created_at
        return time_diff.total_seconds() <= hours * 3600
    
    def to_dict(self):
        return {
            'id': self.id,
            'postId': self.post_id,
            'content': self.content,
            'author': {
                'id': self.author_id,
                'firstName': self.author_first_name,
                'lastName': self.author_last_name,
                'fullName': self.get_author_name(),
                'profilePicture': self.author.profile_picture if self.author else None
            },
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat(),
            'isRecent': self.is_recent(),
            'postContentPreview': self.get_post_content_preview()
        }