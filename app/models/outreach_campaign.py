from datetime import datetime
from app.extensions import db

class OutreachCampaign(db.Model):
    __tablename__ = "outreach_campaigns"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    email_account_id = db.Column(
        db.Integer,
        db.ForeignKey("outreach_email_accounts.id"),
        nullable=False
    )

    name = db.Column(db.String(255), nullable=False)
    target_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)

    industry = db.Column(db.String(100))
    location = db.Column(db.String(100))

    status = db.Column(
        db.String(50),
        default="draft"
    )  # draft | sending | completed

    max_emails = db.Column(db.Integer)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
