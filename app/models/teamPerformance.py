from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from sqlalchemy import Enum
from app.extensions import db

class TeamPerformance(db.Model):
    __tablename__ = 'team_performance'
    
    id = db.Column(db.Integer, primary_key=True)
    startup_id = db.Column(db.Integer, db.ForeignKey('startups.id'), nullable=False)
    
    score_percentage = db.Column(db.Float, default=0)  # 92%
    active_members = db.Column(db.Integer, default=0)  # 12
    tasks_completed = db.Column(db.Integer, default=0)  # 45
    productivity_level = db.Column(Enum('low', 'medium', 'high'), default='medium')
    
    period_start = db.Column(db.DateTime, nullable=False)
    period_end = db.Column(db.DateTime, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parent_startup = db.relationship('Startup', back_populates='team_performance_records')
    
    # HELPER FUNCTIONS
    
    def update_score(self, new_score):
        """Update performance score and adjust productivity level"""
        self.score_percentage = new_score
        
        if new_score >= 80:
            self.productivity_level = 'high'
        elif new_score >= 60:
            self.productivity_level = 'medium'
        else:
            self.productivity_level = 'low'
        
        db.session.commit()
    
    def increment_tasks_completed(self, count=1):
        """Increment completed tasks count"""
        self.tasks_completed += count
        db.session.commit()
    
    def update_active_members(self, active_count):
        """Update active members count"""
        self.active_members = active_count
        db.session.commit()
    
    def is_current_period(self):
        """Check if this performance record is for the current period"""
        now = datetime.utcnow()
        return self.period_start <= now <= self.period_end
    def _enum_to_value(self,value):
        return value.value if hasattr(value, "value") else value
        
    def to_dict(self):
        return {
            'id': self.id,
            'startup_id': self.startup_id,
            'score_percentage': self.score_percentage,
            'active_members': self.active_members,
            'tasks_completed': self.tasks_completed,
            'productivity_level':self._enum_to_value( self.productivity_level),
            'period_start': self.period_start.isoformat(),
            'period_end': self.period_end.isoformat(),
            'is_current_period': self.is_current_period(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }