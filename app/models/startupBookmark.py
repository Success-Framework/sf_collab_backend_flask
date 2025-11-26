from datetime import datetime
from app.extensions import db

class StartupBookmark(db.Model):
    __tablename__ = 'startup_bookmarks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    startup_id = db.Column(db.Integer, db.ForeignKey('startups.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(255))
    content_preview = db.Column(db.Text)
    url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    bookmark_owner = db.relationship('User', back_populates='startup_bookmarks',foreign_keys=[user_id])
    bookmarked_startup = db.relationship('Startup', back_populates='startup_bookmarks',foreign_keys=[startup_id])
    
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
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'startup_id': self.startup_id,
            'title': self.title,
            'content_preview': self.content_preview,
            'url': self.url,
            'created_at': self.created_at.isoformat(),
            'startup': {
                'id': self.startup.id,
                'name': self.startup.name,
                'industry': self.startup.industry
            } if self.startup else None
        }