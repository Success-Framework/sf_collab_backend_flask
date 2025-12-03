from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from sqlalchemy import Enum
from app.extensions import db

class GrowthMetric(db.Model):
    __tablename__ = 'growth_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    startup_id = db.Column(db.Integer, db.ForeignKey('startups.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    metric_type = db.Column(Enum('user_growth', 'revenue', 'market_share', 'overall'), nullable=False)
    
    current_value = db.Column(db.Float, default=0)
    previous_value = db.Column(db.Float, default=0)
    growth_percentage = db.Column(db.Float, default=0)  # 156%
    
    user_growth_percentage = db.Column(db.Float, default=0)  # +45%
    revenue_amount = db.Column(db.Float, default=0)  # $45k
    market_share_percentage = db.Column(db.Float, default=0)  # 12%
    
    period_start = db.Column(db.DateTime, nullable=False)
    period_end = db.Column(db.DateTime, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    # Change these relationships to use string references:
    parent_startup = db.relationship('Startup', back_populates='growth_metrics_startup', foreign_keys=[startup_id])
    metric_owner = db.relationship('User', back_populates='growth_metrics', foreign_keys=[user_id])
    
    # HELPER FUNCTIONS
    
    def calculate_growth_percentage(self):
        """Calculate growth percentage based on current and previous values"""
        if self.previous_value == 0:
            return 0
        return ((self.current_value - self.previous_value) / self.previous_value) * 100
    
    def update_values(self, current_value, previous_value=None):
        """Update metric values and recalculate growth"""
        self.current_value = current_value
        
        if previous_value is not None:
            self.previous_value = previous_value
        
        self.growth_percentage = self.calculate_growth_percentage()
        
        # Update specific metric type values
        if self.metric_type == 'user_growth':
            self.user_growth_percentage = self.growth_percentage
        elif self.metric_type == 'revenue':
            self.revenue_amount = current_value
        elif self.metric_type == 'market_share':
            self.market_share_percentage = current_value
        
        db.session.commit()
    
    def is_current_period(self):
        """Check if this metric is for the current period"""
        now = datetime.utcnow()
        return self.period_start <= now <= self.period_end
    
    def get_period_duration(self):
        """Get the duration of the period in days"""
        return (self.period_end - self.period_start).days
    
    def get_trend_direction(self):
        """Get trend direction (positive/negative/neutral)"""
        if self.growth_percentage > 0:
            return 'positive'
        elif self.growth_percentage < 0:
            return 'negative'
        else:
            return 'neutral'
    
    def format_value(self):
        """Format value based on metric type"""
        if self.metric_type == 'revenue':
            return f"${self.current_value:,.0f}"
        elif self.metric_type in ['market_share', 'user_growth']:
            return f"{self.current_value:.1f}%"
        else:
            return f"{self.current_value:,.0f}"
    
    def _enum_to_value(self,value):
        return value.value if hasattr(value, "value") else value
        
    def to_dict(self):
        return {
            'id': self.id,
            'startup_id': self.startup_id,
            'user_id': self.user_id,
            'metric_type': self._enum_to_value(self.metric_type),
            'current_value': self.current_value,
            'previous_value': self.previous_value,
            'growth_percentage': self.growth_percentage,
            'user_growth_percentage': self.user_growth_percentage,
            'revenue_amount': self.revenue_amount,
            'market_share_percentage': self.market_share_percentage,
            'period_start': self.period_start.isoformat(),
            'period_end': self.period_end.isoformat(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_current_period': self.is_current_period(),
            'period_duration': self.get_period_duration(),
            'trend_direction': self.get_trend_direction(),
            'formatted_value': self.format_value(),
            'startup': {
                'id': self.startup.id,
                'name': self.startup.name
            } if self.startup else None,
            'user': {
                'id': self.user.id,
                'firstName': self.user.first_name,
                'lastName': self.user.last_name
            } if self.user else None
        }