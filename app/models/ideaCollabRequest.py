from datetime import datetime
from app.extensions import db
from sqlalchemy import Enum
from .Enums import JoinRequestStatus


class IdeaCollabRequest(db.Model):
    __tablename__ = 'idea_collab_requests'

    id = db.Column(db.Integer, primary_key=True)
    idea_id = db.Column(db.Integer, db.ForeignKey('ideas.id', ondelete='CASCADE'), nullable=False)
    idea_title = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    message = db.Column(db.Text)
    role = db.Column(db.String(100), default='co-developer')
    status = db.Column(Enum(JoinRequestStatus), default=JoinRequestStatus.pending, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    idea = db.relationship('Idea', backref=db.backref('idea_collab_requests', lazy='dynamic'), foreign_keys=[idea_id])
    requester = db.relationship('User', backref=db.backref('idea_collab_requests', lazy='dynamic'), foreign_keys=[user_id])

    # ── Helpers ──────────────────────────────────────────────────────────

    def approve(self):
        self.status = JoinRequestStatus.approved
        self.updated_at = datetime.utcnow()

    def reject(self):
        self.status = JoinRequestStatus.rejected
        self.updated_at = datetime.utcnow()

    def cancel(self):
        self.status = JoinRequestStatus.cancelled
        self.updated_at = datetime.utcnow()

    def is_pending(self):
        return self.status == JoinRequestStatus.pending

    def _enum_to_value(self, value):
        return value.value if hasattr(value, 'value') else value

    def to_dict(self):
        return {
            'id': self.id,
            'idea_id': self.idea_id,
            'idea_title': self.idea_title,
            'user_id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'message': self.message,
            'role': self.role,
            'status': self._enum_to_value(self.status),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }