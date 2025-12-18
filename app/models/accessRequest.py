from datetime import datetime
from app.extensions import db

class AccessRequest(db.Model):
    __tablename__ = "access_requests"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    permission_id = db.Column(db.Integer, db.ForeignKey("permissions.id"), nullable=False)
    reason = db.Column(db.Text)
    status = db.Column(db.String(20), default="pending", index=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    reviewed_by = db.Column(db.Integer, nullable=True)
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    permission = db.relationship(
        "Permission",
        back_populates="access_requests",
        lazy="joined"
    )

    def to_dict(self, include_user_info=False):
        """Convert access request to dictionary"""
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "permission": self.permission.to_dict() if self.permission else None,
            "reason": self.reason,
            "status": self.status,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "reviewed_by": self.reviewed_by,
            "requested_at": self.requested_at.isoformat(),
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
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

    def approve(self, reviewer_id, expires_at=None):
        """Approve the access request"""
        from app.models.userPermission import UserPermission
        
        self.status = "approved"
        self.reviewed_by = reviewer_id
        self.reviewed_at = datetime.utcnow()
        self.expires_at = expires_at
        self.updated_at = datetime.utcnow()
        
        # Create user permission
        user_permission = UserPermission(
            user_id=self.user_id,
            permission_id=self.permission_id,
            granted_by=reviewer_id,
            starts_at=datetime.utcnow(),
            expires_at=expires_at
        )
        
        db.session.add(user_permission)
        db.session.commit()
        
        # Log the activity
        from app.models.activity import Activity
        Activity.log(
            action="access_request_approved",
            user_id=reviewer_id,
            details=f"Approved access request {self.id} for permission {self.permission.key}"
        )
        
        return user_permission

    def reject(self, reviewer_id, reason=None):
        """Reject the access request"""
        self.status = "rejected"
        self.reviewed_by = reviewer_id
        self.reviewed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        if reason:
            self.reason = f"{self.reason}\n\nRejection reason: {reason}"
        
        db.session.commit()
        
        # Log the activity
        from app.models.activity import Activity
        Activity.log(
            action="access_request_rejected",
            user_id=reviewer_id,
            details=f"Rejected access request {self.id} for permission {self.permission.key}"
        )

    def is_expired(self):
        """Check if the requested access would be expired"""
        if not self.expires_at:
            return False
        
        return datetime.utcnow() > self.expires_at