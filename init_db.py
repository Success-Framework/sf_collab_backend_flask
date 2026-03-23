from app import create_app
from app.extensions import db
import os
from app.models.Enums import UserStatus

app = create_app("development")
basedir = os.path.abspath(os.path.dirname(__file__))

# Using relative path because simple URIs seem to work better with monkey patching
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/sf_collab_dev.db'
print(f"Using DB URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

with app.app_context():
    print("Initializing database...")
    db.create_all()
    print("Database initialized successfully.")

    # Create a test user if none exists
    from app.models.user import User
    test_user = User.query.filter_by(email="test@example.com").first()
    if not test_user:
        print("Creating test user...")
        from werkzeug.security import generate_password_hash
        user = User(
            email="test@example.com",
            password=generate_password_hash("password123"),
            first_name="Test",
            last_name="User",
            status=UserStatus.active
        )
        db.session.add(user)
        db.session.commit()
        print("Test user created.")
    else:
        print("Test user already exists.")
