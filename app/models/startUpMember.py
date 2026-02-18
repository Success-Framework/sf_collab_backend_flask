from datetime import datetime
from app.extensions import db
from app.models.Enums import UserRoles
from sqlalchemy import Enum

class StartupMember(db.Model):
    __tablename__ = 'startup_members'
    
    id = db.Column(db.Integer, primary_key=True)
    startup_id = db.Column(db.Integer, db.ForeignKey('startups.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    admin = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(100), default=UserRoles.member)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    member_user = db.relationship('User', back_populates='startup_memberships')
    member_startup = db.relationship('Startup', back_populates='startup_members')
    
    # HELPER FUNCTIONS
    
    def update_role(self, new_role):
        """Update member role"""
        self.role = new_role
        db.session.commit()
    
    def deactivate(self):
        """Deactivate membership"""
        self.is_active = False
        self.startup.update_member_count()
    
    def activate(self):
        """Activate membership"""
        self.is_active = True
        self.startup.update_member_count()
    
    def get_full_name(self):
        """Get member's full name"""
        return f"{self.first_name} {self.last_name}"
    
    def _enum_to_value(self, value):
        return value.value if hasattr(value, "value") else value
        
    def to_dict(self):
        return {
            'id': self.id,
            'startupId': self.startup_id,
            'userId': self.user_id,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'role': self._enum_to_value(self.role),
            'joinedAt': self.joined_at.isoformat(),
            'isActive': self.is_active,
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat(),
            'fullName': self.get_full_name(),
            'profilePicture': self.member_user.profile_picture if self.member_user else None,
            'admin': self.admin
        }