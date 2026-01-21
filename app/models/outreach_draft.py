from datetime import datetime
from app.extensions import db

class OutreachDraft(db.Model):
    __tablename__ = "outreach_drafts"

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(
        db.Integer, db.ForeignKey("outreach_campaigns.id"), nullable=False
    )

    subject = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)

    status = db.Column(
        db.String(50), default="generated"
    )  # generated | edited | approved

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
