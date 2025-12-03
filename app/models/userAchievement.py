from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
# from sqlalchemy import Enum
from app.extensions import db

class UserAchievement(db.Model):
    __tablename__ = 'user_achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), nullable=False)
    
    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow)
    progress_percentage = db.Column(db.Integer, default=0)
    is_completed = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    achievement_owner = db.relationship('User', back_populates='user_achievements', foreign_keys=[user_id])
    achievement = db.relationship('Achievement', back_populates='user_achievements', foreign_keys=[achievement_id])
    
    # HELPER FUNCTIONS
    
    def update_progress(self, progress):
        """Update progress and check if achievement is unlocked"""
        self.progress_percentage = max(0, min(100, progress))
        
        if self.progress_percentage >= 100 and not self.is_completed:
            self.unlock()
        
        db.session.commit()
    
    def unlock(self):
        """Unlock achievement and award points"""
        self.is_completed = True
        self.unlocked_at = datetime.utcnow()
        self.progress_percentage = 100
        
        # Award XP points to user
        if self.user and self.achievement:
            self.user.add_xp_points(self.achievement.points)
        
        db.session.commit()
    
    def increment_progress(self, increment=10):
        """Increment progress by specified amount"""
        new_progress = self.progress_percentage + increment
        self.update_progress(new_progress)
    
    def get_time_since_unlock(self):
        """Get time since achievement was unlocked"""
        if self.is_completed and self.unlocked_at:
            return datetime.utcnow() - self.unlocked_at
        return None
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'achievement_id': self.achievement_id,
            'unlocked_at': self.unlocked_at.isoformat() if self.unlocked_at else None,
            'progress_percentage': self.progress_percentage,
            'is_completed': self.is_completed,
            'created_at': self.created_at.isoformat(),
            'achievement': self.achievement.to_dict() if self.achievement else None,
            'time_since_unlock': str(self.get_time_since_unlock()) if self.get_time_since_unlock() else None
        }