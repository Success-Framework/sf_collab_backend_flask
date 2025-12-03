from datetime import datetime
from app.extensions import db
from sqlalchemy import Enum
from .Enums import JoinRequestStatus

class JoinRequest(db.Model):
    __tablename__ = 'join_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    startup_id = db.Column(db.Integer, db.ForeignKey('startups.id', ondelete='CASCADE'), nullable=False)
    startup_name = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    message = db.Column(db.Text)
    role = db.Column(db.String(100), default='member')
    status = db.Column(Enum(JoinRequestStatus), default=JoinRequestStatus.pending)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    target_startup = db.relationship('Startup', back_populates='join_requests', foreign_keys=[startup_id])
    request_user = db.relationship('User', back_populates='join_requests', foreign_keys=[user_id])
    
    # HELPER FUNCTIONS
    
    def approve(self, reviewer_id=None):
        """Approve join request"""
        self.status = JoinRequestStatus.approved
        self.updated_at = datetime.utcnow()
        
        # Add user to startup members
        from models.startUpMember import StartupMember
        member = StartupMember(
            startup_id=self.startup_id,
            user_id=self.user_id,
            first_name=self.first_name,
            last_name=self.last_name,
            role=self.role
        )
        db.session.add(member)
        
        # Update startup member count
        if self.startup:
            self.startup.update_member_count()
        
        db.session.commit()
        return member
    
    def reject(self, reviewer_id=None):
        """Reject join request"""
        self.status = JoinRequestStatus.rejected
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def cancel(self):
        """Cancel join request (by user)"""
        self.status = JoinRequestStatus.cancelled
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def is_pending(self):
        """Check if request is pending"""
        return self.status == JoinRequestStatus.pending
    
    def get_duration(self):
        """Get time since request was created"""
        return datetime.utcnow() - self.created_at
    
    def _enum_to_value(self,value):
        return value.value if hasattr(value, "value") else value
        
    def to_dict(self):
        return {
            'id': self.id,
            'startupId': self.startup_id,
            'startupName': self.startup_name,
            'userId': self.user_id,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'message': self.message,
            'role': self.role,
            'status': self._enum_to_value(self.status.value),
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat(),
            'isPending': self.is_pending(),
            'duration': str(self.get_duration()),
            'startup': {
                'id': self.startup.id,
                'name': self.startup.name,
                'industry': self.startup.industry
            } if self.startup else None,
            'user': {
                'id': self.user.id,
                'firstName': self.user.first_name,
                'lastName': self.user.last_name,
                'email': self.user.email
            } if self.user else None
        }