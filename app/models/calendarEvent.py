from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from sqlalchemy import Enum
from app.extensions import db

class CalendarEvent(db.Model):
    __tablename__ = 'calendar_events'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    startup_id = db.Column(db.Integer, db.ForeignKey('startups.id'), nullable=True)
    
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)
    all_day = db.Column(db.Boolean, default=False)
    
    category = db.Column(Enum('meeting', 'deadline', 'reminder', 'event'), default='event')
    color = db.Column(db.String(20))  # hex color for calendar display
    
    location = db.Column(db.String(255))
    link = db.Column(db.String(255))  # URL link for virtual meetings
    is_recurring = db.Column(db.Boolean, default=False)
    recurrence_rule = db.Column(db.String(255))  # RRULE format
    
    reminder_minutes = db.Column(db.Integer, default=30)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    event_owner = db.relationship('User', back_populates='calendar_events', foreign_keys=[user_id])
    parent_startup = db.relationship('Startup', back_populates='calendar_events', foreign_keys=[startup_id])
    
    # HELPER FUNCTIONS
    
    def update_dates(self, start_date, end_date=None, all_day=False):
        """Update event dates"""
        self.start_date = start_date
        self.end_date = end_date
        self.all_day = all_day
        db.session.commit()
    
    def get_duration(self):
        """Get event duration in minutes"""
        if not self.end_date:
            return 0
        duration = self.end_date - self.start_date
        return duration.total_seconds() / 60
    
    def is_past(self):
        """Check if event is in the past"""
        now = datetime.utcnow()
        return self.end_date and self.end_date < now if self.end_date else self.start_date < now
    
    def is_ongoing(self):
        """Check if event is currently ongoing"""
        now = datetime.utcnow()
        if self.end_date:
            return self.start_date <= now <= self.end_date
        return self.start_date.date() == now.date() if self.all_day else False
    
    def get_reminder_time(self):
        """Get reminder time"""
        return self.start_date - timedelta(minutes=self.reminder_minutes)
    
    def should_remind(self):
        """Check if reminder should be sent"""
        if self.reminder_minutes <= 0:
            return False
        
        reminder_time = self.get_reminder_time()
        now = datetime.utcnow()
        return reminder_time <= now <= self.start_date
    
    def get_category_color(self):
        """Get color based on category"""
        colors = {
            'meeting': '#3B82F6',    # blue
            'deadline': '#EF4444',    # red
            'reminder': '#F59E0B',    # amber
            'event': '#8B5CF6'        # violet
        }
        return self.color or colors.get(self.category, '#6B7280')
    
    def _enum_to_value(self,value):
        return value.value if hasattr(value, "value") else value
        
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'startup_id': self.startup_id,
            'title': self.title,
            'description': self.description,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'all_day': self.all_day,
            'category': self._enum_to_value(self.category),
            'color': self.get_category_color(),
            'location': self.location,
            'is_recurring': self.is_recurring,
            'recurrence_rule': self.recurrence_rule,
            'reminder_minutes': self.reminder_minutes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'duration_minutes': self.get_duration(),
            'is_past': self.is_past(),
            'is_ongoing': self.is_ongoing(),
            'reminder_time': self.get_reminder_time().isoformat() if self.reminder_minutes > 0 else None,
            'should_remind': self.should_remind(),
            'link': self.link,
            'user': {
                'id': self.event_owner.id,
                'firstName': self.event_owner.first_name,
                'lastName': self.event_owner.last_name
            } if self.event_owner else None,
            'startup': {
                'id': self.parent_startup.id,
                'name': self.parent_startup.name
            } if self.parent_startup else None
        }