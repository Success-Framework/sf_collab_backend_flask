from datetime import datetime
from app.extensions import db

class ResourceView(db.Model):
    __tablename__ = 'resource_views'
    
    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('knowledge.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    knowledge_resource = db.relationship('Knowledge', back_populates='views_list', foreign_keys=[resource_id])
    view_owner = db.relationship('User', back_populates='resource_views', foreign_keys=[user_id])
    
    # HELPER FUNCTIONS
    
    def get_time_since_view(self):
        """Get time since view was created"""
        return datetime.utcnow() - self.viewed_at
    
    def is_recent(self, hours=24):
        """Check if view is recent"""
        time_diff = datetime.utcnow() - self.viewed_at
        return time_diff.total_seconds() <= hours * 3600
    
    def get_resource_details(self):
        """Get resource details"""
        if self.resource:
            return {
                'title': self.resource.title,
                'category': self.resource.category,
                'author': f"{self.resource.author_first_name} {self.resource.author_last_name}",
                'views_count': self.resource.views
            }
        return None
    
    def to_dict(self):
        return {
            'id': self.id,
            'resource_id': self.resource_id,
            'user_id': self.user_id,
            'viewed_at': self.viewed_at.isoformat(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'time_since_view': str(self.get_time_since_view()),
            'is_recent': self.is_recent(),
            'resource': self.get_resource_details(),
            'user': {
                'id': self.user.id,
                'firstName': self.user.first_name,
                'lastName': self.user.last_name
            } if self.user else None
        }