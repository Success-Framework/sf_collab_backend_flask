from datetime import datetime
from app.extensions import db
from sqlalchemy import Enum, JSON
from .Enums import ResourceStatus, Privacy
from .ideaComment import IdeaComment

class Idea(db.Model):
    __tablename__ = 'ideas'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    project_details = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    industry = db.Column(db.String(100), nullable=False)
    stage = db.Column(db.String(100), nullable=False)
    tags = db.Column(JSON, default=[])
    privacy = db.Column(Enum(Privacy), default=Privacy.public)
    image_url = db.Column(db.String(255), nullable=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    creator_first_name = db.Column(db.String(100))
    creator_last_name = db.Column(db.String(100))
    
    status = db.Column(Enum(ResourceStatus), default=ResourceStatus.active)
    likes = db.Column(db.Integer, default=0)
    views = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    #! Relationships
    idea_creator = db.relationship(
        'User',
        back_populates='ideas',
        foreign_keys=[creator_id]
    )

    team_members = db.relationship('TeamMember', 
        back_populates='parent_idea', 
        lazy='dynamic', 
        cascade='all, delete-orphan',
        foreign_keys='TeamMember.idea_id')
    
    idea_comments = db.relationship('IdeaComment', 
        back_populates='parent_idea', 
        lazy='dynamic', 
        cascade='all, delete-orphan',
        foreign_keys='IdeaComment.idea_id')
    
    suggestions = db.relationship('Suggestion', 
        back_populates='parent_idea', 
        lazy='dynamic', 
        cascade='all, delete-orphan',
        foreign_keys='Suggestion.idea_id')
    
    idea_bookmarks = db.relationship('IdeaBookmark',
        back_populates='bookmarked_idea',
        lazy='dynamic',
        cascade='all, delete-orphan',
        foreign_keys='IdeaBookmark.idea_id')
    
    # HELPER FUNCTIONS
    def increment_views(self):
        """Increment view count"""
        self.views += 1
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
    
    def add_team_member(self, name, position, skills=None):
        """Add team member to idea"""
        from models.teamMember import TeamMember
        member = TeamMember(
            idea_id=self.id,
            name=name,
            position=position,
            skills=skills or {}
        )
        db.session.add(member)
        db.session.commit()
        return member
    
    def add_tag(self, tag):
        """Add tag to idea"""
        if not self.tags:
            self.tags = []
        if tag not in self.tags:
            self.tags.append(tag)
        db.session.commit()
    
    def remove_tag(self, tag):
        """Remove tag from idea"""
        if self.tags and tag in self.tags:
            self.tags.remove(tag)
        db.session.commit()
    
    def update_stage(self, new_stage):
        """Update idea stage"""
        self.stage = new_stage
        db.session.commit()
    
    def get_comments_count(self):
        """Get number of comments"""
        return self.idea_comments.count()
    
    def get_team_size(self):
        """Get number of team members"""
        return self.team_members.count()
        
    def _enum_to_value(self,value):
        return value.value if hasattr(value, "value") else value
    def save_image(self, image_url):
        """Save image URL to idea (if applicable)"""
        self.image_url = image_url
        db.session.commit()
    def to_dict(self, include_comments=False, include_team=True):
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'projectDetails': self.project_details,
            'industry': self.industry,
            'stage': self.stage,
            'privacy': self._enum_to_value(self.privacy),
            'tags': self.tags or [],
            'creator': {
                'id': self.creator_id,
                'firstName': self.creator_first_name,
                'lastName': self.creator_last_name
            },
            'status': self.status.value,
            'likes': self.likes,
            'views': self.views,
            'commentsCount': self.get_comments_count(),
            'teamSize': self.get_team_size(),
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat(),
            'imageUrl': self.image_url
        }
        
        if include_team:
            data['teamMembers'] = [{'name': tm.name, 'position': tm.position, 'skills': tm.skills} 
                                   for tm in self.team_members.all()]
        
        if include_comments:
            data['comments'] = [comment.to_dict() for comment in self.idea_comments.order_by(IdeaComment.created_at.desc()).all()]
        
        return data