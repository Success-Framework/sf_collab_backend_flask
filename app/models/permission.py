from datetime import datetime
from app.extensions import db

class Permission(db.Model):
    __tablename__ = "permissions"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), default='General', index=True)  # Added category field
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user_permissions = db.relationship(
        "UserPermission",
        back_populates="permission",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )
    
    access_requests = db.relationship(
        "AccessRequest",
        back_populates="permission",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "key": self.key,
            "description": self.description,
            "category": self.category,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def get_active_user_permissions(self):
        """Get all active user permissions for this permission"""
        from app.models.userPermission import UserPermission
        now = datetime.utcnow()
        
        return UserPermission.query.filter(
            UserPermission.permission_id == self.id,
            (UserPermission.starts_at == None) | (UserPermission.starts_at <= now),
            (UserPermission.expires_at == None) | (UserPermission.expires_at > now)
        ).all()

    def get_user_count(self):
        """Get count of users with this permission"""
        return self.user_permissions.count()

    def get_pending_requests(self):
        """Get pending access requests for this permission"""
        return self.access_requests.filter_by(status="pending").all()

    def get_permissions_by_category(self, category):
        """Get all permissions in a specific category"""
        return Permission.query.filter_by(category=category).all()

    @classmethod
    def get_categories(cls):
        """Get list of distinct permission categories"""
        categories = db.session.query(cls.category).distinct().all()
        return [category[0] for category in categories]

    @classmethod
    def get_permissions_with_category(cls):
        """Get all permissions grouped by category"""
        permissions = cls.query.order_by(cls.category, cls.key).all()
        result = {}
        for permission in permissions:
            if permission.category not in result:
                result[permission.category] = []
            result[permission.category].append(permission.to_dict())
        return result