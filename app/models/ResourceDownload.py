from datetime import datetime
from app.extensions import db

class ResourceDownload(db.Model):
    __tablename__ = 'resource_downloads'
    
    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('knowledge.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    downloaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - ALL CORRECTED
    # resource relationship defined in Knowledge model as 'knowledge_resource'
    knowledge_resource = db.relationship('Knowledge', back_populates='resource_downloads', foreign_keys=[resource_id])
    
    # user relationship defined in User model as 'download_owner'
    download_owner = db.relationship('User', back_populates='resource_downloads', foreign_keys=[user_id])
    
    # HELPER FUNCTIONS
    def get_time_since_download(self):
        """Get time since download was created"""
        return datetime.utcnow() - self.downloaded_at
    
    def is_recent(self, hours=24):
        """Check if download is recent"""
        time_diff = datetime.utcnow() - self.downloaded_at
        return time_diff.total_seconds() <= hours * 3600
    
    def get_resource_details(self):
        """Get resource details"""
        if self.knowledge_resource:
            return {
                'title': self.knowledge_resource.title,
                'category': self.knowledge_resource.category,
                'author': f"{self.knowledge_resource.author_first_name} {self.knowledge_resource.author_last_name}",
                'file_url': self.knowledge_resource.file_url
            }
        return None
    
    def to_dict(self):
        return {
            'id': self.id,
            'resource_id': self.resource_id,
            'user_id': self.user_id,
            'downloaded_at': self.downloaded_at.isoformat(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'time_since_download': str(self.get_time_since_download()),
            'is_recent': self.is_recent(),
            'resource': self.get_resource_details(),
            'user': {
                'id': self.download_owner.id,
                'firstName': self.download_owner.first_name,
                'lastName': self.download_owner.last_name,
                'email': self.download_owner.email
            } if self.download_owner else None
        }