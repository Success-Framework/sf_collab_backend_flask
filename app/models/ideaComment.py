from datetime import datetime
from app.extensions import db

class IdeaComment(db.Model):
    __tablename__ = 'idea_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    idea_id = db.Column(db.Integer, db.ForeignKey('ideas.id', ondelete='CASCADE'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    author_first_name = db.Column(db.String(100))
    author_last_name = db.Column(db.String(100))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    #! Relationships
    comment_author = db.relationship('User', back_populates='idea_comments', foreign_keys=[author_id])
    parent_idea = db.relationship('Idea', back_populates='idea_comments', foreign_keys=[idea_id])
    
    #! HELPER FUNCTIONS
    
    def update_content(self, new_content):
        """Update comment content"""
        self.content = new_content
        db.session.commit()
    
    def get_author_name(self):
        """Get author's full name"""
        return f"{self.author_first_name} {self.author_last_name}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'ideaId': self.idea_id,
            'content': self.content,
            'author': {
                'id': self.author_id,
                'firstName': self.author_first_name,
                'lastName': self.author_last_name,
                'fullName': self.get_author_name()
            },
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat()
        }