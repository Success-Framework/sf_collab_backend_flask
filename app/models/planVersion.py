from datetime import datetime
from app.extensions import db


class PlanVersion(db.Model):
    __tablename__ = "plan_versions"

    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey("business_plans.id"), nullable=False)

    version_number = db.Column(db.Integer, nullable=False)
    trigger_type = db.Column(db.String(50))
    summary = db.Column(db.Text)

    health_score = db.Column(db.Integer)
    health_status = db.Column(db.String(30))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "version": self.version_number,
            "trigger": self.trigger_type,
            "summary": self.summary,
            "health_score": self.health_score,
            "health_status": self.health_status,
            "created_at": self.created_at.isoformat()
        }
