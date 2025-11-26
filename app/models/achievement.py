from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from sqlalchemy import Enum
from app.extensions import db

class Achievement(db.Model):
    __tablename__ = 'achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(100))  # icon name or emoji
    
    category = db.Column(Enum('task', 'social', 'learning', 'milestone'), default='task')
    points = db.Column(db.Integer, default=0)  # XP points
    
    requirement_type = db.Column(db.String(50))  # 'tasks_completed', 'ideas_created', etc.
    requirement_value = db.Column(db.Integer)  # threshold to unlock
    
    badge_color = db.Column(db.String(20))
    rarity = db.Column(Enum('common', 'rare', 'epic', 'legendary'), default='common')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user_achievements = db.relationship('UserAchievement', back_populates='achievement', lazy='dynamic', cascade='all, delete-orphan')
    
    # HELPER FUNCTIONS
    
    def get_unlocked_count(self):
        """Get count of users who unlocked this achievement"""
        return self.user_achievements.filter_by(is_completed=True).count()
    
    def get_progress_for_user(self, user_id):
        """Get progress of this achievement for a specific user"""
        user_achievement = self.user_achievements.filter_by(user_id=user_id).first()
        return user_achievement.progress_percentage if user_achievement else 0
    
    def is_unlocked_by_user(self, user_id):
        """Check if achievement is unlocked by user"""
        user_achievement = self.user_achievements.filter_by(user_id=user_id, is_completed=True).first()
        return user_achievement is not None
    
    def calculate_rarity_color(self):
        """Calculate badge color based on rarity"""
        colors = {
            'common': '#6B7280',
            'rare': '#3B82F6',
            'epic': '#8B5CF6',
            'legendary': '#F59E0B'
        }
        return colors.get(self.rarity, '#6B7280')
    
    def to_dict(self, user_id=None):
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'icon': self.icon,
            'category': self.category,
            'points': self.points,
            'requirement_type': self.requirement_type,
            'requirement_value': self.requirement_value,
            'badge_color': self.badge_color or self.calculate_rarity_color(),
            'rarity': self.rarity,
            'unlocked_count': self.get_unlocked_count(),
            'created_at': self.created_at.isoformat()
        }
        
        if user_id:
            data['user_progress'] = self.get_progress_for_user(user_id)
            data['is_unlocked'] = self.is_unlocked_by_user(user_id)
        
        return data