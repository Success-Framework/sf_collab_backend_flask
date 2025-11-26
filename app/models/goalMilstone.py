from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from sqlalchemy import Enum
from app.extensions import db

class GoalMilestone(db.Model):
    __tablename__ = 'goal_milestones'
    
    id = db.Column(db.Integer, primary_key=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('project_goals.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)
    
    is_completed = db.Column(db.Boolean, default=False)
    completed_date = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project_goal = db.relationship('ProjectGoal', back_populates='milestones', foreign_keys=[goal_id])
    milestone_owner = db.relationship('User', back_populates='goal_milestones', foreign_keys=[user_id])
    
    # HELPER FUNCTIONS
    
    def complete(self):
        """Mark milestone as completed"""
        self.is_completed = True
        self.completed_date = datetime.utcnow()
        
        # Update parent goal progress
        if self.goal:
            self.goal.complete_milestone()
        
        db.session.commit()
    
    def uncomplete(self):
        """Mark milestone as not completed"""
        self.is_completed = False
        self.completed_date = None
        
        # Update parent goal progress
        if self.goal:
            self.goal.milestones_completed = max(0, self.goal.milestones_completed - 1)
            self.goal.update_progress()
        
        db.session.commit()
    
    def update_order(self, new_order):
        """Update milestone order"""
        self.order = new_order
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'goal_id': self.goal_id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'order': self.order,
            'is_completed': self.is_completed,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'goal_title': self.goal.title if self.goal else None
        }