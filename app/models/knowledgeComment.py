from datetime import datetime
from app.extensions import db

class KnowledgeComment(db.Model):
    __tablename__ = 'knowledge_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('knowledge.id', ondelete='CASCADE'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    author_first_name = db.Column(db.String(100))
    author_last_name = db.Column(db.String(100))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    knowledge_resource = db.relationship('Knowledge', back_populates='knowledge_comments', foreign_keys=[resource_id])
    comment_author = db.relationship('User', back_populates='knowledge_comments', foreign_keys=[author_id])
    
    # HELPER FUNCTIONS
    
    def update_content(self, new_content):
        """Update comment content"""
        self.content = new_content
        db.session.commit()
    
    def get_author_name(self):
        """Get author's full name"""
        return f"{self.author_first_name} {self.author_last_name}"
    
    def get_knowledge_title(self):
        """Get knowledge post title"""
        return self.knowledge.title if self.knowledge else None
    
    def to_dict(self):
        return {
            'id': self.id,
            'resourceId': self.resource_id,
            'content': self.content,
            'author': {
                'id': self.author_id,
                'firstName': self.author_first_name,
                'lastName': self.author_last_name,
                'fullName': self.get_author_name(),
                'profilePicture': self.author.profile_picture if self.author else None
            },
            'knowledgeTitle': self.get_knowledge_title(),
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat()
        }