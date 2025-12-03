from datetime import datetime
from app.extensions import db
from sqlalchemy import Enum, JSON
from .Enums import PostType
from .postComment import PostComment

class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    author_first_name = db.Column(db.String(100))
    author_last_name = db.Column(db.String(100))
    
    content = db.Column(db.Text, nullable=False)
    type = db.Column(Enum(PostType), default=PostType.professional)
    tags = db.Column(JSON, default=[])
    
    likes = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    shares = db.Column(db.Integer, default=0)
    saves = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - ALL CORRECTED
    # user and author relationships defined in User model
    post_author = db.relationship('User', back_populates='authored_posts', foreign_keys=[user_id])
    
    post_likes = db.relationship('PostLike', 
        back_populates='liked_post', 
        lazy='dynamic', 
        cascade='all, delete-orphan',
        foreign_keys='PostLike.post_id')
    
    post_comments = db.relationship('PostComment', 
        back_populates='parent_post', 
        lazy='dynamic', 
        cascade='all, delete-orphan',
        foreign_keys='PostComment.post_id')
    
    media_items = db.relationship('PostMedia', 
        back_populates='parent_post', 
        lazy='dynamic', 
        cascade='all, delete-orphan',
        foreign_keys='PostMedia.post_id')
    
    # HELPER FUNCTIONS
    def increment_likes(self):
        """Increment like count"""
        self.likes += 1
        db.session.commit()
    
    def decrement_likes(self):
        """Decrement like count"""
        if self.likes > 0:
            self.likes -= 1
        db.session.commit()
    
    def increment_comments(self):
        """Increment comment count"""
        self.comments_count += 1
        db.session.commit()
    
    def decrement_comments(self):
        """Decrement comment count"""
        if self.comments_count > 0:
            self.comments_count -= 1
        db.session.commit()
    
    def increment_shares(self):
        """Increment share count"""
        self.shares += 1
        db.session.commit()
    
    def increment_saves(self):
        """Increment save count"""
        self.saves += 1
        db.session.commit()
    
    def add_tag(self, tag):
        """Add tag to post"""
        if not self.tags:
            self.tags = []
        if tag not in self.tags:
            self.tags.append(tag)
        db.session.commit()
    
    def remove_tag(self, tag):
        """Remove tag from post"""
        if self.tags and tag in self.tags:
            self.tags.remove(tag)
        db.session.commit()
    
    def is_liked_by_user(self, user_id):
        """Check if post is liked by user"""
        return self.post_likes.filter_by(user_id=user_id).first() is not None
    
    def get_recent_comments(self, limit=5):
        """Get recent comments"""
        return self.post_comments.order_by(PostComment.created_at.desc()).limit(limit).all()
    
    def get_media_count(self):
        """Get number of media items"""
        return self.media_items.count()
    
    def _enum_to_value(self,value):
        return value.value if hasattr(value, "value") else value
        
    def to_dict(self, include_comments=False, include_media=False, user_id=None):
        data = {
            'id': self.id,
            'userId': self.user_id,
            'author': {
                'id': self.author_id,
                'firstName': self.author_first_name,
                'lastName': self.author_last_name,
                'profilePicture': self.post_author.profile_picture if self.post_author else None
            },
            'content': self.content,
            'type': self._enum_to_value(self.type.value),
            'tags': self.tags or [],
            'likes': self.likes,
            'commentsCount': self.comments_count,
            'shares': self.shares,
            'saves': self.saves,
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat(),
            'mediaCount': self.get_media_count()
        }
        
        if user_id:
            data['isLiked'] = self.is_liked_by_user(user_id)
        
        if include_comments:
            data['comments'] = [comment.to_dict() for comment in self.get_recent_comments()]
        
        if include_media:
            data['media'] = [media.to_dict() for media in self.media_items.all()]
        
        return data