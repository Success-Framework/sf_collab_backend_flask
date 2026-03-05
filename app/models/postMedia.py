from datetime import datetime
from app.extensions import db

class PostMedia(db.Model):
    __tablename__ = 'post_media'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False)
    data = db.Column(db.LargeBinary)
    content_type = db.Column(db.String(100))
    file_name = db.Column(db.String(255))
    file_size = db.Column(db.Integer)  # Size in bytes
    caption = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parent_post = db.relationship('Post', back_populates='media_items', foreign_keys=[post_id])
    
    # HELPER FUNCTIONS
    
    def get_file_size_formatted(self):
        """Get formatted file size"""
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        else:
            return f"{self.file_size / (1024 * 1024):.1f} MB"
    
    def is_image(self):
        """Check if media is an image"""
        return self.content_type and self.content_type.startswith('image/')
    
    def is_video(self):
        """Check if media is a video"""
        return self.content_type and self.content_type.startswith('video/')
    
    def is_document(self):
        """Check if media is a document"""
        return self.content_type and (
            self.content_type.startswith('application/') or 
            self.content_type in ['text/plain', 'text/html']
        )
    
    def get_media_type(self):
        """Get media type category"""
        if self.is_image():
            return 'image'
        elif self.is_video():
            return 'video'
        elif self.is_document():
            return 'document'
        else:
            return 'other'
    
    def update_caption(self, new_caption):
        """Update media caption"""
        self.caption = new_caption
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'postId': self.post_id,
            'contentType': self.content_type,
            'fileName': self.file_name,
            'fileSize': self.file_size,
            'fileSizeFormatted': self.get_file_size_formatted(),
            'caption': self.caption,
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat(),
            'mediaType': self.get_media_type(),
            'isImage': self.is_image(),
            'isVideo': self.is_video(),
            'isDocument': self.is_document(),
            'post': {
                'id': self.parent_post.id,
                'content': self.parent_post.content[:100] + '...' if len(self.parent_post.content) > 100 else self.parent_post.content
            } if self.parent_post else None
        }