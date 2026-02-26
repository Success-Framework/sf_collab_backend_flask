from datetime import datetime
from sqlalchemy import Enum, UniqueConstraint
import enum
from app.extensions import db


class InvitationStatus(enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"
    expired = "expired"


class StartupInvitation(db.Model):
    __tablename__ = "startup_invitations"

    id = db.Column(db.Integer, primary_key=True)

    # Relationships
    startup_id = db.Column(
        db.Integer,
        db.ForeignKey("startups.id", ondelete="CASCADE"),
        nullable=False
    )

    invited_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    invited_by_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    # Role the user will have if accepted
    role = db.Column(db.String(100), nullable=False)

    # Status
    status = db.Column(
        Enum(InvitationStatus),
        default=InvitationStatus.pending,
        nullable=False
    )

    # Optional expiration
    expires_at = db.Column(db.DateTime, nullable=True)

    # Timestamps
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    responded_at = db.Column(db.DateTime, nullable=True)

    # Prevent duplicate active invitations
    __table_args__ = (
        UniqueConstraint(
            "startup_id",
            "invited_user_id",
            name="unique_startup_invitation"
        ),
    )

    # Relationships
    startup = db.relationship("Startup", backref="invitations")
    invited_user = db.relationship(
        "User",
        foreign_keys=[invited_user_id],
        backref="startup_invitations_received"
    )
    invited_by = db.relationship(
        "User",
        foreign_keys=[invited_by_id],
        backref="startup_invitations_sent"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "startup_id": self.startup_id,
            "startup_name": self.startup.name if self.startup else None,
            "invited_user_id": self.invited_user_id,
            "invited_by_id": self.invited_by_id,
            "role": self.role,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }