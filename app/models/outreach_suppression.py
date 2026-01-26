from datetime import datetime
from app.extensions import db

class SuppressionList(db.Model):
    __tablename__ = "outreach_suppression"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    reason = db.Column(db.String(50))  # unsubscribe | bounce | manual
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
