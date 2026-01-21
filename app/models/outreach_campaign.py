from datetime import datetime
from app.extensions import db

class OutreachCampaign(db.Model):
    __tablename__ = "outreach_campaigns"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    email_account_id = db.Column(
        db.Integer, db.ForeignKey("email_accounts.id"), nullable=False
    )

    name = db.Column(db.String(255), nullable=False)
    target_type = db.Column(db.String(50), nullable=False)  # clients | investors | etc
    description = db.Column(db.Text, nullable=False)

    industry = db.Column(db.String(100))
    location = db.Column(db.String(100))

    status = db.Column(
        db.String(50), default="draft"
    )  # draft | ready | sending | completed

    max_emails = db.Column(db.Integer)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "targetType": self.target_type,
            "description": self.description,
            "industry": self.industry,
            "location": self.location,
            "status": self.status,
            "maxEmails": self.max_emails,
            "createdAt": self.created_at.isoformat(),
        }
