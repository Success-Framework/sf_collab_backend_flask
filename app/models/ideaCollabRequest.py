from datetime import datetime
from app.extensions import db
from sqlalchemy import Enum
from .Enums import JoinRequestStatus  # Reuse existing enum


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
    status = db.Column(Enum(JoinRequestStatus), default=JoinRequestStatus.pending)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    target_idea = db.relationship('Idea', foreign_keys=[idea_id])
    request_user = db.relationship('User', foreign_keys=[user_id])

    def approve(self):
        """Approve request and add user as TeamMember on the idea"""
        self.status = JoinRequestStatus.approved
        self.updated_at = datetime.utcnow()

        from app.models.teamMember import TeamMember
        member = TeamMember(
            idea_id=self.idea_id,
            name=f"{self.first_name} {self.last_name}",
            position=self.role,
            skills={}
        )
        db.session.add(member)
        return member

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
        user = self.request_user
        idea = self.target_idea
        return {
            'id': self.id,
            'ideaId': self.idea_id,
            'ideaTitle': self.idea_title,
            'userId': self.user_id,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'message': self.message,
            'role': self.role,
            'status': self._enum_to_value(self.status),
            'isPending': self.is_pending(),
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat(),
            'user': {
                'id': user.id,
                'firstName': user.first_name,
                'lastName': user.last_name,
                'profilePicture': user.profile_picture
            } if user else None,
            'idea': {
                'id': idea.id,
                'title': idea.title
            } if idea else None
        }