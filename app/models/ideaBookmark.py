from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from sqlalchemy import Enum
from app.extensions import db

class IdeaBookmark(db.Model):
    __tablename__ = 'idea_bookmarks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    idea_id = db.Column(db.Integer, db.ForeignKey('ideas.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(255))
    content_preview = db.Column(db.Text)
    url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    #! Relationships
    bookmark_owner = db.relationship('User', back_populates='idea_bookmarks', foreign_keys=[user_id])
    bookmarked_idea = db.relationship('Idea', back_populates='idea_bookmarks', foreign_keys=[idea_id])
    
    #! HELPER FUNCTIONS
    
    def update_content(self, title=None, content_preview=None, url=None):
        """Update bookmark content"""
        if title:
            self.title = title
        if content_preview:
            self.content_preview = content_preview
        if url:
            self.url = url
        db.session.commit()
    def count(self):
        """Count total bookmarks for an idea"""
        return IdeaBookmark.query.filter_by(idea_id=self.idea_id).count()
    def get_idea_details(self):
        """Get idea details"""
        if self.bookmarked_idea:
            return {
                'title': self.bookmarked_idea.title,
                'description': self.bookmarked_idea.description,
                'industry': self.bookmarked_idea.industry,
                'stage': self.bookmarked_idea.stage,
                'creator': f"{self.bookmarked_idea.creator_first_name} {self.bookmarked_idea.creator_last_name}",
                'likes': self.bookmarked_idea.likes,
                'views': self.bookmarked_idea.views
            }
        return None
    
    def is_recent(self, days=7):
        """Check if bookmark is recent"""
        time_diff = datetime.utcnow() - self.created_at
        return time_diff.days <= days
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'idea_id': self.idea_id,
            'title': self.title,
            'content_preview': self.content_preview,
            'url': self.url,
            'created_at': self.created_at.isoformat(),
            'idea': self.get_idea_details(),
            'is_recent': self.is_recent(),
            'user': {
                'id': self.bookmark_owner.id,
                'firstName': self.bookmark_owner.first_name,
                'lastName': self.bookmark_owner.last_name
            } if self.bookmark_owner else None
        }