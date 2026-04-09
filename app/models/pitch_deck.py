from datetime import datetime
from app.extensions import db


class PitchDeck(db.Model):
    __tablename__ = "pitch_decks"

    id = db.Column(db.Integer, primary_key=True)

    # Creator
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", backref=db.backref("pitch_decks", lazy=True))

    # Deck metadata
    company_name = db.Column(db.String(255), nullable=False)
    tagline = db.Column(db.String(500), nullable=True)
    template = db.Column(db.String(50), nullable=False, default="general")  # general | saas | fintech | consumer
    sector = db.Column(db.String(100), nullable=True)

    # Raw form input stored as JSON (for regeneration / editing later)
    form_data = db.Column(db.JSON, nullable=True)

    # AI-generated slide content stored as JSON
    generated_content = db.Column(db.JSON, nullable=True)

    # File reference
    file_path = db.Column(db.String(500), nullable=True)   # absolute path on server
    file_name = db.Column(db.String(255), nullable=True)   # e.g. "acme_pitch_deck.pptx"

    # Status
    status = db.Column(db.String(50), default="pending")   # pending | generated | failed

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "company_name": self.company_name,
            "tagline": self.tagline,
            "template": self.template,
            "sector": self.sector,
            "form_data": self.form_data,
            "generated_content": self.generated_content,
            "file_name": self.file_name,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def to_list_dict(self):
        """Lightweight version for listing decks — no full content"""
        return {
            "id": self.id,
            "company_name": self.company_name,
            "tagline": self.tagline,
            "template": self.template,
            "sector": self.sector,
            "file_name": self.file_name,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }