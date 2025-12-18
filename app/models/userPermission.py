from datetime import datetime
from app.extensions import db

class UserPermission(db.Model):
    __tablename__ = "user_permissions"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    permission_id = db.Column(
        db.Integer,
        db.ForeignKey("permissions.id", ondelete="CASCADE"),
        nullable=False
    )

    starts_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    granted_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    permission_owner = db.relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="permissions"
    )

    permission = db.relationship(
        "Permission",
        back_populates="user_permissions"
    )


    def is_active(self):
        """Check if permission is currently active"""
        now = datetime.utcnow()
        
        # Check start time
        if self.starts_at and self.starts_at > now:
            return False
        
        # Check expiration
        if self.expires_at and self.expires_at <= now:
            return False
        
        return True

    def to_dict(self, include_user_info=False):
        """Convert user permission to dictionary"""
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "permission": self.permission.to_dict() if self.permission else None,
            "starts_at": self.starts_at.isoformat() if self.starts_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "granted_by": self.granted_by,
            "is_active": self.is_active(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        # Include user info if requested
        if include_user_info and self.user_id:
            from app.models.user import User
            user = User.query.get(self.user_id)
            if user:
                data['user'] = {
                    'id': user.id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email
                }
        
        return data

    def time_remaining(self):
        """Get time remaining until expiration in seconds"""
        if not self.expires_at:
            return None
        
        now = datetime.utcnow()
        if self.expires_at <= now:
            return 0
        
        return (self.expires_at - now).total_seconds()

    def revoke(self, revoked_by):
        """Revoke this user permission"""
        # You might want to implement soft delete instead
        db.session.delete(self)
        
        # Log the activity
        from app.models.activity import Activity
        Activity.log(
            action="permission_revoked",
            user_id=revoked_by,
            details=f"Revoked permission {self.permission.key} from user {self.user_id}"
        )
        
        db.session.commit()