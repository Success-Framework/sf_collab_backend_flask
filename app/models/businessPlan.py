from datetime import datetime
from app.extensions import db

class BusinessPlan(db.Model):
    __tablename__ = 'business_plans'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    title = db.Column(db.String(255), nullable=False)
    industry = db.Column(db.String(100), nullable=True)
    stage = db.Column(db.String(50), nullable=True)  # idea, mvp, growth, etc.

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    sections = db.relationship(
        'PlanSection',
        back_populates='plan',
        cascade='all, delete-orphan'
    )

    financials = db.relationship(
        'PlanFinancial',
        uselist=False,
        back_populates='plan',
        cascade='all, delete-orphan'
    )

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'industry': self.industry,
            'stage': self.stage,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
