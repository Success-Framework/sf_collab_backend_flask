from datetime import datetime
from app.extensions import db

class KnowledgeBookmark(db.Model):
    __tablename__ = 'knowledge_bookmarks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    knowledge_id = db.Column(db.Integer, db.ForeignKey('knowledge.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(255))
    content_preview = db.Column(db.Text)
    url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    bookmark_owner = db.relationship('User', back_populates='knowledge_bookmarks', foreign_keys=[user_id])
    knowledge = db.relationship('Knowledge', back_populates='bookmarks', foreign_keys=[knowledge_id])
    
    # HELPER FUNCTIONS
    
    def update_content(self, title=None, content_preview=None, url=None):
        """Update bookmark content"""
        if title:
            self.title = title
        if content_preview:
            self.content_preview = content_preview
        if url:
            self.url = url
        db.session.commit()
    
    def get_knowledge_details(self):
        """Get knowledge post details"""
        if self.knowledge:
            return {
                'title': self.knowledge.title,
                'category': self.knowledge.category,
                'author': f"{self.knowledge.author_first_name} {self.knowledge.author_last_name}",
                'views': self.knowledge.views,
                'likes': self.knowledge.likes
            }
        return None
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'knowledge_id': self.knowledge_id,
            'title': self.title,
            'content_preview': self.content_preview,
            'url': self.url,
            'created_at': self.created_at.isoformat(),
            'knowledge': self.get_knowledge_details(),
            'user': {
                'id': self.user.id,
                'firstName': self.user.first_name,
                'lastName': self.user.last_name
            } if self.user else None
        }