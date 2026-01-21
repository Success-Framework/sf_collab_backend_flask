from app.extensions import db
from datetime import datetime

class StartupDocument(db.Model):
    __tablename__ = 'startup_documents'
    
    id = db.Column(db.Integer, primary_key=True)
    startup_id = db.Column(db.Integer, db.ForeignKey('startups.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)  # Path to file in file system
    file_url = db.Column(db.String(500))  # Add this field
    content_type = db.Column(db.String(100), nullable=False)
    document_type = db.Column(db.String(50), default='general')
    file_size = db.Column(db.Integer)  # Size in bytes
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    visible_by = db.Column(db.String(50), default='all')  # 'public', 'team', 'private'
    # Relationship
    parent_startup = db.relationship('Startup', back_populates='startup_documents', foreign_keys=[startup_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'content_type': self.content_type,
            'document_type': self.document_type,
            'file_size': self.file_size,
            'uploaded_at': self.uploaded_at.isoformat(),
            'download_url': f'/api/startups/{self.startup_id}/documents/{self.id}/download',
            "file_url":self.file_url or f'/api/startups/{self.startup_id}/documents/{self.id}/download',
            'visible_by': self.visible_by,
        }