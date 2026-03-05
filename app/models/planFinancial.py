from datetime import datetime
from sqlalchemy import JSON
from app.extensions import db

class PlanFinancial(db.Model):
    __tablename__ = 'plan_financials'

    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('business_plans.id'), nullable=False)
    
    scenario = db.Column(
        db.String(20),
        default="base"   # base | best | worst
    )
    revenue_inputs = db.Column(JSON, default={})
    expense_inputs = db.Column(JSON, default={})
    assumptions = db.Column(JSON, default={})

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    plan = db.relationship('BusinessPlan', back_populates='financials')

    def to_dict(self):
        return {
            'id': self.id,
            'plan_id': self.plan_id,
            'revenue_inputs': self.revenue_inputs,
            'expense_inputs': self.expense_inputs,
            'assumptions': self.assumptions,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
