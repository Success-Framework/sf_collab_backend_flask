from app import create_app
from app.extensions import db
from app.models.user import User
import os

app = create_app("development")
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/sf_collab_dev.db'

with app.app_context():
    print("Verifying test user...")
    user = User.query.filter_by(email="test@example.com").first()
    if user:
        user.is_email_verified = True
        # Also ensure roles are set correctly if needed
        # (The subagent said it added them via API, but let's be sure)
        db.session.commit()
        print(f"User {user.email} is now verified.")
    else:
        print("Error: Test user not found.")
