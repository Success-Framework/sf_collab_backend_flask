from datetime import datetime
from app.extensions import db

class OutreachSendJob(db.Model):
    __tablename__ = "outreach_send_jobs"

    id = db.Column(db.Integer, primary_key=True)

    campaign_id = db.Column(db.Integer, nullable=False)
    contact_id = db.Column(db.Integer, nullable=False)
    draft_id = db.Column(db.Integer, nullable=False)
    email_account_id = db.Column(db.Integer, nullable=False)

    status = db.Column(
        db.String(50),
        default="queued"
    )  # queued | sending | sent | failed

    attempts = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text)
    sent_at = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
