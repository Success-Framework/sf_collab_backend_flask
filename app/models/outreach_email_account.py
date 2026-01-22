from datetime import datetime
from app.extensions import db

class OutreachEmailAccount(db.Model):
    __tablename__ = "outreach_email_accounts"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    email_address = db.Column(db.String(255), nullable=False)
    from_name = db.Column(db.String(255), nullable=False)

    smtp_host = db.Column(db.String(255), nullable=False)
    smtp_port = db.Column(db.Integer, nullable=False)
    smtp_username = db.Column(db.String(255), nullable=False)
    smtp_password_encrypted = db.Column(db.Text, nullable=False)

    use_tls = db.Column(db.Boolean, default=True)

    daily_limit = db.Column(db.Integer, default=200)
    hourly_limit = db.Column(db.Integer, default=40)

    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "emailAddress": self.email_address,
            "fromName": self.from_name,
            "smtpHost": self.smtp_host,
            "smtpPort": self.smtp_port,
            "useTls": self.use_tls,
            "dailyLimit": self.daily_limit,
            "hourlyLimit": self.hourly_limit,
            "isActive": self.is_active,
        }
