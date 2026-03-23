import uuid
from datetime import datetime
from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import JSON


class PitchDeck(db.Model):
    __tablename__ = "pitch_decks"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    startup_id = db.Column(db.Integer, db.ForeignKey("startups.id"), nullable=True)

    title = db.Column(db.String(255), nullable=False)
    template_type = db.Column(db.String(100), nullable=False)
    theme_type = db.Column(db.String(100), nullable=False)

    slides_json = db.Column(db.JSON, nullable=False)

    credits_used = db.Column(db.Integer, default=20)

    status = db.Column(db.String(50), default="draft")  # draft | exported

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Optional relationships
    user = db.relationship("User", backref=db.backref("pitch_decks", lazy=True))
    startup = db.relationship("Startup", backref=db.backref("pitch_decks", lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "startup_id": self.startup_id,
            "title": self.title,
            "template_type": self.template_type,
            "theme_type": self.theme_type,
            "slides_json": self.slides_json,
            "credits_used": self.credits_used,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
