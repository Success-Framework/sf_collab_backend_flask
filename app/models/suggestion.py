from datetime import datetime
from app.extensions import db
from sqlalchemy import Enum
from app.models.Enums import SuggestionStatus

class Suggestion(db.Model):
    __tablename__ = 'suggestions'
    
    id = db.Column(db.Integer, primary_key=True)
    idea_id = db.Column(db.Integer, db.ForeignKey('ideas.id', ondelete='CASCADE'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    author_first_name = db.Column(db.String(100))
    author_last_name = db.Column(db.String(100))
    
    status = db.Column(Enum(SuggestionStatus), default=SuggestionStatus.pending)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parent_idea = db.relationship('Idea', back_populates='suggestions', foreign_keys=[idea_id])
    suggestion_author = db.relationship('User', back_populates='suggestions', foreign_keys=[author_id])
    
    # HELPER FUNCTIONS
    
    def update_status(self, new_status):
        """Update suggestion status"""
        self.status = SuggestionStatus(new_status)
        db.session.commit()
    
    def approve(self):
        """Approve suggestion"""
        self.update_status('approved')
    
    def reject(self):
        """Reject suggestion"""
        self.update_status('rejected')
    
    def get_author_name(self):
        """Get author's full name"""
        return f"{self.author_first_name} {self.author_last_name}"
    
    def get_idea_details(self):
        """Get idea details"""
        if self.idea:
            return {
                'title': self.idea.title,
                'description': self.idea.description,
                'industry': self.idea.industry,
                'stage': self.idea.stage
            }
        return None
    
    def is_pending(self):
        """Check if suggestion is pending"""
        return self.status == SuggestionStatus.pending
    
    def is_approved(self):
        """Check if suggestion is approved"""
        return self.status == SuggestionStatus.approved
    
    def is_rejected(self):
        """Check if suggestion is rejected"""
        return self.status == SuggestionStatus.rejected
    
    def _enum_to_value(self,value):
        return value.value if hasattr(value, "value") else value
        
    def to_dict(self):
        return {
            'id': self.id,
            'ideaId': self.idea_id,
            'content': self.content,
            'author': {
                'id': self.author_id,
                'firstName': self.author_first_name,
                'lastName': self.author_last_name,
                'fullName': self.get_author_name(),
                'profilePicture': self.author.profile_picture if self.author else None
            },
            'status': self._enum_to_value(self.status.value),
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat(),
            'isPending': self.is_pending(),
            'isApproved': self.is_approved(),
            'isRejected': self.is_rejected(),
            'idea': self.get_idea_details()
        }