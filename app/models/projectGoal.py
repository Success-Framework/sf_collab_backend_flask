from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from sqlalchemy import Enum
from app.extensions import db
from .goalMilstone import GoalMilestone


class ProjectGoal(db.Model):
    __tablename__ = 'project_goals'
    
    id = db.Column(db.Integer, primary_key=True)
    startup_id = db.Column(db.Integer, db.ForeignKey('startups.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    progress_percentage = db.Column(db.Float, default=0)  # 78%
    milestones_completed = db.Column(db.Integer, default=0)  # 8
    milestones_total = db.Column(db.Integer, default=0)  # 10
    
    is_on_track = db.Column(db.Boolean, default=True)
    next_milestone = db.Column(db.String(255))  # "MVP Launch"
    
    target_date = db.Column(db.DateTime)
    completed_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(Enum('active', 'completed', 'on_hold', 'cancelled'), default='active')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    goal_owner = db.relationship('User', back_populates='project_goals', foreign_keys=[user_id])
    parent_startup = db.relationship('Startup', back_populates='project_goals', foreign_keys=[startup_id])
    milestones = db.relationship('GoalMilestone', back_populates='project_goal', lazy='dynamic', cascade='all, delete-orphan')
    
    # HELPER FUNCTIONS
    
    def update_progress(self, completed_milestones=None, total_milestones=None):
        """Update progress percentage based on milestones"""
        if completed_milestones is not None:
            self.milestones_completed = completed_milestones
        if total_milestones is not None:
            self.milestones_total = total_milestones
        
        if self.milestones_total > 0:
            self.progress_percentage = (self.milestones_completed / self.milestones_total) * 100
        else:
            self.progress_percentage = 0
            
        # Update track status
        self.is_on_track = self._check_if_on_track()
        
        # Auto-complete if 100%
        if self.progress_percentage >= 100 and self.status != 'completed':
            self.complete_goal()
        
        db.session.commit()
    
    def _check_if_on_track(self):
        """Check if goal is on track based on target date"""
        if not self.target_date or self.status != 'active':
            return True
            
        today = datetime.utcnow()
        days_passed = (today - self.created_at).days
        total_days = (self.target_date - self.created_at).days
        
        if total_days <= 0:
            return self.progress_percentage >= 100
            
        expected_progress = (days_passed / total_days) * 100
        return self.progress_percentage >= expected_progress
    
    def complete_goal(self):
        """Mark goal as completed"""
        self.status = 'completed'
        self.progress_percentage = 100
        self.milestones_completed = self.milestones_total
        self.completed_date = datetime.utcnow()
        self.is_on_track = True
    
    def add_milestone(self, title, description="", order=None):
        """Add a milestone to the goal"""
        
        
        if order is None:
            order = self.milestones_list.count() + 1
        
        milestone = GoalMilestone(
            goal_id=self.id,
            user_id=self.user_id,
            title=title,
            description=description,
            order=order
        )
        
        db.session.add(milestone)
        self.milestones_total += 1
        self.update_progress()
        
        return milestone
    
    def complete_milestone(self):
        """Complete a milestone and update progress"""
        if self.milestones_completed < self.milestones_total:
            self.milestones_completed += 1
            self.update_progress()
    
    def change_status(self, new_status):
        """Change goal status"""
        valid_statuses = ['active', 'completed', 'on_hold', 'cancelled']
        if new_status in valid_statuses:
            self.status = new_status
            if new_status == 'completed':
                self.complete_goal()
            
            db.session.commit()
    
    def get_milestones(self, completed_only=False):
        """Get milestones with optional filtering"""
        query = self.milestones_list
        if completed_only:
            query = query.filter_by(is_completed=True)
        return query.order_by(GoalMilestone.order).all()
    
    def to_dict(self, include_milestones=False):
        data = {
            'id': self.id,
            'startup_id': self.startup_id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'progress_percentage': self.progress_percentage,
            'milestones_completed': self.milestones_completed,
            'milestones_total': self.milestones_total,
            'is_on_track': self.is_on_track,
            'next_milestone': self.next_milestone,
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'days_remaining': self._get_days_remaining()
        }
        
        if include_milestones:
            data['milestones'] = [milestone.to_dict() for milestone in self.get_milestones()]
        
        return data
    
    def _get_days_remaining(self):
        """Calculate days remaining until target date"""
        if not self.target_date or self.status == 'completed':
            return 0
        
        today = datetime.utcnow()
        remaining = (self.target_date - today).days
        return max(0, remaining)