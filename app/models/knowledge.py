from datetime import datetime
from app.extensions import db
from sqlalchemy import Enum, JSON
from .Enums import ResourceStatus
from .knowledgeComment import KnowledgeComment

class Knowledge(db.Model):
    __tablename__ = 'knowledge'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    title_description = db.Column(db.Text, nullable=False)
    content_preview = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    file_url = db.Column(db.String(500), nullable=True)
    tags = db.Column(JSON, default=[])
    
    # Author info
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    author_first_name = db.Column(db.String(100))
    author_last_name = db.Column(db.String(100))
    
    status = db.Column(Enum(ResourceStatus), default=ResourceStatus.active)
    views = db.Column(db.Integer, default=0)
    downloads = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    
    # Image storage
    image_buffer = db.Column(db.LargeBinary, nullable=True)
    image_content_type = db.Column(db.String(100), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - ALL CORRECTED
    # author relationship defined in User model as 'knowledge_author'
    knowledge_author=db.relationship('User', back_populates='knowledge_posts', foreign_keys=[author_id])
    
    knowledge_comments = db.relationship('KnowledgeComment', 
        back_populates='knowledge_resource', 
        lazy='dynamic', 
        cascade='all, delete-orphan',
        foreign_keys='KnowledgeComment.resource_id')
    
    bookmarks = db.relationship('KnowledgeBookmark', 
        back_populates='knowledge', 
        lazy='dynamic', 
        cascade='all, delete-orphan',
        foreign_keys='KnowledgeBookmark.knowledge_id')
    
    resource_downloads = db.relationship('ResourceDownload',
        back_populates='knowledge_resource',
        lazy='dynamic',
        foreign_keys='ResourceDownload.resource_id',
        cascade='all, delete-orphan')
    
    resource_likes = db.relationship('ResourceLike',
        back_populates='knowledge_resource',
        lazy='dynamic',
        foreign_keys='ResourceLike.resource_id',
        cascade='all, delete-orphan')
    
    views_list = db.relationship('ResourceView',
        back_populates='knowledge_resource',
        lazy='dynamic',
        foreign_keys='ResourceView.resource_id',
        cascade='all, delete-orphan')
    
    # HELPER FUNCTIONS
    def increment_views(self):
        """Increment view count"""
        self.views += 1
        db.session.commit()
    
    def increment_downloads(self):
        """Increment download count"""
        self.downloads += 1
        db.session.commit()
    
    def increment_likes(self):
        """Increment like count"""
        self.likes += 1
        db.session.commit()
    
    def decrement_likes(self):
        """Decrement like count"""
        if self.likes > 0:
            self.likes -= 1
        db.session.commit()
    
    def add_tag(self, tag):
        """Add tag to knowledge"""
        if not self.tags:
            self.tags = []
        if tag not in self.tags:
            self.tags.append(tag)
        db.session.commit()
    
    def remove_tag(self, tag):
        """Remove tag from knowledge"""
        if self.tags and tag in self.tags:
            self.tags.remove(tag)
        db.session.commit()
    
    def update_status(self, new_status):
        """Update knowledge status"""
        self.status = ResourceStatus(new_status)
        db.session.commit()
    
    def get_comments_count(self):
        """Get number of comments"""
        return self.comments.count()
    
    def get_bookmarks_count(self):
        """Get number of bookmarks"""
        return self.bookmarks.count()
    
    def is_bookmarked_by_user(self, user_id):
        """Check if knowledge is bookmarked by user"""
        return self.bookmarks.filter_by(user_id=user_id).first() is not None
    
    def _enum_to_value(self,value):
        return value.value if hasattr(value, "value") else value
        
    def to_dict(self, include_comments=False, include_author_details=True):
        data = {
            'id': self.id,
            'title': self.title,
            'titleDescription': self.title_description,
            'contentPreview': self.content_preview,
            'category': self.category,
            'fileUrl': self.file_url,
            'tags': self.tags or [],
            'author': {
                'id': self.author_id,
                'firstName': self.author_first_name,
                'lastName': self.author_last_name
            },
            'status': self._enum_to_value(self.status.value),
            'views': self.views,
            'downloads': self.downloads,
            'likes': self.likes,
            'commentsCount': self.get_comments_count(),
            'bookmarksCount': self.get_bookmarks_count(),
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat()
        }
        
        if include_author_details and self.knowledge_author:
            data['author']['profilePicture'] = self.knowledge_author.profile_picture
            data['author']['company'] = self.knowledge_author.profile_company
        
        if include_comments:
            data['comments'] = [comment.to_dict() for comment in self.comments.order_by(KnowledgeComment.created_at.desc()).all()]
        
        return data