from app import create_app
from app.extensions import db
from app.models.waitlist import Waitlist
from app.models.user import User
import os

app = create_app("development")
basedir = os.path.abspath(os.path.dirname(__file__))
# Ensure we point to the correct DB if not set via env
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/sf_collab_dev.db'

with app.app_context():
    print("Bypassing waitlist...")
    email = "test@example.com"
    user = User.query.filter_by(email=email).first()
    
    # Add to waitlist table
    existing_waitlist = Waitlist.query.filter_by(email=email).first()
    if not existing_waitlist:
        new_entry = Waitlist(
            email=email,
            name="Test User",
            referral_points=100,
            contribution_points=500,
            activity_points=200
        )
        db.session.add(new_entry)
        db.session.commit()
        print(f"Added {email} to waitlist.")
    else:
        print(f"{email} already on waitlist.")
        
    print("Waitlist bypass complete.")
