from datetime import datetime
from app.extensions import db

class PlanSection(db.Model):
    __tablename__ = 'plan_sections'

    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('business_plans.id'), nullable=False)

    section_type = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    plan = db.relationship('BusinessPlan', back_populates='sections')

    def to_dict(self):
        return {
            'id': self.id,
            'plan_id': self.plan_id,
            'section_type': self.section_type,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
