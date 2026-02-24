from datetime import datetime
from app.extensions import db

class OutreachContact(db.Model):
    __tablename__ = "outreach_contacts"

    id = db.Column(db.Integer, primary_key=True)

    campaign_id = db.Column(
        db.Integer,
        db.ForeignKey("outreach_campaigns.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    company_name = db.Column(db.String(255))
    email = db.Column(db.String(255), nullable=False)

    source = db.Column(db.String(50))  # csv | website
    status = db.Column(
        db.String(50),
        default="unverified"
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("campaign_id", "email", name="uq_outreach_campaign_email"),
    )
