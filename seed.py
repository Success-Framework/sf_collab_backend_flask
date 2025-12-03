# seed_calendar_events.py
from datetime import datetime, timedelta
import random
from app import create_app
from app.models import db, CalendarEvent, User, Startup

def seed_calendar_events():
    app = create_app()
    with app.app_context():
        # Get some users and startups
        users = User.query.limit(5).all()
        startups = Startup.query.limit(3).all()
        
        if not users or not startups:
            print("Need users and startups first!")
            return
        
        # Event categories
        categories = ['meeting', 'deadline', 'reminder', 'event']
        
        # Generate events for each user
        for user in users:
            for i in range(10):  # 10 events per user
                # Random date within next 30 days
                start_date = datetime.utcnow() + timedelta(days=random.randint(0, 30))
                duration_hours = random.choice([1, 2, 4, 8])
                end_date = start_date + timedelta(hours=duration_hours)
                
                event = CalendarEvent(
                    user_id=user.id,
                    startup_id=random.choice(startups).id if random.random() > 0.3 else None,
                    title=f"Event {i+1} for {user.first_name}",
                    description=f"This is a sample event description for {user.first_name}",
                    start_date=start_date,
                    end_date=end_date,
                    all_day=random.random() > 0.8,
                    category=random.choice(categories),
                    color=None,  # Will use category-based colors
                    location=f"Location {i+1}" if random.random() > 0.5 else None,
                    reminder_minutes=random.choice([0, 5, 15, 30, 60]),
                    is_recurring=random.random() > 0.9,
                    recurrence_rule="FREQ=WEEKLY;INTERVAL=1" if random.random() > 0.9 else None
                )
                
                db.session.add(event)
        
        db.session.commit()
        print(f"Created {len(users) * 10} calendar events!")

if __name__ == '__main__':
    seed_calendar_events()